"""F8 / M11: Score Explainer.

Formats transparent, evidence-referenced explanations for threat scores,
providing family point breakdowns, ordered signal attributions, and non-attribution disclaimers.
"""
from dataclasses import dataclass
from typing import Any

FIXED_DISCLAIMER = (
    "This threat score and confidence evaluation are an explainable triage aid based on technical signals, "
    "not a conclusive legal determination of sender identity or malicious intent."
)


@dataclass(frozen=True)
class ScoreExplanationResult:
    score: int
    verdict: str
    confidence: str
    contributions: list[dict[str, Any]]
    family_breakdown: dict[str, dict[str, int]]
    narrative_summary: str
    disclaimer: str
    first_contact_suppressed: bool
    suppression_reason: str | None


class ScoreExplainer:
    """Composes structured, explainable breakdowns of threat scoring decisions."""

    @classmethod
    def compose_explanation(
        cls,
        *,
        score: int,
        verdict: str,
        confidence: str,
        contributions: list[dict[str, Any]],
        family_points_acc: dict[str, int],
        family_ceilings: dict[str, int],
        first_contact_suppressed: bool = False,
        suppression_reason: str | None = None,
    ) -> ScoreExplanationResult:
        """Build structured explanation result with family breakdown and ordered contributions."""
        sorted_contributions = sorted(
            contributions,
            key=lambda item: (abs(item.get("points", 0)), item.get("family") != "conflicts"),
            reverse=True,
        )

        family_breakdown = {
            fam: {
                "allocated_points": family_points_acc.get(fam, 0),
                "ceiling_points": family_ceilings.get(fam, 0),
            }
            for fam in family_ceilings
        }

        # Build narrative summary
        top_signals = [c["signal"] for c in sorted_contributions[:3] if c.get("points", 0) > 0]
        if top_signals:
            narrative = f"Message evaluated with a {verdict} threat priority ({score}/100, {confidence} confidence). Primary technical score drivers: {', '.join(top_signals)}."
        else:
            narrative = f"Message evaluated with a {verdict} threat priority ({score}/100). No significant adversarial technical signals detected."

        if first_contact_suppressed and suppression_reason:
            narrative += f" [Guardrail Note: {suppression_reason}]"

        return ScoreExplanationResult(
            score=score,
            verdict=verdict,
            confidence=confidence,
            contributions=sorted_contributions,
            family_breakdown=family_breakdown,
            narrative_summary=narrative,
            disclaimer=FIXED_DISCLAIMER,
            first_contact_suppressed=first_contact_suppressed,
            suppression_reason=suppression_reason,
        )
