"""M11: Signal Normalizer.

Standardizes heterogeneous forensic findings across disparate detection modules
into normalized strength metrics (0.0 to 1.0) grouped by signal family.
"""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizedSignal:
    family: str  # 'authentication', 'content_intent', 'url_quishing', 'infrastructure', 'conflicts', 'novelty'
    name: str
    strength: float  # 0.0 to 1.0
    raw_reason: str
    evidence_reference_id: str | None = None


def normalize_all_signals(
    *,
    auth_results: dict[str, Any],
    anomalies: list[dict[str, Any]],
    detections: dict[str, Any],
    url_artifacts: list[dict[str, Any]],
    qr_results: list[dict[str, Any]],
    attachment_artifacts: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
    origin_info: dict[str, Any] | None = None,
    first_contact_info: dict[str, Any] | None = None,
) -> list[NormalizedSignal]:
    """Transform all module outputs into normalized scoring signals."""
    signals: list[NormalizedSignal] = []

    # 1. Authentication Family
    dmarc = auth_results.get("dmarc", "none")
    spf = auth_results.get("spf", "none")
    dkim = auth_results.get("dkim", "none")
    if dmarc in {"fail", "permerror"}:
        signals.append(NormalizedSignal(
            family="authentication",
            name="DMARC Policy Failure",
            strength=1.0,
            raw_reason="Domain owner policy rejected the message transmission.",
        ))
    elif spf in {"fail", "softfail"} or dkim == "fail":
        signals.append(NormalizedSignal(
            family="authentication",
            name="SPF/DKIM Verification Failure",
            strength=0.75,
            raw_reason=f"Cryptographic check failed: SPF={spf}, DKIM={dkim}.",
        ))
    elif not auth_results.get("spf_aligned") and not auth_results.get("dkim_aligned") and (spf == "pass" or dkim == "pass"):
        signals.append(NormalizedSignal(
            family="authentication",
            name="Sender Domain Misalignment",
            strength=0.6,
            raw_reason="Authentication passed on unaligned third-party envelope.",
        ))

    # 2. Content & NLP Intent Family
    classification = detections.get("classification", {})
    predicted_class = classification.get("predicted_class", "benign")
    if predicted_class != "benign":
        class_prob = classification.get("probabilities", {}).get(predicted_class, 0.5)
        signals.append(NormalizedSignal(
            family="content_intent",
            name=f"Intent Classification: {predicted_class.replace('_', ' ').title()}",
            strength=min(1.0, class_prob),
            raw_reason=f"Multi-class threat model evaluated {int(class_prob * 100)}% probability of {predicted_class}.",
        ))

    for bec in detections.get("bec_patterns", []):
        signals.append(NormalizedSignal(
            family="content_intent",
            name=bec.get("title", "BEC Pattern"),
            strength=1.0 if bec.get("severity") == "Critical" else 0.8,
            raw_reason=bec.get("description", "BEC fraud pattern identified in text."),
        ))

    for imp in detections.get("impersonation", []):
        signals.append(NormalizedSignal(
            family="content_intent",
            name=imp.get("title", "Executive Impersonation"),
            strength=1.0,
            raw_reason=imp.get("description", "Sender display name mimics leadership."),
        ))

    for lookalike in detections.get("lookalike_domains", []):
        signals.append(NormalizedSignal(
            family="content_intent",
            name=lookalike.get("title", "Lookalike Domain"),
            strength=1.0 if lookalike.get("severity") == "Critical" else 0.8,
            raw_reason=lookalike.get("description", "Domain mimics trusted brand."),
        ))

    for conceal in detections.get("concealment", []):
        signals.append(NormalizedSignal(
            family="content_intent",
            name=conceal.get("title", "Adversarial Concealment"),
            strength=0.75,
            raw_reason=conceal.get("description", "Zero-width characters or hidden CSS detected."),
        ))

    # 3. URL & Quishing Family
    mismatched_urls = [u for u in url_artifacts if u.get("mismatch_flag")]
    if mismatched_urls:
        signals.append(NormalizedSignal(
            family="url_quishing",
            name="Deceptive Anchor Text Mismatch",
            strength=1.0,
            raw_reason=f"Link anchor text deceptively mimics trusted host: {mismatched_urls[0].get('anchor_text')}.",
        ))

    qr_threats = [q for q in qr_results if q.get("payload")]
    if qr_threats:
        signals.append(NormalizedSignal(
            family="url_quishing",
            name="Quishing: Embedded QR Code Destination",
            strength=0.85,
            raw_reason=f"Embedded QR code decoded to external URL: {qr_threats[0].get('payload')[:50]}...",
        ))

    undecodable_qr = [q for q in qr_results if q.get("undecodable")]
    if undecodable_qr:
        signals.append(NormalizedSignal(
            family="url_quishing",
            name="Quishing: QR Present but Undecodable",
            strength=0.5,
            raw_reason="QR finder patterns detected but symbols could not be decoded across rotations.",
        ))

    suspicious_att = [a for a in attachment_artifacts if a.get("is_suspicious")]
    if suspicious_att:
        for att in suspicious_att:
            for ind in att.get("static_indicators", []):
                signals.append(NormalizedSignal(
                    family="url_quishing",
                    name=f"Attachment Risk: {ind.get('type')}",
                    strength=1.0 if ind.get("severity") == "Critical" else 0.8,
                    raw_reason=ind.get("description", "Disguised executable or embedded macro."),
                ))

    # 4. Infrastructure & Relay Anomalies Family
    for anom in anomalies:
        signals.append(NormalizedSignal(
            family="infrastructure",
            name=anom.get("title", "Header Anomaly"),
            strength=0.75 if anom.get("severity") == "High" else 0.5,
            raw_reason=anom.get("description", "Header inconsistency detected."),
        ))

    if origin_info and origin_info.get("infra_type") in {"datacenter", "vpn_proxy"}:
        signals.append(NormalizedSignal(
            family="infrastructure",
            name=f"Origin Infrastructure: {origin_info.get('infra_type', '').title()}",
            strength=0.4,
            raw_reason=f"Earliest reliable hop originates from {origin_info.get('infra_type')} IP ({origin_info.get('ip')}).",
        ))

    # 5. First-Contact / Novelty Family
    if first_contact_info and first_contact_info.get("is_first_contact") and not first_contact_info.get("suppressed"):
        signals.append(NormalizedSignal(
            family="novelty",
            name="First-Contact Sender Domain (Novelty)",
            strength=0.35,
            raw_reason="Sender domain has not been observed previously in institutional baseline history.",
        ))

    return signals
