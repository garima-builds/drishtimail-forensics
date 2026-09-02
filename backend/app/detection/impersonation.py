import re
from typing import Any
from ..domain_utils import get_organizational_domain

DEFAULT_PROTECTED_ROLES = [
    "director", "registrar", "dean", "provost", "chancellor", "vice chancellor",
    "ceo", "cfo", "chief financial officer", "president", "head of department",
    "it helpdesk", "system administrator", "security operations"
]


def detect_impersonation(
    sender_header: str,
    protected_identities: list[dict[str, Any]] | None = None,
    institutional_domains: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Compare From display name and email address against protected lists."""
    if not sender_header:
        return []

    # Parse display name and email: "Dr. John Doe <john@attacker-domain.com>"
    match = re.search(r"^(.*?)(?:<([^>]+)>)?$", sender_header.strip())
    display_name = match.group(1).strip().strip('"\'') if match else ""
    email_addr = match.group(2).strip() if (match and match.group(2)) else sender_header.strip()

    email_domain_match = re.search(r"@([a-zA-Z0-9.\-_]+)", email_addr)
    email_domain = email_domain_match.group(1).lower() if email_domain_match else ""

    inst_orgs = {get_organizational_domain(d) for d in (institutional_domains or []) if d}
    sender_org = get_organizational_domain(email_domain)
    is_internal_sender = (sender_org in inst_orgs) if inst_orgs else False


    findings: list[dict[str, Any]] = []

    # 1. Protected VIP Name Matching
    for vip in (protected_identities or []):
        name = vip.get("name", "").lower()
        if name and name in display_name.lower():
            expected_email = vip.get("email", "").lower()
            if email_addr.lower() != expected_email and not is_internal_sender:
                findings.append({
                    "type": "vip_impersonation",
                    "severity": "Critical",
                    "title": f"Executive Impersonation: '{vip.get('name')}'",
                    "display_name": display_name,
                    "actual_email": email_addr,
                    "expected_email": expected_email,
                    "description": (
                        f"From display name matches protected individual '{vip.get('name')}', "
                        f"but email was sent from external address <{email_addr}>."
                    ),
                })

    # 2. Generic Institutional Role Impersonation
    if not findings and not is_internal_sender:
        for role in DEFAULT_PROTECTED_ROLES:
            if re.search(rf"\b{role}\b", display_name, re.IGNORECASE):
                findings.append({
                    "type": "role_impersonation",
                    "severity": "High",
                    "title": f"Institutional Role Impersonation: '{role.title()}'",
                    "display_name": display_name,
                    "actual_email": email_addr,
                    "description": (
                        f"Display name claims institutional role '{role.title()}', "
                        f"sent from non-institutional domain '{email_domain}'."
                    ),
                })
                break

    return findings
