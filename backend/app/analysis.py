import re
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit


@dataclass(frozen=True)
class AuthSemantics:
    spf: str
    dkim: str
    dmarc: str
    key: str
    establishes: str
    does_not_establish: str
    effect: str


def _result(headers: dict[str, list[str]], mechanism: str) -> str:
    values = " ".join(headers.get("authentication-results", [])).lower()
    match = re.search(rf"\b{mechanism}=(pass|fail|softfail|neutral|none|temperror|permerror)\b", values)
    return match.group(1) if match else "none"


def authentication_semantics(headers: dict[str, list[str]]) -> AuthSemantics:
    spf, dkim, dmarc = (_result(headers, value) for value in ("spf", "dkim", "dmarc"))
    key = f"spf:{spf}|dkim:{dkim}|dmarc:{dmarc}"
    if dmarc == "pass" and (spf == "pass" or dkim == "pass"):
        return AuthSemantics(spf, dkim, dmarc, key, "The receiving system observed an aligned sender-authentication result for this message.", "Authentication results do not establish that the sender's intent, content, links, or attachments are safe.", "Treat sender identity as technically authenticated; continue content and delivery-path analysis.")
    if any(value in {"fail", "softfail", "permerror", "temperror"} for value in (spf, dkim, dmarc)):
        return AuthSemantics(spf, dkim, dmarc, key, "The authentication record establishes a failed or unreliable sender-authentication check.", "A failure alone does not identify a sender or prove malicious intent.", "Increase scrutiny of identity signals and preserve the conflicting header evidence.")
    return AuthSemantics(spf, dkim, dmarc, key, "The available headers do not provide a positive aligned authentication conclusion.", "Absence of a pass does not by itself establish spoofing or maliciousness.", "Keep identity confidence limited and assess other independent signals.")


URL_PATTERN = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)


def normalize_url(raw: str) -> str:
    parsed = urlsplit(raw.rstrip(".,;:!?"))
    host = (parsed.hostname or "").lower()
    netloc = host if parsed.port is None else f"{host}:{parsed.port}"
    return urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "/", parsed.query, ""))


def extract_urls(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for match in URL_PATTERN.finditer(text):
        raw = match.group(0)
        normalized = normalize_url(raw)
        if normalized not in seen:
            seen.add(normalized)
            found.append((raw, normalized))
    return found
