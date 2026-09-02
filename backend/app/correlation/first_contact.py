"""F4: First-Contact Institutional Baseline Engine.

Tracks sighting counts, historical frequency, and familiarity bands (Novel, Rare, Common)
for all institutional indicators.
Suppresses first-contact novelty signals until database volume meets minimum history floor.
"""
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from ..models import IndicatorHistory, Message


def check_and_update_indicator_history(
    db: Session,
    indicator_type: str,
    value: str,
    is_active_case: bool = False,
    history_suppression_floor: int = 20,
) -> dict[str, Any]:
    """Look up indicator familiarity, update sighting count, and apply suppression floor."""
    val_clean = value.strip().lower()
    now_dt = datetime.now(timezone.utc)

    record = db.scalar(
        select(IndicatorHistory).where(
            IndicatorHistory.indicator_type == indicator_type,
            IndicatorHistory.value == val_clean,
        )
    )

    total_indexed_messages = db.scalar(select(func.count()).select_from(Message)) or 0
    is_floor_met = (total_indexed_messages >= history_suppression_floor)

    if not record:
        record = IndicatorHistory(
            indicator_type=indicator_type,
            value=val_clean,
            first_seen=now_dt,
            last_seen=now_dt,
            sighting_count=1,
            distinct_cases=1 if is_active_case else 0,
            familiarity_band="Novel",
        )
        db.add(record)
        is_first_contact = True
        band = "Novel"
    else:
        record.sighting_count += 1
        record.last_seen = now_dt
        if is_active_case:
            record.distinct_cases += 1

        if record.sighting_count > 5:
            record.familiarity_band = "Common"
        elif record.sighting_count > 1:
            record.familiarity_band = "Rare"
        else:
            record.familiarity_band = "Novel"

        is_first_contact = False
        band = record.familiarity_band

    return {
        "indicator_type": indicator_type,
        "value": val_clean,
        "first_seen": record.first_seen.isoformat(),
        "last_seen": record.last_seen.isoformat(),
        "sighting_count": record.sighting_count,
        "distinct_cases": record.distinct_cases,
        "familiarity_band": band,
        "is_first_contact": is_first_contact,
        "suppressed": (not is_floor_met),
        "suppression_reason": (
            None if is_floor_met else
            f"First-contact signal suppressed: system message volume ({total_indexed_messages}) is below history threshold ({history_suppression_floor})."
        ),
    }
