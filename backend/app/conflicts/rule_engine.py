"""F1 / M10: Evidence Conflict Rule Evaluation Engine.

Cross-checks outputs of M2 (Detections), M3 (Protocol & Headers), M4 (Origin),
M5 (Correlation Baseline), and M9 (URLs/QR) to detect cross-evidence contradictions,
attaching exact evidence reference IDs and structured dual-sided narratives.
"""
from typing import Any
from uuid import UUID
from .rule_table import ConflictRuleTable, ConflictRule
from .narrator import ConflictNarrator


class ConflictRuleEngine:
    """Evaluates the 9 canonical evidence conflict rules across forensic signals."""

    @classmethod
    def evaluate(
        cls,
        *,
        auth_results: dict[str, Any],
        anomalies: list[dict[str, Any]],
        detections: dict[str, Any],
        url_artifacts: list[dict[str, Any]],
        qr_results: list[dict[str, Any]],
        origin_info: dict[str, Any] | None = None,
        indicator_history: dict[str, Any] | list[dict[str, Any]] | None = None,
        external_threat_flags: list[dict[str, Any]] | None = None,
        evidence_refs: dict[str, UUID | str] | None = None,
    ) -> list[dict[str, Any]]:
        """Evaluate all 9 conflict rules and return enriched conflict findings."""
        conflicts: list[dict[str, Any]] = []
        refs = evidence_refs or {}
        default_ref = refs.get("primary") or refs.get("body") or None

        spf = (auth_results.get("spf") or "none").lower()
        dkim = (auth_results.get("dkim") or "none").lower()
        dmarc = (auth_results.get("dmarc") or "none").lower()
        spf_aligned = bool(auth_results.get("spf_aligned", False))
        dkim_aligned = bool(auth_results.get("dkim_aligned", False))
        forwarding_detected = bool(auth_results.get("forwarding_detected", False))

        classification = detections.get("classification", {})
        predicted_class = classification.get("predicted_class", "benign")
        threat_prob = 1.0 - classification.get("probabilities", {}).get("benign", 0.5)

        has_bec = bool(detections.get("bec_patterns"))
        has_imp = bool(detections.get("impersonation"))
        has_lookalike = bool(detections.get("lookalike_domains"))
        has_conceal = bool(detections.get("concealment"))
        has_content_risk = (threat_prob >= 0.60) or has_bec or has_imp or has_lookalike or has_conceal

        # -------------------------------------------------------------
        # Rule C01: Authenticated but Misaligned Sender
        # -------------------------------------------------------------
        if (spf == "pass" or dkim == "pass") and not (spf_aligned or dkim_aligned):
            rule = ConflictRuleTable.get_by_id("C01")
            if rule:
                narrative = ConflictNarrator.narrate(
                    rule=rule,
                    side_a_detail=f"Authentication Result: SPF={spf}, DKIM={dkim} passed on third-party envelope/signing domain.",
                    side_b_detail="Header Alignment: Domain alignment check failed (Header From domain does not align with envelope or signing identity).",
                    specific_context="Sender passed technical cryptographic authentication on an unaligned third-party infrastructure.",
                )
                conflicts.append({
                    "conflict_type": rule.conflict_type,
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "title": rule.title,
                    "summary": narrative.summary,
                    "evidence_side_a": narrative.evidence_side_a,
                    "evidence_side_b": narrative.evidence_side_b,
                    "investigative_guidance": narrative.investigative_guidance,
                    "reconciliation_effect": narrative.reconciliation_effect,
                    "score_adjustment": rule.base_score_adjustment,
                    "evidence_ref_a_id": refs.get("auth", default_ref),
                    "evidence_ref_b_id": refs.get("from", default_ref),
                    "detail": {
                        "spf": spf,
                        "dkim": dkim,
                        "spf_aligned": spf_aligned,
                        "dkim_aligned": dkim_aligned,
                    },
                })

        # -------------------------------------------------------------
        # Rule C02: Reply-Path Header Divergence
        # -------------------------------------------------------------
        reply_to_anom = [a for a in anomalies if a.get("type") == "reply_to_divergence"]
        if reply_to_anom:
            rule = ConflictRuleTable.get_by_id("C02")
            if rule:
                anom = reply_to_anom[0]
                narrative = ConflictNarrator.narrate(
                    rule=rule,
                    side_a_detail=f"From Header: Claimed sender entity ({anom.get('header_name', 'From')}).",
                    side_b_detail=f"Reply-To Header: Routed to divergent address/domain ({anom.get('description')}).",
                    specific_context=anom.get("description"),
                )
                conflicts.append({
                    "conflict_type": rule.conflict_type,
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "title": rule.title,
                    "summary": narrative.summary,
                    "evidence_side_a": narrative.evidence_side_a,
                    "evidence_side_b": narrative.evidence_side_b,
                    "investigative_guidance": narrative.investigative_guidance,
                    "reconciliation_effect": narrative.reconciliation_effect,
                    "score_adjustment": rule.base_score_adjustment,
                    "evidence_ref_a_id": refs.get("from", default_ref),
                    "evidence_ref_b_id": refs.get("reply_to", default_ref),
                    "detail": {"anomaly": anom},
                })

        # -------------------------------------------------------------
        # Rule C03: Cryptographic Pass with High Content Threat
        # -------------------------------------------------------------
        if dmarc == "pass" and has_content_risk:
            rule = ConflictRuleTable.get_by_id("C03")
            if rule:
                narrative = ConflictNarrator.narrate(
                    rule=rule,
                    side_a_detail="Protocol Authentication: Cryptographic DMARC verification passed for claimed domain owner.",
                    side_b_detail=f"Content Threat Engine: High-risk hostile intent identified (Class: {predicted_class}, Probability: {int(threat_prob * 100)}%).",
                    specific_context="Sender passed strict DMARC alignment, but message body contains aggressive financial fraud, lookalike links, or credential solicitation (Account Compromise Indicator).",
                )
                conflicts.append({
                    "conflict_type": rule.conflict_type,
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "title": rule.title,
                    "summary": narrative.summary,
                    "evidence_side_a": narrative.evidence_side_a,
                    "evidence_side_b": narrative.evidence_side_b,
                    "investigative_guidance": narrative.investigative_guidance,
                    "reconciliation_effect": narrative.reconciliation_effect,
                    "score_adjustment": rule.base_score_adjustment,
                    "evidence_ref_a_id": refs.get("auth", default_ref),
                    "evidence_ref_b_id": refs.get("body", default_ref),
                    "detail": {
                        "predicted_class": predicted_class,
                        "threat_prob": threat_prob,
                        "has_bec": has_bec,
                        "has_imp": has_imp,
                    },
                })

        # -------------------------------------------------------------
        # Rule C04: Authentication Fail with Benign Content (Forwarding)
        # -------------------------------------------------------------
        if (spf in {"fail", "softfail"} or dkim == "fail") and not has_content_risk and forwarding_detected:
            rule = ConflictRuleTable.get_by_id("C04")
            if rule:
                narrative = ConflictNarrator.narrate(
                    rule=rule,
                    side_a_detail=f"Protocol Authentication: SPF={spf}, DKIM={dkim} failed at receiving border gateway.",
                    side_b_detail="Transit & Content: Intermediary forwarding headers present and message content contains zero threat cues.",
                    specific_context="Sender authentication failed due to forwarding/mailing list hops, but content analysis reveals legitimate communication.",
                )
                conflicts.append({
                    "conflict_type": rule.conflict_type,
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "title": rule.title,
                    "summary": narrative.summary,
                    "evidence_side_a": narrative.evidence_side_a,
                    "evidence_side_b": narrative.evidence_side_b,
                    "investigative_guidance": narrative.investigative_guidance,
                    "reconciliation_effect": narrative.reconciliation_effect,
                    "score_adjustment": rule.base_score_adjustment,
                    "evidence_ref_a_id": refs.get("auth", default_ref),
                    "evidence_ref_b_id": refs.get("received", default_ref),
                    "detail": {
                        "spf": spf,
                        "dkim": dkim,
                        "forwarding_detected": True,
                    },
                })

        # -------------------------------------------------------------
        # Rule C05: Visible Anchor vs Destination Host Mismatch
        # -------------------------------------------------------------
        mismatched_urls = [u for u in url_artifacts if u.get("mismatch_flag")]
        if mismatched_urls:
            rule = ConflictRuleTable.get_by_id("C05")
            if rule:
                first_mismatch = mismatched_urls[0]
                anchor = first_mismatch.get("anchor_text") or "Trusted Domain Display"
                dest = first_mismatch.get("destination_host") or first_mismatch.get("normalized_url")
                narrative = ConflictNarrator.narrate(
                    rule=rule,
                    side_a_detail=f"Visible Anchor Text: Displays trusted reference '{anchor}'.",
                    side_b_detail=f"Underlying Destination: Hyperlink href routes to external host '{dest}'.",
                    specific_context=f"Visible link displays '{anchor}' but points to external destination '{dest}'.",
                )
                conflicts.append({
                    "conflict_type": rule.conflict_type,
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "title": rule.title,
                    "summary": narrative.summary,
                    "evidence_side_a": narrative.evidence_side_a,
                    "evidence_side_b": narrative.evidence_side_b,
                    "investigative_guidance": narrative.investigative_guidance,
                    "reconciliation_effect": narrative.reconciliation_effect,
                    "score_adjustment": rule.base_score_adjustment,
                    "evidence_ref_a_id": refs.get("body", default_ref),
                    "evidence_ref_b_id": refs.get("url", default_ref),
                    "detail": {
                        "anchor_text": anchor,
                        "destination_host": dest,
                        "raw_url": first_mismatch.get("raw_url"),
                    },
                })

        # -------------------------------------------------------------
        # Rule C06: QR Code Payload vs Body Text Divergence
        # -------------------------------------------------------------
        qr_urls = [q for q in qr_results if q.get("payload")]
        body_urls = [u for u in url_artifacts if u.get("provenance") in {"body", "html_anchor"}]
        if qr_urls:
            qr_hosts = {q["payload"].split("/")[2].lower() for q in qr_urls if "//" in q["payload"]}
            body_hosts = {u.get("destination_host", "").lower() for u in body_urls if u.get("destination_host")}
            if qr_hosts and not (qr_hosts & body_hosts):
                rule = ConflictRuleTable.get_by_id("C06")
                if rule:
                    narrative = ConflictNarrator.narrate(
                        rule=rule,
                        side_a_detail=f"Body Text: Contains {len(body_urls)} text hyperlinks (none matching QR destination).",
                        side_b_detail=f"QR Code Engine: Decoded embedded image routes to unmentioned external host(s): {', '.join(qr_hosts)}.",
                        specific_context="Email body text contains no suspicious links or mentions, while an attached or inline QR code embeds an unlinked external URL.",
                    )
                    conflicts.append({
                        "conflict_type": rule.conflict_type,
                        "rule_id": rule.rule_id,
                        "severity": rule.severity,
                        "title": rule.title,
                        "summary": narrative.summary,
                        "evidence_side_a": narrative.evidence_side_a,
                        "evidence_side_b": narrative.evidence_side_b,
                        "investigative_guidance": narrative.investigative_guidance,
                        "reconciliation_effect": narrative.reconciliation_effect,
                        "score_adjustment": rule.base_score_adjustment,
                        "evidence_ref_a_id": refs.get("body", default_ref),
                        "evidence_ref_b_id": refs.get("part", default_ref),
                        "detail": {
                            "qr_hosts": list(qr_hosts),
                            "body_hosts": list(body_hosts),
                        },
                    })

        # -------------------------------------------------------------
        # Rule C07: Origin Geography vs Claimed Sender Entity
        # -------------------------------------------------------------
        if origin_info and origin_info.get("country_code"):
            infra_type = origin_info.get("infra_type", "")
            country = origin_info.get("country", "")
            if infra_type in {"datacenter", "vpn_proxy"} and has_imp:
                rule = ConflictRuleTable.get_by_id("C07")
                if rule:
                    narrative = ConflictNarrator.narrate(
                        rule=rule,
                        side_a_detail="Claimed Sender: Institutional leadership or domestic official authority.",
                        side_b_detail=f"Origin Infrastructure: Earliest reliable hop originates from {infra_type.title()} IP ({origin_info.get('ip')}) in {country}.",
                        specific_context=f"Sender claims internal institutional identity, but origin IP resolves to a commercial {infra_type} in {country}.",
                    )
                    conflicts.append({
                        "conflict_type": rule.conflict_type,
                        "rule_id": rule.rule_id,
                        "severity": rule.severity,
                        "title": rule.title,
                        "summary": narrative.summary,
                        "evidence_side_a": narrative.evidence_side_a,
                        "evidence_side_b": narrative.evidence_side_b,
                        "investigative_guidance": narrative.investigative_guidance,
                        "reconciliation_effect": narrative.reconciliation_effect,
                        "score_adjustment": rule.base_score_adjustment,
                        "evidence_ref_a_id": refs.get("from", default_ref),
                        "evidence_ref_b_id": refs.get("received", default_ref),
                        "detail": {
                            "origin_ip": origin_info.get("ip"),
                            "infra_type": infra_type,
                            "country": country,
                        },
                    })

        # -------------------------------------------------------------
        # Rule C08: Relay Timestamp vs Latency Timing
        # -------------------------------------------------------------
        timing_anom = [a for a in anomalies if a.get("type") == "negative_hop_delay"]
        if timing_anom:
            rule = ConflictRuleTable.get_by_id("C08")
            if rule:
                narrative = ConflictNarrator.narrate(
                    rule=rule,
                    side_a_detail="Relay Hop Sequence: Chronological bottom-to-top transit order.",
                    side_b_detail="Hop Timestamp Analysis: Negative latency or impossible progression detected across intermediate nodes.",
                    specific_context="Recorded timestamps in Received headers show negative or physically impossible transit intervals, suggesting clock skew or forged headers.",
                )
                conflicts.append({
                    "conflict_type": rule.conflict_type,
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "title": rule.title,
                    "summary": narrative.summary,
                    "evidence_side_a": narrative.evidence_side_a,
                    "evidence_side_b": narrative.evidence_side_b,
                    "investigative_guidance": narrative.investigative_guidance,
                    "reconciliation_effect": narrative.reconciliation_effect,
                    "score_adjustment": rule.base_score_adjustment,
                    "evidence_ref_a_id": refs.get("received", default_ref),
                    "evidence_ref_b_id": refs.get("received", default_ref),
                    "detail": {"anomalies": timing_anom},
                })

        # -------------------------------------------------------------
        # Rule C09: External Feed Flag on Established Local Sender
        # -------------------------------------------------------------
        hist = indicator_history if isinstance(indicator_history, dict) else (indicator_history[0] if (indicator_history and len(indicator_history) > 0) else {})
        is_familiar = hist.get("familiarity_band") in {"Common", "Familiar"} or hist.get("sighting_count", 0) > 5
        if external_threat_flags and is_familiar:
            rule = ConflictRuleTable.get_by_id("C09")
            if rule:
                narrative = ConflictNarrator.narrate(
                    rule=rule,
                    side_a_detail=f"External Threat Feed: Flagged indicator with hostile reputation ({external_threat_flags[0].get('feed_name', 'Threat Feed')}).",
                    side_b_detail=f"Institutional Baseline: Indicator has established local history ({hist.get('sighting_count')} sightings, Familiar band).",
                    specific_context="External reputation feed flagged an indicator, but local institutional history demonstrates a long, familiar, clean baseline.",
                )
                conflicts.append({
                    "conflict_type": rule.conflict_type,
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "title": rule.title,
                    "summary": narrative.summary,
                    "evidence_side_a": narrative.evidence_side_a,
                    "evidence_side_b": narrative.evidence_side_b,
                    "investigative_guidance": narrative.investigative_guidance,
                    "reconciliation_effect": narrative.reconciliation_effect,
                    "score_adjustment": rule.base_score_adjustment,
                    "evidence_ref_a_id": refs.get("feed", default_ref),
                    "evidence_ref_b_id": refs.get("baseline", default_ref),
                    "detail": {
                        "feed_flags": external_threat_flags,
                        "history": hist,
                    },
                })

        return conflicts


def evaluate_evidence_conflicts(
    *,
    auth_results: dict[str, Any],
    anomalies: list[dict[str, Any]],
    detections: dict[str, Any],
    url_artifacts: list[dict[str, Any]],
    qr_results: list[dict[str, Any]],
    origin_info: dict[str, Any] | None = None,
    indicator_history: dict[str, Any] | list[dict[str, Any]] | None = None,
    external_threat_flags: list[dict[str, Any]] | None = None,
    evidence_refs: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Convenience functional wrapper for ConflictRuleEngine.evaluate."""
    return ConflictRuleEngine.evaluate(
        auth_results=auth_results,
        anomalies=anomalies,
        detections=detections,
        url_artifacts=url_artifacts,
        qr_results=qr_results,
        origin_info=origin_info,
        indicator_history=indicator_history,
        external_threat_flags=external_threat_flags,
        evidence_refs=evidence_refs,
    )
