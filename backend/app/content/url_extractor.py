"""M9: URL Extractor & Normalizer.

Extracts hyperlinks from plain-text and HTML bodies with anchor text tracking,
normalizes URL syntax, and converges QR-derived and body URLs into a single artifact set.
"""
import re
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit
from bs4 import BeautifulSoup


URL_REGEX = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)


@dataclass(frozen=True)
class ExtractedUrl:
    raw_url: str
    normalized_url: str
    destination_host: str
    provenance: str  # 'body', 'html_anchor', 'qr_inline', 'qr_attachment', 'attachment_link'
    anchor_text: str | None = None


def normalize_url(raw: str) -> str:
    """Normalize a URL string by stripping punctuation, lowercasing scheme/host."""
    cleaned = raw.strip().rstrip(".,;:!?)>\"'")
    try:
        parsed = urlsplit(cleaned)
        scheme = (parsed.scheme or "http").lower()
        host = (parsed.hostname or "").lower()
        if not host:
            return cleaned
        netloc = host if parsed.port is None else f"{host}:{parsed.port}"
        path = parsed.path or "/"
        return urlunsplit((scheme, netloc, path, parsed.query, ""))
    except Exception:
        return cleaned


def extract_all_urls(
    plain_text: str = "",
    html_body: str = "",
    qr_urls: list[tuple[str, str]] | None = None,  # list of (payload_url, provenance)
) -> list[ExtractedUrl]:
    """Extract all distinct URLs with anchor text and provenance tagging."""
    results: list[ExtractedUrl] = []
    seen: set[str] = set()

    # 1. Extract from HTML body with anchor text
    if html_body:
        try:
            soup = BeautifulSoup(html_body, "html.parser")
            for link in soup.find_all(["a", "link", "area"], href=True):
                href = link.get("href", "").strip()
                if href.startswith(("http://", "https://")):
                    norm = normalize_url(href)
                    if norm not in seen:
                        seen.add(norm)
                        host = urlsplit(norm).hostname or ""
                        anchor = link.get_text(strip=True) or None
                        results.append(ExtractedUrl(
                            raw_url=href,
                            normalized_url=norm,
                            destination_host=host,
                            provenance="html_anchor",
                            anchor_text=anchor,
                        ))
        except Exception:
            pass

    # 2. Extract from Plain-Text body with regex
    if plain_text:
        for match in URL_REGEX.finditer(plain_text):
            raw = match.group(0)
            norm = normalize_url(raw)
            if norm not in seen:
                seen.add(norm)
                host = urlsplit(norm).hostname or ""
                results.append(ExtractedUrl(
                    raw_url=raw,
                    normalized_url=norm,
                    destination_host=host,
                    provenance="body",
                    anchor_text=None,
                ))

    # 3. Add QR-derived URLs
    if qr_urls:
        for payload, prov in qr_urls:
            if payload.startswith(("http://", "https://")):
                norm = normalize_url(payload)
                if norm not in seen:
                    seen.add(norm)
                    host = urlsplit(norm).hostname or ""
                    results.append(ExtractedUrl(
                        raw_url=payload,
                        normalized_url=norm,
                        destination_host=host,
                        provenance=prov,
                        anchor_text="[QR Code Payload]",
                    ))

    return results
