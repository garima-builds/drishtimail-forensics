"""Domain extraction and TLD parsing helper with graceful zero-dependency fallback."""
from dataclasses import dataclass
import re

try:
    import tldextract
    _HAS_TLDEXTRACT = True
except ImportError:
    _HAS_TLDEXTRACT = False


@dataclass(frozen=True)
class ExtractedDomain:
    subdomain: str
    domain: str
    suffix: str


COMMON_MULTI_TLDS = {
    "co.uk", "org.uk", "gov.uk", "ac.uk", "co.in", "ac.in", "gov.in", "res.in",
    "edu.in", "nic.in", "net.in", "org.in", "com.au", "edu.au", "gov.au",
    "co.jp", "ne.jp", "ac.jp", "gov.jp", "com.br", "co.za", "com.sg", "edu.sg"
}


def extract_domain_parts(domain_str: str | None) -> ExtractedDomain:
    """Extract subdomain, domain, and suffix with graceful fallback."""
    if not domain_str:
        return ExtractedDomain("", "", "")

    clean = domain_str.lower().strip().rstrip(".")

    if _HAS_TLDEXTRACT:
        try:
            res = tldextract.extract(clean)
            return ExtractedDomain(subdomain=res.subdomain or "", domain=res.domain or "", suffix=res.suffix or "")
        except Exception:
            pass

    # Pure Python fallback parser
    tokens = clean.split(".")
    if len(tokens) == 1:
        return ExtractedDomain("", tokens[0], "")
    elif len(tokens) == 2:
        return ExtractedDomain("", tokens[0], tokens[1])

    # Check for known 2-part suffixes like .ac.in or .co.uk
    two_part_suffix = ".".join(tokens[-2:])
    if two_part_suffix in COMMON_MULTI_TLDS:
        domain = tokens[-3] if len(tokens) >= 3 else ""
        subdomain = ".".join(tokens[:-3]) if len(tokens) > 3 else ""
        return ExtractedDomain(subdomain=subdomain, domain=domain, suffix=two_part_suffix)

    # Default 1-part suffix (.com, .org, .edu, .xyz)
    suffix = tokens[-1]
    domain = tokens[-2]
    subdomain = ".".join(tokens[:-2])
    return ExtractedDomain(subdomain=subdomain, domain=domain, suffix=suffix)


def get_organizational_domain(domain_str: str | None) -> str:
    """Return 'example.com' or 'university.edu' for any subdomain."""
    if not domain_str:
        return ""
    parts = extract_domain_parts(domain_str)
    if parts.domain and parts.suffix:
        return f"{parts.domain}.{parts.suffix}".lower()
    return domain_str.lower().strip().rstrip(".")
