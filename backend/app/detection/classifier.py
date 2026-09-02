"""M2: Multi-Class Threat Probability Classifier.

Emits calibrated probabilities across six distinct threat classes:
1. Phishing (Credential harvesting & deceptive links)
2. BEC / Financial Fraud (Invoices, wire diversion, gift cards)
3. Malware Carrier (Hostile attachments & macros)
4. Impersonation (Leadership & VIP spoofing)
5. Spam / Bulk (Unsolicited mass marketing)
6. Benign (Legitimate verified communication)

Architecture:
- Primary Engine: Trained statistical ML model (TF-IDF + Calibrated Linear Classifier, model.joblib)
- Forensic Signal Layer: Extracted forensic signals (lookalikes, attachments, QR, concealment, URL mismatches)
- Fallback Engine: Heuristic logit accumulator + Softmax when ML artifact is missing or corrupted.
"""
import math
import os
from dataclasses import dataclass
from typing import Any
import joblib

CLASSES = ["phishing", "bec_fraud", "malware_carrier", "impersonation", "spam", "benign"]

_MODEL = None
_MODEL_LOADED = False


def get_trained_model():
    """Retrieve cached trained ML model pipeline from disk."""
    global _MODEL, _MODEL_LOADED
    if not _MODEL_LOADED:
        model_path = os.path.join(os.path.dirname(__file__), "model.joblib")
        if os.path.exists(model_path):
            try:
                _MODEL = joblib.load(model_path)
            except Exception as err:
                _MODEL = None
        else:
            _MODEL = None
        _MODEL_LOADED = True
    return _MODEL


def reset_model_cache():
    """Reset model cache for testing fallback behavior."""
    global _MODEL, _MODEL_LOADED
    _MODEL = None
    _MODEL_LOADED = False


@dataclass(frozen=True)
class ClassificationResult:
    predicted_class: str
    probabilities: dict[str, float]
    primary_threat_confidence: str
    top_contributing_signals: list[str]
    engine_type: str  # 'trained_ml' or 'heuristic_fallback'


def _heuristic_classify(
    *,
    social_engineering_findings: list[dict[str, Any]],
    bec_findings: list[dict[str, Any]],
    impersonation_findings: list[dict[str, Any]],
    lookalike_findings: list[dict[str, Any]],
    concealment_findings: list[dict[str, Any]],
    attachment_findings: list[dict[str, Any]],
    url_findings: list[dict[str, Any]],
    auth_status: str,
    has_qr_threat: bool,
) -> tuple[str, dict[str, float], str, list[str]]:
    """Heuristic fallback logit accumulator."""
    logits = {
        "phishing": 0.5,
        "bec_fraud": 0.5,
        "malware_carrier": 0.2,
        "impersonation": 0.2,
        "spam": 1.0,
        "benign": 2.5 if auth_status == "pass" else 1.0,
    }
    signals: list[str] = []

    if lookalike_findings:
        logits["phishing"] += 3.5 * len(lookalike_findings)
        logits["impersonation"] += 2.0 * len(lookalike_findings)
        logits["benign"] -= 2.0
        signals.append("Lookalike Domain Detected")

    if impersonation_findings:
        logits["impersonation"] += 4.5 * len(impersonation_findings)
        logits["bec_fraud"] += 2.0
        logits["benign"] -= 2.5
        signals.append("Executive/VIP Impersonation Flag")

    if bec_findings:
        logits["bec_fraud"] += 4.5 * len(bec_findings)
        logits["phishing"] += 1.0
        logits["benign"] -= 3.0
        signals.append(f"BEC Pattern: {bec_findings[0].get('title', 'Financial Diversion')}")

    suspicious_att = [a for a in attachment_findings if a.get("is_suspicious")]
    if suspicious_att:
        logits["malware_carrier"] += 5.0 * len(suspicious_att)
        logits["phishing"] += 1.5
        logits["benign"] -= 3.0
        signals.append("Dangerous / Disguised Attachment")

    if has_qr_threat:
        logits["phishing"] += 3.5
        logits["benign"] -= 2.0
        signals.append("Quishing / Decoded QR Destination")

    if concealment_findings:
        logits["phishing"] += 2.0
        logits["spam"] += 2.5
        signals.append("Adversarial Body Concealment")

    for se in social_engineering_findings:
        cat = se.get("category", "")
        if cat in {"financial_instruction", "urgency"}:
            logits["bec_fraud"] += 1.5
            logits["phishing"] += 1.5
        if cat in {"authority", "threat_of_consequence"}:
            logits["impersonation"] += 1.5
            logits["phishing"] += 1.5
        signals.append(f"Intent Pressure: {cat}")

    mismatched_urls = [u for u in url_findings if u.get("mismatch_flag")]
    if mismatched_urls:
        logits["phishing"] += 3.0
        signals.append("Deceptive URL Anchor Mismatch")

    max_logit = max(logits.values())
    exp_logits = {k: math.exp(v - max_logit) for k, v in logits.items()}
    sum_exp = sum(exp_logits.values())
    probabilities = {k: round(v / sum_exp, 4) for k, v in exp_logits.items()}

    predicted_class = max(probabilities, key=probabilities.get)
    pred_prob = probabilities[predicted_class]
    confidence = "High" if pred_prob >= 0.70 else "Medium" if pred_prob >= 0.45 else "Low"

    return predicted_class, probabilities, confidence, list(dict.fromkeys(signals))[:5]


