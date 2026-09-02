"""F4: First-Contact Novelty Guardrail.

Enforces the critical safety assertion:
1. Novelty (first time an indicator is observed) alone must NEVER independently classify an email as malicious.
2. If removing first-contact signals drops an elevated/high score below the triage threshold,
   the guardrail intervenes, downgrades the verdict, and records explicit suppression rationale.
"""
from typing import Any


def apply_first_contact_guardrail(
    raw_score: int,
    contributions: list[dict[str, Any]],
    has_hard_threat_signals: bool,
    threshold: int = 55,
) -> tuple[int, str, bool, str | None]:
    """Test score against first-contact guardrail assertion.

    Returns:
        (final_score, final_verdict, was_suppressed, suppression_reason)
    """
    novelty_points = sum(c["points"] for c in contributions if c.get("family") == "novelty")

    score_without_novelty = max(0, raw_score - novelty_points)
    was_suppressed = False
    suppression_reason = None

    final_score = raw_score

    # If raw score reached High/Critical threshold primarily due to novelty without hard threats
    if raw_score >= threshold and score_without_novelty < threshold and not has_hard_threat_signals:
        final_score = score_without_novelty
        was_suppressed = True
        suppression_reason = (
            f"First-contact novelty contributed {novelty_points} points. "
            f"In accordance with institutional guardrails, novelty alone cannot trigger a High/Critical threat verdict. "
            f"Score safely adjusted from {raw_score} to {final_score}."
        )

    # Verdict classification
    if final_score >= 75:
        verdict = "Critical"
    elif final_score >= 55:
        verdict = "High"
    elif final_score >= 25:
        verdict = "Elevated"
    else:
        verdict = "Low"

    return final_score, verdict, was_suppressed, suppression_reason
