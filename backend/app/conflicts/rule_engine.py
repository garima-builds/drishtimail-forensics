"""F1 / M10: Evidence Conflict Rule Evaluation Engine.

Cross-checks outputs of M2 (Detections), M3 (Protocol & Headers), M4 (Origin),
M5 (Correlation Baseline), and M9 (URLs/QR) to detect contradictions and generate
dual-sided evidence citations.
"""
from typing import Any
from .rule_table import CONFLICT_RULES


def evaluate_evidence_conflicts(
    *,
    auth_results: dict[str, Any],
    anomalies: list[dict[str, Any]],
    detections: dict[str, Any],
    url_artifacts: list[dict[str, Any]],
    qr_results: list[dict[str, Any]],
    origin_info: dict[str, Any] | None = None,
    indicator_history: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Evaluate all 9 evidence conflict rules against analyzed message signals."""
    conflicts: list[dict[str, Any]] = []

    spf = auth_results.get("spf", "none")
    dkim = auth_results.get("dkim", "none")
    dmarc = auth_results.get("dmarc", "none")
    spf_aligned = auth_results.get("spf_aligned", False)
    dkim_aligned = auth_results.get("dkim_aligned", False)
    forwarding_detected = auth_results.get("forwarding_detected", False)

    classification = detections.get("classification", {})
    predicted_class = classification.get("predicted_class", "benign")
    threat_prob = 1.0 - classification.get("probabilities", {}).get("benign", 0.5)

    has_bec = bool(detections.get("bec_patterns"))
    has_imp = bool(detections.get("impersonation"))
    has_lookalike = bool(detections.get("lookalike_domains"))
    has_conceal = bool(detections.get("concealment"))
    has_content_risk = (threat_prob >= 0.60) or has_bec or has_imp or has_lookalike or has_conceal

    # Rule C01: Authenticated but Misaligned
    if (spf == "pass" or dkim == "pass") and not (spf_aligned or dkim_aligned):
        conflicts.append({
            "conflict_type": "authenticated_but_misaligned",
            "rule_id": "C01",
            "severity": "High",
            "title": "Authenticated but Misaligned Sender",
            "summary": "Technical cryptographic check passed on a 3rd party domain, but does not align with the Header From identity.",
            "evidence_side_a": f"Authentication Result: SPF={spf}, DKIM={dkim} passed on envelope/signing domain.",
            "evidence_side_b": "Header Alignment: Domain alignment check failed (From domain does not match signing/return-path domain).",
            "score_adjustment": 15,
        })

    # Rule C02: Reply-Path Divergence
    reply_to_anom = [a for a in anomalies if a.get("type") == "reply_to_divergence"]
    if reply_to_anom:
        conflicts.append({
            "conflict_type": "reply_path_divergence",
            "rule_id": "C02",
            "severity": "High",
            "title": "Reply-Path Header Divergence",
            "summary": "Visible sender domain contradicts the destination where email responses will be routed.",
            "evidence_side_a": f"From Header: {reply_to_anom[0].get('description')}",
            "evidence_side_b": "Reply-To Header: Configured to route replies to a different domain.",
            "score_adjustment": 20,
        })

    # Rule C03: Cryptographic Pass with High Content Threat (Account Compromise)
    if dmarc == "pass" and has_content_risk:
        conflicts.append({
            "conflict_type": "auth_pass_vs_content_risk",
            "rule_id": "C03",
            "severity": "Critical",
            "title": "Cryptographic Pass with High Content Threat (Likely Compromised Account)",
            "summary": "Sender passes strict DMARC alignment, but message body contains aggressive financial fraud, lookalike links, or credential solicitation.",
            "evidence_side_a": "Protocol Authentication: DMARC passed with valid aligned domain ownership.",
            "evidence_side_b": f"Content Threat Engine: High-risk intent detected (Class: {predicted_class}, Confidence: {classification.get('confidence', 'High')}).",
            "score_adjustment": 25,
        })

    # Rule C04: Authentication Fail with Benign Content (Forwarding / Mailing List)
    if (spf in {"fail", "softfail"} or dkim == "fail") and not has_content_risk and forwarding_detected:
        conflicts.append({
            "conflict_type": "auth_fail_vs_benign_content",
            "rule_id": "C04",
            "severity": "Low",
            "title": "Authentication Failure with Benign Content (Forwarding Artifact)",
            "summary": "Authentication failed due to forwarding intermediate MTAs, but content contains no hostile signals.",
            "evidence_side_a": f"Protocol Authentication: SPF={spf}, DKIM={dkim} failed at receiving border.",
            "evidence_side_b": "Transit & Content: Forwarding headers present and message content is benign.",
            "score_adjustment": -10,  # Mitigate false positive
        })

    # Rule C05: Display Text vs Destination Host Mismatch
    mismatched_urls = [u for u in url_artifacts if u.get("mismatch_flag")]
    if mismatched_urls:
        first_mismatch = mismatched_urls[0]
        conflicts.append({
            "conflict_type": "display_text_vs_destination_host",
            "rule_id": "C05",
            "severity": "Critical",
            "title": "Anchor Text vs Destination Host Mismatch",
            "summary": "Visible hyperlink label explicitly mimics a trusted brand while the underlying link routes to an external host.",
            "evidence_side_a": f"Visible Text: '{first_mismatch.get('anchor_text')}'",
            "evidence_side_b": f"Destination Host: '{first_mismatch.get('destination_host')}' (URL: {first_mismatch.get('raw_url')[:60]}...)",
            "score_adjustment": 25,
        })

    # Rule C06: QR Code Destination vs Body Text Divergence
    qr_urls = [q for q in qr_results if q.get("payload")]
    body_urls = [u for u in url_artifacts if u.get("provenance") in {"body", "html_anchor"}]
    if qr_urls:
        qr_hosts = {q["payload"].split("/")[2].lower() for q in qr_urls if "//" in q["payload"]}
        body_hosts = {u.get("destination_host", "").lower() for u in body_urls if u.get("destination_host")}
        # Check if QR host is completely divergent from body text links
        if qr_hosts and not (qr_hosts & body_hosts):
            conflicts.append({
                "conflict_type": "qr_destination_vs_body_divergence",
                "rule_id": "C06",
                "severity": "High",
                "title": "QR Payload vs Body Text Divergence",
                "summary": "Message body text contains no links or benign links, but the embedded QR code payload routes to an unmentioned external host.",
                "evidence_side_a": f"Body Content: {len(body_urls)} text hyperlinks present.",
                "evidence_side_b": f"QR Code Engine: Decoded payload routes to '{', '.join(qr_hosts)}'.",
                "score_adjustment": 20,
            })

    # Rule C07: Origin Geography vs Claimed Entity
    if origin_info and origin_info.get("country_code"):
        infra_type = origin_info.get("infra_type", "")
        country = origin_info.get("country", "")
        if infra_type in {"datacenter", "vpn_proxy"} and has_imp:
            conflicts.append({
                "conflict_type": "geography_vs_claimed_entity",
                "rule_id": "C07",
                "severity": "Medium",
                "title": "Origin Infrastructure vs Claimed Entity",
                "summary": "Message claims to represent institutional leadership, but origin IP resolves to a commercial cloud/proxy datacenter.",
                "evidence_side_a": "Claimed Sender: Institutional leadership / internal authority.",
                "evidence_side_b": f"Origin Infrastructure: {infra_type.title()} IP located in {country}.",
                "score_adjustment": 15,
            })

    # Rule C08: Relay Timestamp vs Latency Timing
    timing_anom = [a for a in anomalies if a.get("type") == "negative_hop_delay"]
    if timing_anom:
        conflicts.append({
            "conflict_type": "header_timestamp_vs_relay_timing",
            "rule_id": "C08",
            "severity": "Medium",
            "title": "Relay Timestamp & Sequence Inconsistency",
            "summary": "Intermediate relay hops show negative time progression or forged timestamp intervals.",
            "evidence_side_a": "Relay Hop Headers: Chronological transit order.",
            "evidence_side_b": "Timestamp Sequence: Negative inter-hop transit latency detected.",
            "score_adjustment": 10,
        })

    return conflicts
