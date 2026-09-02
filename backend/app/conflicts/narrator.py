"""F1 / M10: Conflict Narrator.

Synthesizes objective forensic explanations for cross-evidence contradictions,
providing dual-sided citations, investigative guidance, and non-attribution framing.
"""
from dataclasses import dataclass
from typing import Any
from .rule_table import ConflictRule


@dataclass(frozen=True)
class ConflictNarrative:
    conflict_type: str
    rule_id: str
    severity: str
    title: str
    summary: str
    evidence_side_a: str
    evidence_side_b: str
    investigative_guidance: str
    reconciliation_effect: str
    non_attribution_note: str


class ConflictNarrator:
    """Generates structured narrative explanations for detected evidence conflicts."""

    @staticmethod
    def narrate(
        rule: ConflictRule,
        side_a_detail: str,
        side_b_detail: str,
        specific_context: str | None = None,
    ) -> ConflictNarrative:
        """Compose a structured conflict narrative with dual-sided citations."""
        guidance_map = {
            "C01": "Inspect envelope Return-Path against Header From. Verify if sending service is an authorized third-party SaaS provider or an unauthorized relay channel.",
            "C02": "Do not reply via automated email. Verify identity through out-of-band communication before taking action on requests routed to the divergent Reply-To address.",
            "C03": "Treat sending account as potentially compromised. Inspect earliest reliable hop IP against user login telemetry and check for mailbox forwarding rules.",
            "C04": "Review ARC seal chain and DKIM signatures to determine if upstream forwarder modified message headers while preserving original integrity.",
            "C05": "Examine the underlying URL destination host. Do not rely on visible hyperlink text or brand logos as proof of destination legitimacy.",
            "C06": "Trace decoded QR code destination through URL unshortening and sandbox analysis. Treat QR payload as an out-of-band link bypass attempt.",
            "C07": "Check if institution has authorized foreign cloud infrastructure or if the origin node belongs to a commercial hosting provider/proxy.",
            "C08": "Analyze intermediate MTA clock synchronizations and Received header syntax for signs of artificial header insertion or proxying.",
            "C09": "Correlate external threat intelligence against local historical familiarity. A high internal baseline suggests potential feed false positive.",
        }

        reconciliation_map = {
            "C01": f"Score increased by +{rule.base_score_adjustment} pts due to unaligned sender identity.",
            "C02": f"Score increased by +{rule.base_score_adjustment} pts due to diverted response routing.",
            "C03": f"Score increased by +{rule.base_score_adjustment} pts; cryptographic pass overridden by hostile payload intent.",
            "C04": f"Score adjusted by {rule.base_score_adjustment} pts; technical authentication failure mitigated by benign content and forwarding headers.",
            "C05": f"Score increased by +{rule.base_score_adjustment} pts due to active visual deception in hyperlink text.",
            "C06": f"Score increased by +{rule.base_score_adjustment} pts due to unlinked external destination embedded in QR image.",
            "C07": f"Score increased by +{rule.base_score_adjustment} pts due to geographic/infrastructure divergence.",
            "C08": f"Score increased by +{rule.base_score_adjustment} pts due to temporal transit inconsistency.",
            "C09": f"Score adjusted by {rule.base_score_adjustment} pts; external feed alert attenuated by established local familiarity.",
        }

        summary = specific_context or rule.description
        guidance = guidance_map.get(rule.rule_id, "Review both evidence sources and cross-correlate with organizational logs.")
        reconciliation = reconciliation_map.get(rule.rule_id, f"Score adjusted by {rule.base_score_adjustment} pts.")
        disclaimer = "Finding represents technical cross-evidence inconsistency, not a conclusive determination of attacker identity."

        return ConflictNarrative(
            conflict_type=rule.conflict_type,
            rule_id=rule.rule_id,
            severity=rule.severity,
            title=rule.title,
            summary=summary,
            evidence_side_a=side_a_detail,
            evidence_side_b=side_b_detail,
            investigative_guidance=guidance,
            reconciliation_effect=reconciliation,
            non_attribution_note=disclaimer,
        )
