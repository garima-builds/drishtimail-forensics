"""M3: Sender Authentication & Protocol Alignment Validator.

Evaluates SPF, DKIM, DMARC, and ARC results from headers with domain alignment checks.
"""
import re
from dataclasses import dataclass
from ..domain_utils import extract_domain_parts, get_organizational_domain


@dataclass(frozen=True)
class ValidationOutput:
    spf: str
    dkim: str
    dmarc: str
    spf_aligned: bool
    dkim_aligned: bool
    arc_status: str
    forwarding_detected: bool
    from_domain: str | None
    return_path_domain: str | None
    dkim_domain: str | None


def _extract_domain(email_address: str | None) -> str | None:
    if not email_address:
        return None
    match = re.search(r"@([a-zA-Z0-9.\-_]+)", email_address)
    return match.group(1).lower().rstrip(".") if match else None


def _is_domain_aligned(d1: str | None, d2: str | None, strict: bool = False) -> bool:
    if not d1 or not d2:
        return False
    d1 = d1.lower().rstrip(".")
    d2 = d2.lower().rstrip(".")
    if strict:
        return d1 == d2
    return get_organizational_domain(d1) == get_organizational_domain(d2)



def validate_email_authentication(
    headers: dict[str, list[str]],
    sender_header: str | None = None,
) -> ValidationOutput:
    """Extract and validate SPF, DKIM, DMARC, ARC, and domain alignment."""
    auth_results_lines = headers.get("authentication-results", [])
    received_spf_lines = headers.get("received-spf", [])
    arc_results_lines = headers.get("arc-authentication-results", [])
    arc_seal_lines = headers.get("arc-seal", [])
    return_path_lines = headers.get("return-path", [])

    full_auth_text = " ".join(auth_results_lines + received_spf_lines).lower()

    # SPF Extraction
    spf_match = re.search(r"\bspf=(pass|fail|softfail|neutral|none|temperror|permerror)\b", full_auth_text)
    if not spf_match and received_spf_lines:
        first_spf = received_spf_lines[0].lower()
        for candidate in ("pass", "fail", "softfail", "neutral", "none", "temperror", "permerror"):
            if first_spf.startswith(candidate) or f" {candidate} " in first_spf:
                spf_match = re.search(rf"\b{candidate}\b", first_spf)
                break
    spf_result = spf_match.group(1) if spf_match else "none"

    # DKIM Extraction
    dkim_match = re.search(r"\bdkim=(pass|fail|neutral|none|temperror|permerror)\b", full_auth_text)
    dkim_result = dkim_match.group(1) if dkim_match else ("pass" if "dkim-signature" in headers else "none")

    # DMARC Extraction
    dmarc_match = re.search(r"\bdmarc=(pass|fail|none|temperror|permerror)\b", full_auth_text)
    dmarc_result = dmarc_match.group(1) if dmarc_match else "none"

    # ARC status
    arc_text = " ".join(arc_results_lines + arc_seal_lines).lower()
    arc_match = re.search(r"\b(?:arc=(pass|fail)|cv=(pass|fail|none))\b", arc_text)
    arc_status = (arc_match.group(1) or arc_match.group(2)) if arc_match else "none"

    # Forwarding signals
    forwarding_detected = bool(
        arc_results_lines
        or headers.get("x-forwarded-for")
        or headers.get("x-forwarded-to")
        or headers.get("resent-from")
        or headers.get("list-id")
        or headers.get("list-unsubscribe")
        or "mailing list" in full_auth_text
    )

    # Domain extraction for alignment
    from_raw = sender_header or (headers.get("from", [""])[0] if headers.get("from") else "")
    from_domain = _extract_domain(from_raw)

    return_path_raw = return_path_lines[0] if return_path_lines else ""
    return_path_domain = _extract_domain(return_path_raw)

    # DKIM signing domain extraction
    dkim_sig = " ".join(headers.get("dkim-signature", []))
    dkim_domain_match = re.search(r"\bd=([a-zA-Z0-9.\-_]+)", dkim_sig)
    dkim_domain = dkim_domain_match.group(1).lower() if dkim_domain_match else None

    # Alignment evaluations
    spf_aligned = _is_domain_aligned(from_domain, return_path_domain) if (spf_result == "pass") else False
    dkim_aligned = _is_domain_aligned(from_domain, dkim_domain) if (dkim_result == "pass") else False

    # Synthetic DMARC calculation if not in headers
    if dmarc_result == "none" and from_domain:
        if (spf_result == "pass" and spf_aligned) or (dkim_result == "pass" and dkim_aligned):
            dmarc_result = "pass"
        elif spf_result in {"fail", "softfail"} or dkim_result == "fail":
            dmarc_result = "fail"

    return ValidationOutput(
        spf=spf_result,
        dkim=dkim_result,
        dmarc=dmarc_result,
        spf_aligned=spf_aligned,
        dkim_aligned=dkim_aligned,
        arc_status=arc_status,
        forwarding_detected=forwarding_detected,
        from_domain=from_domain,
        return_path_domain=return_path_domain,
        dkim_domain=dkim_domain,
    )
