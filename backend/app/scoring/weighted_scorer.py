"""F8 / M11: Explainable Weighted-Additive Threat Scoring Engine.

Implements transparent, additive threat scoring with strict family weight ceilings,
conflict adjustments from M10, first-contact guardrail enforcement, and structured explanations.
"""
from dataclasses import dataclass
from typing import Any
from .normalizer import NormalizedSignal, SignalNormalizer
from .first_contact_guard import apply_first_contact_guardrail
from .explainer import ScoreExplainer, FIXED_DISCLAIMER

# Default per-family weight ceilings
FAMILY_CEILINGS = {
    "authentication": 28,
    "content_intent": 35,
    "url_quishing": 30,
    "infrastructure": 20,
    "novelty": 10,
}


@dataclass(frozen=True)
class ScoredVerdict:
    score: int
    verdict: str  # Low, Elevated, High, Critical
    confidence: str  # Low, Medium, High
    contributions: list[dict[str, Any]]
    family_breakdown: dict[str, dict[str, int]]
    narrative_summary: str
    disclaimer: str
    first_contact_suppressed: bool
    suppression_reason: str | None


class WeightedScorer:
    """Calculates additive explainable threat scores with family ceilings and guardrails."""

    @classmethod
    def compute(
        cls,
        signals: list[NormalizedSignal],
        conflicts: list[dict[str, Any]],
        custom_ceilings: dict[str, int] | None = None,
    ) -> ScoredVerdict:
        """Compute transparent additive threat score with ceiling clamping and conflict adjustments."""
        ceilings = dict(custom_ceilings or FAMILY_CEILINGS)
        family_points_acc: dict[str, int] = {k: 0 for k in ceilings}
        contributions: list[dict[str, Any]] = []

        # 1. Calculate points per signal family
        for sig in signals:
            family = sig.family
            ceiling = ceilings.get(family, 25)

            if family == "content_intent":
                base_pts = int(sig.strength * 22)
            elif family == "authentication":
                base_pts = int(sig.strength * 28)
            elif family == "url_quishing":
                base_pts = int(sig.strength * 25)
            elif family == "infrastructure":
                base_pts = int(sig.strength * 15)
            elif family == "novelty":
                base_pts = int(sig.strength * 10)
            else:
                base_pts = int(sig.strength * 10)

            current_family_total = family_points_acc.get(family, 0)
            allowed_pts = max(0, min(base_pts, ceiling - current_family_total))

            if allowed_pts > 0:
                family_points_acc[family] = current_family_total + allowed_pts
                contributions.append({
                    "signal": sig.name,
                    "family": family,
                    "points": allowed_pts,
                    "reason": sig.raw_reason,
                    "evidence_reference_id": sig.evidence_reference_id,
                })

        # 2. Add M10 Evidence Conflict Adjustments
        conflict_net = sum(c.get("score_adjustment", 0) for c in conflicts)
        conflict_pts = max(-10, min(25, conflict_net))
        if conflict_pts != 0:
            contributions.append({
                "signal": f"Evidence Conflict Adjustment ({len(conflicts)} detected)",
                "family": "conflicts",
                "points": conflict_pts,
                "reason": f"Adjusted threat score based on {len(conflicts)} cross-evidence contradiction(s).",
                "evidence_reference_id": None,
            })

        raw_sum = sum(c["points"] for c in contributions)
        raw_score = max(0, min(100, raw_sum))

        # 3. Check for hard threat signals (e.g. high-confidence BEC, phishing links, active mismatch)
        has_hard_threats = any(
            c.get("family") in {"content_intent", "url_quishing", "authentication"} and c.get("points", 0) >= 15
            for c in contributions
        )

        # 4. Apply First-Contact Novelty Guardrail
        final_score, verdict, suppressed, supp_reason = apply_first_contact_guardrail(
            raw_score=raw_score,
            contributions=contributions,
            has_hard_threat_signals=has_hard_threats,
            threshold=55,
        )

        # 5. Confidence calculation
        total_signals = len(signals) + len(conflicts)
        if total_signals >= 4 and final_score >= 50:
            confidence = "High"
        elif total_signals >= 2:
            confidence = "Medium"
        else:
            confidence = "Low"

        # 6. Compose structured explanation via ScoreExplainer
        explanation = ScoreExplainer.compose_explanation(
            score=final_score,
            verdict=verdict,
            confidence=confidence,
            contributions=contributions,
            family_points_acc=family_points_acc,
            family_ceilings=ceilings,
            first_contact_suppressed=suppressed,
            suppression_reason=supp_reason,
        )

        return ScoredVerdict(
            score=explanation.score,
            verdict=explanation.verdict,
            confidence=explanation.confidence,
            contributions=explanation.contributions,
            family_breakdown=explanation.family_breakdown,
            narrative_summary=explanation.narrative_summary,
            disclaimer=explanation.disclaimer,
            first_contact_suppressed=explanation.first_contact_suppressed,
            suppression_reason=explanation.suppression_reason,
        )


def compute_explainable_score(
    signals: list[NormalizedSignal],
    conflicts: list[dict[str, Any]],
    custom_ceilings: dict[str, int] | None = None,
) -> ScoredVerdict:
    """Convenience functional wrapper for WeightedScorer.compute."""
    return WeightedScorer.compute(
        signals=signals,
        conflicts=conflicts,
        custom_ceilings=custom_ceilings,
    )