def classify_message_intent(
    *,
    full_text: str = "",
    social_engineering_findings: list[dict[str, Any]] | None = None,
    bec_findings: list[dict[str, Any]] | None = None,
    impersonation_findings: list[dict[str, Any]] | None = None,
    lookalike_findings: list[dict[str, Any]] | None = None,
    concealment_findings: list[dict[str, Any]] | None = None,
    attachment_findings: list[dict[str, Any]] | None = None,
    url_findings: list[dict[str, Any]] | None = None,
    auth_status: str = "none",
    has_qr_threat: bool = False,
) -> ClassificationResult:
    """Compute calibrated six-class probabilities using trained ML model with heuristic fallback."""
    se = social_engineering_findings or []
    bec = bec_findings or []
    imp = impersonation_findings or []
    lookalikes = lookalike_findings or []
    conceal = concealment_findings or []
    att = attachment_findings or []
    urls = url_findings or []

    model = get_trained_model()

    # 1. Primary Path: Statistical ML Model Inference
    if model is not None and full_text.strip():
        try:
            probas = model.predict_proba([full_text])[0]
            class_names = list(model.classes_)
            ml_probabilities = {c: round(float(p), 4) for c, p in zip(class_names, probas)}

            # Ensure all 6 classes exist in output
            for c in CLASSES:
                if c not in ml_probabilities:
                    ml_probabilities[c] = 0.0

            predicted_class = max(ml_probabilities, key=ml_probabilities.get)
            pred_prob = ml_probabilities[predicted_class]
            confidence = "High" if pred_prob >= 0.70 else "Medium" if pred_prob >= 0.45 else "Low"

            # Aggregate forensic signals
            signals = []
            if lookalikes:
                signals.append("Lookalike Domain Detected")
            if imp:
                signals.append("Executive/VIP Impersonation Flag")
            if bec:
                signals.append(f"BEC Pattern: {bec[0].get('title', 'Financial Diversion')}")
            if any(a.get("is_suspicious") for a in att):
                signals.append("Dangerous / Disguised Attachment")
            if has_qr_threat:
                signals.append("Quishing / Decoded QR Destination")
            if conceal:
                signals.append("Adversarial Body Concealment")
            if any(u.get("mismatch_flag") for u in urls):
                signals.append("Deceptive URL Anchor Mismatch")
            for item in se:
                signals.append(f"Intent Pressure: {item.get('category', '')}")

            return ClassificationResult(
                predicted_class=predicted_class,
                probabilities=ml_probabilities,
                primary_threat_confidence=confidence,
                top_contributing_signals=list(dict.fromkeys(signals))[:5],
                engine_type="trained_ml",
            )
        except Exception:
            pass  # Fall through to heuristic fallback on any model error

    # 2. Fallback Path: Heuristic Logit Accumulator
    pred_cls, probs, conf, sigs = _heuristic_classify(
        social_engineering_findings=se,
        bec_findings=bec,
        impersonation_findings=imp,
        lookalike_findings=lookalikes,
        concealment_findings=conceal,
        attachment_findings=att,
        url_findings=urls,
        auth_status=auth_status,
        has_qr_threat=has_qr_threat,
    )

    return ClassificationResult(
        predicted_class=pred_cls,
        probabilities=probs,
        primary_threat_confidence=conf,
        top_contributing_signals=sigs,
        engine_type="heuristic_fallback",
    )
