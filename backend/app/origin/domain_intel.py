from datetime import datetime, timezone
from typing import Any
from ..domain_utils import extract_domain_parts

HIGH_RISK_TLDS = {".xyz", ".top", ".club", ".work", ".icu", ".cam", ".monster", ".buzz", ".vip", ".cfd", ".sbs"}


def evaluate_domain_risk(
    domain: str,
    creation_date: datetime | None = None,
    nameservers: list[str] | None = None,
    mx_records: list[str] | None = None,
) -> dict[str, Any]:
    """Analyze domain age and structural DNS properties for threat flags."""
    if not domain:
        return {"domain": "", "age_days": None, "high_risk_flags": []}

    domain_clean = domain.lower().strip().rstrip(".")
    ext = extract_domain_parts(domain_clean)
    suffix = f".{ext.suffix}".lower() if ext.suffix else ""


    flags: list[str] = []
    age_days: int | None = None

    # 1. Domain Age Evaluation
    if creation_date:
        if creation_date.tzinfo is None:
            creation_date = creation_date.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - creation_date
        age_days = max(0, delta.days)

        if age_days < 14:
            flags.append(f"Newly Registered Domain (< 14 days old: {age_days} days)")
        elif age_days < 30:
            flags.append(f"Young Domain (< 30 days old: {age_days} days)")

    # 2. High-Risk TLD Check
    if suffix in HIGH_RISK_TLDS:
        flags.append(f"High-Risk / Low-Reputation Top-Level Domain ({suffix})")

    # 3. Missing Mail Exchanger Check
    if mx_records is not None and len(mx_records) == 0:
        flags.append("Domain lacks published MX (Mail Exchanger) DNS records")

    return {
        "domain": domain_clean,
        "age_days": age_days,
        "creation_date": creation_date.isoformat() if creation_date else None,
        "nameservers": nameservers or [],
        "mail_records": mx_records or [],
        "high_risk_flags": flags,
        "is_high_risk": len(flags) > 0,
    }
