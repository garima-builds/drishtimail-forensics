"""M2: Detection Feature Extractor & Pipeline Coordinator.

Orchestrates all NLP, heuristic, and pattern detection modules on parsed message content.
"""
from typing import Any
from .social_engineering import detect_social_engineering
from .bec_detector import detect_bec_patterns
from .impersonation import detect_impersonation
from .lookalike import detect_lookalike_domain
from .concealment import detect_concealment_techniques
from .thread_hijack import detect_thread_hijack
from .classifier import classify_message_intent, ClassificationResult


def run_detection_pipeline(
    *,
    sender: str,
    subject: str,
    headers: dict[str, list[str]],
    plain_text: str,
    html_body: str,
    url_artifacts: list[dict[str, Any]],
    attachment_artifacts: list[dict[str, Any]],
    auth_status: str,
    has_qr_threat: bool = False,
    protected_identities: list[dict[str, Any]] | None = None,
    protected_domains: list[str] | None = None,
) -> dict[str, Any]:
    """Execute complete M2 detection suite and return indicators with class probabilities."""
    full_text = f"{subject}\n{plain_text}"

    # 1. Social Engineering Cues
    se_findings = detect_social_engineering(full_text)

    # 2. BEC / Fraud Patterns
    bec_findings = detect_bec_patterns(full_text)

    # 3. Impersonation Check
    imp_findings = detect_impersonation(
        sender_header=sender,
        protected_identities=protected_identities,
        institutional_domains=protected_domains,
    )

    # 4. Lookalike Domain Check on Sender
    sender_domain = sender.split("@")[-1].strip(">").strip() if "@" in sender else ""
    lookalike_findings = detect_lookalike_domain(
        domain=sender_domain,
        protected_domains=protected_domains,
    )

    # Also check lookalikes in extracted URLs
    for url_obj in url_artifacts:
        dest_host = url_obj.get("destination_host", "")
        if dest_host and dest_host != sender_domain:
            url_lookalikes = detect_lookalike_domain(dest_host, protected_domains=protected_domains)
            lookalike_findings.extend(url_lookalikes)

    # 5. Concealment Check
    conceal_findings = detect_concealment_techniques(plain_text=plain_text, html_body=html_body)

    # 6. Thread Hijack Check
    th_findings = detect_thread_hijack(subject=subject, headers=headers)

    # 7. Multi-Class Probability Classification
    classification = classify_message_intent(
        social_engineering_findings=se_findings,
        bec_findings=bec_findings,
        impersonation_findings=imp_findings,
        lookalike_findings=lookalike_findings,
        concealment_findings=conceal_findings,
        attachment_findings=attachment_artifacts,
        url_findings=url_artifacts,
        auth_status=auth_status,
        has_qr_threat=has_qr_threat,
    )

    return {
        "classification": {
            "predicted_class": classification.predicted_class,
            "probabilities": classification.probabilities,
            "confidence": classification.primary_threat_confidence,
            "top_signals": classification.top_contributing_signals,
        },
        "social_engineering": se_findings,
        "bec_patterns": bec_findings,
        "impersonation": imp_findings,
        "lookalike_domains": lookalike_findings,
        "concealment": conceal_findings,
        "thread_hijack": th_findings,
    }
