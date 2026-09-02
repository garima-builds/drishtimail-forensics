import re
from typing import Any
from ..domain_utils import extract_domain_parts, get_organizational_domain


URL_LIKE_PATTERN = re.compile(r"(?:https?://)?([a-zA-Z0-9.\-_]+\.[a-zA-Z]{2,})", re.IGNORECASE)
BRAND_NAMES = ("microsoft", "google", "office", "bank", "paypal", "apple", "amazon", "netflix", "adobe", "university", "sbi", "hdfc", "icici")


def compare_display_vs_destination(
    anchor_text: str | None,
    destination_host: str,
) -> dict[str, Any]:
    """Check if visible anchor text deceives the user about the actual link destination."""
    if not anchor_text or not destination_host:
        return {"mismatch": False, "reason": None}

    anchor_clean = anchor_text.strip().lower()
    dest_clean = destination_host.strip().lower()

    # Case 1: Anchor text looks like a URL/domain
    match = URL_LIKE_PATTERN.search(anchor_clean)
    if match:
        claimed_domain = match.group(1).lower()
        claimed_org = get_organizational_domain(claimed_domain)
        dest_org = get_organizational_domain(dest_clean)

        if claimed_org != dest_org and claimed_org:
            return {
                "mismatch": True,
                "severity": "Critical",
                "claimed_host": claimed_domain,
                "actual_host": dest_clean,
                "reason": (
                    f"Visible text displays trusted domain '{claimed_domain}', but hyperlink routes to '{dest_clean}'."
                ),
            }


    # Case 2: Anchor text contains brand name while destination is not brand's domain
    for brand in BRAND_NAMES:
        if brand in anchor_clean and brand not in dest_clean:
            return {
                "mismatch": True,
                "severity": "High",
                "claimed_host": brand,
                "actual_host": dest_clean,
                "reason": (
                    f"Link text refers to '{brand}', but the actual link destination is '{dest_clean}'."
                ),
            }

    return {"mismatch": False, "reason": None}
