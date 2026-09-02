import re
from typing import Any
from ..domain_utils import extract_domain_parts

# Common character substitution / homoglyph mapping
HOMOGLYPH_MAP = {
    '0': 'o', '1': 'l', '3': 'e', '4': 'a', '5': 's', '8': 'b',
    'vv': 'w', 'rn': 'm', 'cl': 'd', 'cj': 'g',
    '\u0430': 'a', '\u043e': 'o', '\u0440': 'p', '\u0441': 'c', '\u0443': 'y', '\u0445': 'x',  # Cyrillic
    '\u03bf': 'o', '\u03c1': 'p', '\u03b1': 'a',  # Greek
}

PROTECTED_BRANDS = [
    "microsoft", "office365", "google", "paypal", "apple", "amazon",
    "netflix", "adobe", "chase", "wellsfargo", "university", "aicte", "sih"
]


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute string edit distance."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def _normalize_homoglyphs(text: str) -> str:
    """Normalize common numeric and unicode homoglyphs."""
    norm = text.lower()
    for sub, target in HOMOGLYPH_MAP.items():
        norm = norm.replace(sub, target)
    return norm


def detect_lookalike_domain(
    domain: str,
    protected_domains: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Scan a domain name for lookalike, homoglyph, and typosquatting traits."""
    if not domain:
        return []

    domain_clean = domain.lower().strip().rstrip(".")
    findings: list[dict[str, Any]] = []

    # 1. IDN / Punycode check
    if "xn--" in domain_clean:
        try:
            decoded_domain = domain_clean.encode("ascii").decode("idna")
            findings.append({
                "type": "punycode_idn",
                "severity": "High",
                "title": "Internationalized / Punycode Domain",
                "domain": domain_clean,
                "decoded": decoded_domain,
                "description": f"Domain uses Punycode ({domain_clean}) which renders visually as '{decoded_domain}'.",
            })
        except Exception:
            findings.append({
                "type": "punycode_idn",
                "severity": "High",
                "title": "Punycode Domain Flag",
                "domain": domain_clean,
                "description": f"Domain contains Punycode prefix (xn--): '{domain_clean}'.",
            })

    extracted = extract_domain_parts(domain_clean)
    base_name = extracted.domain.lower() if extracted.domain else domain_clean
    normalized_name = _normalize_homoglyphs(base_name)

    # 2. Check against protected institutional domains
    targets = set(protected_domains or [])
    for brand in PROTECTED_BRANDS:
        targets.add(brand)

    for target in targets:
        target_ext = extract_domain_parts(target.lower())
        target_name = target_ext.domain.lower() if target_ext.domain else target.lower()

        if base_name == target_name:
            # Check TLD swap (e.g. university.xyz instead of university.edu)
            if target_ext.suffix and extracted.suffix and extracted.suffix != target_ext.suffix:
                findings.append({
                    "type": "tld_swap",
                    "severity": "High",
                    "title": f"TLD Swap against '{target}'",
                    "domain": domain_clean,
                    "target": target,
                    "description": f"Domain '{domain_clean}' mimics official domain '{target}' under a different TLD (.{extracted.suffix}).",
                })
            continue


        # Check Homoglyph Normalization match
        if normalized_name == target_name:
            findings.append({
                "type": "homoglyph_substitution",
                "severity": "Critical",
                "title": f"Homoglyph Deception of '{target_name}'",
                "domain": domain_clean,
                "target": target_name,
                "description": (
                    f"Domain label '{base_name}' uses character substitution to mimic brand '{target_name}'."
                ),
            })
            continue

        # Check Levenshtein Edit Distance (1 or 2 edits away on names >= 5 chars)
        if len(target_name) >= 5 and abs(len(base_name) - len(target_name)) <= 2:
            dist = _levenshtein_distance(base_name, target_name)
            if dist in (1, 2):
                findings.append({
                    "type": "edit_distance_typosquat",
                    "severity": "High",
                    "title": f"Typosquat / Edit-Distance Lookalike of '{target_name}'",
                    "domain": domain_clean,
                    "target": target_name,
                    "distance": dist,
                    "description": (
                        f"Domain '{domain_clean}' is only {dist} edit(s) away from trusted domain '{target_name}'."
                    ),
                })

    return findings
