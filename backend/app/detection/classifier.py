"""M2: Multi-Class Threat Probability Classifier.

Emits calibrated probabilities across six distinct threat classes:
1. Phishing (Credential harvesting & deceptive links)
2. BEC / Financial Fraud (Invoices, wire diversion, gift cards)
3. Malware Carrier (Hostile attachments & macros)
4. Impersonation (Leadership & VIP spoofing)
5. Spam / Bulk (Unsolicited mass marketing)
6. Benign (Legitimate verified communication)
"""
import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ClassificationResult:
    predicted_class: str
    probabilities: dict[str, float]
    primary_threat_confidence: str
    top_contributing_signals: list[str]


def classify_message_intent(
    *,
    social_engineering_findings: list[dict[str, Any]],
    bec_findings: list[dict[str, Any]],
    impersonation_findings: list[dict[str, Any]],
    lookalike_findings: list[dict[str, Any]],
    concealment_findings: list[dict[str, Any]],
    attachment_findings: list[dict[str, Any]],
    url_findings: list[dict[str, Any]],
    auth_status: str,  # 'pass', 'fail', 'none'
    has_qr_threat: bool = False,
) -> ClassificationResult:
    """Compute calibrated six-class probabilities from extracted indicator families."""
    # Raw logit accumulators
    logits = {
        "phishing": 0.5,
        "bec_fraud": 0.5,
        "malware_carrier": 0.2,
        "impersonation": 0.2,
        "spam": 1.0,
        "benign": 2.5 if auth_status == "pass" else 1.0,
    }
    signals: list[str] = []

    # 1. Lookalike domain signals -> strongly Phishing / Impersonation
    if lookalike_findings:
        logits["phishing"] += 3.5 * len(lookalike_findings)
        logits["impersonation"] += 2.0 * len(lookalike_findings)
        logits["benign"] -= 2.0
        signals.append("Lookalike Domain Detected")

    # 2. Impersonation findings -> strongly Impersonation / BEC
    if impersonation_findings:
        logits["impersonation"] += 4.5 * len(impersonation_findings)
        logits["bec_fraud"] += 2.0
        logits["benign"] -= 2.5
        signals.append("Executive/VIP Impersonation Flag")

    # 3. BEC findings -> strongly BEC Fraud
    if bec_findings:
        logits["bec_fraud"] += 4.5 * len(bec_findings)
        logits["phishing"] += 1.0
        logits["benign"] -= 3.0
        signals.append(f"BEC Pattern: {bec_findings[0].get('title', 'Financial Diversion')}")

    # 4. Attachment static risks -> strongly Malware Carrier
    suspicious_att = [a for a in attachment_findings if a.get("is_suspicious")]
    if suspicious_att:
        logits["malware_carrier"] += 5.0 * len(suspicious_att)
        logits["phishing"] += 1.5
        logits["benign"] -= 3.0
        signals.append("Dangerous / Disguised Attachment")

    # 5. QR Code Threats / Quishing -> Phishing
    if has_qr_threat:
        logits["phishing"] += 3.5
        logits["benign"] -= 2.0
        signals.append("Quishing / Decoded QR Destination")

    # 6. Concealment findings -> Phishing / Spam
    if concealment_findings:
        logits["phishing"] += 2.0
        logits["spam"] += 2.5
        signals.append("Adversarial Body Concealment")

    # 7. Social Engineering cues
    for se in social_engineering_findings:
        cat = se.get("category", "")
        if cat in {"financial_instruction", "urgency"}:
            logits["bec_fraud"] += 1.5
            logits["phishing"] += 1.5
        if cat in {"authority", "threat_of_consequence"}:
            logits["impersonation"] += 1.5
            logits["phishing"] += 1.5
        signals.append(f"Intent Pressure: {cat}")

    # 8. URL presence with mismatches
    mismatched_urls = [u for u in url_findings if u.get("mismatch_flag")]
    if mismatched_urls:
        logits["phishing"] += 3.0
        signals.append("Deceptive URL Anchor Mismatch")

    # Softmax conversion to probabilities
    max_logit = max(logits.values())
    exp_logits = {k: math.exp(v - max_logit) for k, v in logits.items()}
    sum_exp = sum(exp_logits.values())
    probabilities = {k: round(v / sum_exp, 4) for k, v in exp_logits.items()}

    # Predicted class is highest probability
    predicted_class = max(probabilities, key=probabilities.get)
    pred_prob = probabilities[predicted_class]

    confidence = "High" if pred_prob >= 0.70 else "Medium" if pred_prob >= 0.45 else "Low"

    return ClassificationResult(
        predicted_class=predicted_class,
        probabilities=probabilities,
        primary_threat_confidence=confidence,
        top_contributing_signals=list(dict.fromkeys(signals))[:5],
    )
