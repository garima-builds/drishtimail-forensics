"""F8 / M11: Forensic Signal Normalizer.

Standardizes heterogeneous forensic findings across disparate detection modules
into normalized strength metrics (0.0 to 1.0) grouped by signal family,
preserving evidence reference IDs on every individual signal.
"""
from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class NormalizedSignal:
    family: str  # 'authentication', 'content_intent', 'url_quishing', 'infrastructure', 'conflicts', 'novelty'
    name: str
    strength: float  # 0.0 to 1.0
    raw_reason: str
    evidence_reference_id: str | None = None
    indicator_value: str | None = None


class SignalNormalizer:
    """Normalizes raw forensic detections and protocol validation outputs."""

    @classmethod
    def normalize_all_signals(
        cls,
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
        evidence_refs: dict[str, Any] | None = None,
    ) -> list[NormalizedSignal]:
        """Transform all module outputs into normalized scoring signals with evidence references."""
        signals: list[NormalizedSignal] = []
        refs = evidence_refs or {}
        default_ref = str(refs.get("primary") or refs.get("body") or "") or None

        auth_ref = str(refs.get("auth") or default_ref) if refs.get("auth") or default_ref else None
        body_ref = str(refs.get("body") or default_ref) if refs.get("body") or default_ref else None
        received_ref = str(refs.get("received") or default_ref) if refs.get("received") or default_ref else None

        # ---------------------------------------------------------
        # 1. Authentication Family (max family ceiling = 28 pts)
        # ---------------------------------------------------------
        dmarc = (auth_results.get("dmarc") or "none").lower()
        spf = (auth_results.get("spf") or "none").lower()
        dkim = (auth_results.get("dkim") or "none").lower()
        spf_aligned = bool(auth_results.get("spf_aligned", False))
        dkim_aligned = bool(auth_results.get("dkim_aligned", False))

        if dmarc in {"fail", "permerror"}:
            signals.append(NormalizedSignal(
                family="authentication",
                name="DMARC Policy Failure",
                strength=1.0,
                raw_reason="Domain owner policy rejected the message transmission.",
                evidence_reference_id=auth_ref,
            ))
        elif spf in {"fail", "softfail"} or dkim == "fail":
            signals.append(NormalizedSignal(
                family="authentication",
                name="SPF/DKIM Verification Failure",
                strength=0.75,
                raw_reason=f"Cryptographic sender validation failed (SPF={spf}, DKIM={dkim}).",
                evidence_reference_id=auth_ref,
            ))
        elif (spf == "pass" or dkim == "pass") and not (spf_aligned or dkim_aligned):
            signals.append(NormalizedSignal(
                family="authentication",
                name="Sender Domain Misalignment",
                strength=0.6,
                raw_reason="Authentication passed on unaligned third-party envelope.",
                evidence_reference_id=auth_ref,
            ))

        # ---------------------------------------------------------
        # 2. Content & NLP Intent Family (max family ceiling = 35 pts)
        # ---------------------------------------------------------
        classification = detections.get("classification", {})
        predicted_class = classification.get("predicted_class", "benign")
        if predicted_class != "benign":
            class_prob = classification.get("probabilities", {}).get(predicted_class, 0.5)
            signals.append(NormalizedSignal(
                family="content_intent",
                name=f"Intent Classification: {predicted_class.replace('_', ' ').title()}",
                strength=min(1.0, float(class_prob)),
                raw_reason=f"Multi-class threat model evaluated {int(class_prob * 100)}% probability of {predicted_class.replace('_', ' ')}.",
                evidence_reference_id=body_ref,
            ))

        for bec in detections.get("bec_patterns", []):
            sev = bec.get("severity", "High")
            signals.append(NormalizedSignal(
                family="content_intent",
                name=bec.get("title", "BEC Pattern"),
                strength=1.0 if sev == "Critical" else 0.8,
                raw_reason=bec.get("description", "BEC fraud pattern identified in text."),
                evidence_reference_id=body_ref,
            ))

        for imp in detections.get("impersonation", []):
            signals.append(NormalizedSignal(
                family="content_intent",
                name=imp.get("title", "Executive Impersonation"),
                strength=1.0,
                raw_reason=imp.get("description", "Sender display name mimics leadership identity."),
                evidence_reference_id=str(refs.get("from") or default_ref) if (refs.get("from") or default_ref) else None,
            ))

        for lookalike in detections.get("lookalike_domains", []):
            signals.append(NormalizedSignal(
                family="content_intent",
                name=lookalike.get("title", "Lookalike Domain"),
                strength=1.0 if lookalike.get("severity") == "Critical" else 0.8,
                raw_reason=lookalike.get("description", "Domain mimics trusted brand via homoglyph, typosquat, or TLD swap."),
                evidence_reference_id=str(refs.get("from") or default_ref) if (refs.get("from") or default_ref) else None,
                indicator_value=lookalike.get("domain"),
            ))

        for conceal in detections.get("concealment", []):
            signals.append(NormalizedSignal(
                family="content_intent",
                name=conceal.get("title", "Adversarial Concealment"),
                strength=0.75,
                raw_reason=conceal.get("description", "Zero-width characters or hidden CSS element styling detected."),
                evidence_reference_id=body_ref,
            ))

        # ---------------------------------------------------------
        # 3. URL & Quishing Family (max family ceiling = 30 pts)
        # ---------------------------------------------------------
        mismatched_urls = [u for u in url_artifacts if u.get("mismatch_flag")]
        if mismatched_urls:
            signals.append(NormalizedSignal(
                family="url_quishing",
                name="Deceptive Anchor Text Mismatch",
                strength=1.0,
                raw_reason=f"Hyperlink anchor text deceptively mimics trusted host: '{mismatched_urls[0].get('anchor_text')}'.",
                evidence_reference_id=str(mismatched_urls[0].get("evidence_reference_id") or body_ref) if (mismatched_urls[0].get("evidence_reference_id") or body_ref) else None,
                indicator_value=mismatched_urls[0].get("raw_url"),
            ))

        qr_threats = [q for q in qr_results if q.get("payload")]
        if qr_threats:
            signals.append(NormalizedSignal(
                family="url_quishing",
                name="Quishing: Embedded QR Code Destination",
                strength=0.85,
                raw_reason=f"Embedded QR code image decoded to external URL: {qr_threats[0].get('payload')[:50]}...",
                evidence_reference_id=str(refs.get("part") or default_ref) if (refs.get("part") or default_ref) else None,
                indicator_value=qr_threats[0].get("payload"),
            ))

        undecodable_qr = [q for q in qr_results if q.get("undecodable")]
        if undecodable_qr:
            signals.append(NormalizedSignal(
                family="url_quishing",
                name="Quishing: QR Present but Undecodable",
                strength=0.5,
                raw_reason="QR finder patterns detected in image but symbols could not be decoded across rotations.",
                evidence_reference_id=str(refs.get("part") or default_ref) if (refs.get("part") or default_ref) else None,
            ))

        suspicious_att = [a for a in attachment_artifacts if a.get("is_suspicious")]
        if suspicious_att:
            for att in suspicious_att:
                for ind in att.get("static_indicators", []):
                    signals.append(NormalizedSignal(
                        family="url_quishing",
                        name=f"Attachment Risk: {ind.get('type')}",
                        strength=1.0 if ind.get("severity") == "Critical" else 0.8,
                        raw_reason=ind.get("description", "Disguised executable magic bytes or embedded macro detected."),
                        evidence_reference_id=str(att.get("evidence_reference_id") or refs.get("part") or default_ref) if (att.get("evidence_reference_id") or refs.get("part") or default_ref) else None,
                        indicator_value=att.get("filename"),
                    ))

        # ---------------------------------------------------------
        # 4. Infrastructure & Relay Anomalies (max ceiling = 20 pts)
        # ---------------------------------------------------------
        for anom in anomalies:
            signals.append(NormalizedSignal(
                family="infrastructure",
                name=anom.get("title", "Header Anomaly"),
                strength=0.75 if anom.get("severity") == "High" else 0.5,
                raw_reason=anom.get("description", "Header or routing inconsistency detected."),
                evidence_reference_id=received_ref,
            ))

        if origin_info and origin_info.get("infra_type") in {"datacenter", "vpn_proxy"}:
            signals.append(NormalizedSignal(
                family="infrastructure",
                name=f"Origin Infrastructure: {origin_info.get('infra_type', '').title()}",
                strength=0.4,
                raw_reason=f"Earliest reliable relay hop originates from {origin_info.get('infra_type')} IP ({origin_info.get('ip')}).",
                evidence_reference_id=received_ref,
                indicator_value=origin_info.get("ip"),
            ))

        # ---------------------------------------------------------
        # 5. First-Contact / Novelty Family (max ceiling = 10 pts)
        # ---------------------------------------------------------
        if first_contact_info and first_contact_info.get("is_first_contact") and not first_contact_info.get("suppressed"):
            signals.append(NormalizedSignal(
                family="novelty",
                name="First-Contact Sender Domain (Novelty)",
                strength=0.35,
                raw_reason="Sender domain has not been observed previously in institutional baseline history.",
                evidence_reference_id=str(refs.get("from") or default_ref) if (refs.get("from") or default_ref) else None,
                indicator_value=first_contact_info.get("value"),
            ))

        return signals


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
    evidence_refs: dict[str, Any] | None = None,
) -> list[NormalizedSignal]:
    """Convenience functional wrapper for SignalNormalizer.normalize_all_signals."""
    return SignalNormalizer.normalize_all_signals(
        auth_results=auth_results,
        anomalies=anomalies,
        detections=detections,
        url_artifacts=url_artifacts,
        qr_results=qr_results,
        attachment_artifacts=attachment_artifacts,
        conflicts=conflicts,
        origin_info=origin_info,
        first_contact_info=first_contact_info,
        evidence_refs=evidence_refs,
    )
