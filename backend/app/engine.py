"""Offline, explainable forensic analysis used by the MVP demonstration path."""
import re
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlsplit

from .analysis import authentication_semantics, extract_urls

RISK_TERMS = ("urgent", "verify", "password", "payment", "invoice", "gift card", "suspended", "immediately", "wire transfer")
BRAND_TOKENS = ("microsoft", "google", "office", "university", "bank", "paypal")


def received_hops(headers: dict[str, list[str]]) -> list[dict]:
    hops = []
    for number, value in enumerate(reversed(headers.get("received", [])), start=1):
        ip = re.search(r"\[?(\d{1,3}(?:\.\d{1,3}){3})\]?", value)
        host = re.search(r"from\s+([^\s(]+)", value, re.IGNORECASE)
        hops.append({"hop": number, "claimed_host": host.group(1) if host else "unknown", "ip": ip.group(1) if ip else None, "trust": "unverified", "raw": value})
    if hops:
        hops[-1]["trust"] = "earliest-observed"
    return hops


def sender_lookalike(sender: str) -> list[str]:
    domain_match = re.search(r"@([^>\s]+)", sender.lower())
    if not domain_match:
        return []
    domain = domain_match.group(1)
    hits = []
    for brand in BRAND_TOKENS:
        if brand in domain and not domain.endswith((f"{brand}.com", f"{brand}.edu")):
            hits.append(f"Sender domain contains protected-brand token '{brand}' but is not its expected domain")
    if re.search(r"[0-9]|xn--", domain):
        hits.append("Sender domain contains a numeric or internationalized-domain lookalike signal")
    return hits


def analyze_message(*, sender: str, subject: str, headers: dict[str, list[str]], plain_text: str, attachment_count: int) -> dict:
    auth = authentication_semantics(headers)
    urls = [{"raw": raw, "normalized": normalized, "host": urlsplit(normalized).hostname, "provenance": "body"} for raw, normalized in extract_urls(plain_text)]
    lowered = f"{subject}\n{plain_text}".lower()
    cues = [term for term in RISK_TERMS if term in lowered]
    lookalikes = sender_lookalike(sender)
    contributions = []
    if auth.dmarc in {"fail", "softfail", "permerror", "temperror"}:
        contributions.append(("Authentication failure", 28, "Header authentication result"))
    if lookalikes:
        contributions.append(("Sender lookalike", 20, lookalikes[0]))
    if urls:
        contributions.append(("Embedded URL", min(20, 8 + 4 * len(urls)), "URL present in message body"))
    if cues:
        contributions.append(("Social-engineering language", min(18, 3 * len(cues)), f"Detected cues: {', '.join(cues)}"))
    if attachment_count:
        contributions.append(("Attachment present", min(10, 4 * attachment_count), "Static inspection pending"))
    score = min(100, sum(item[1] for item in contributions))
    verdict = "Critical" if score >= 75 else "High" if score >= 55 else "Elevated" if score >= 25 else "Low"
    conflicts = []
    if auth.dmarc == "pass" and (urls or cues or lookalikes):
        conflicts.append({"class": "authentication-versus-content", "summary": "Sender authentication passed while independent content or identity-risk signals remain present."})
    if urls and not extract_urls(subject):
        conflicts.append({"class": "link-presence", "summary": "Risk-bearing links are present in the body; inspect destination before relying on surrounding text."})
    return {
        "analysed_at": datetime.now(timezone.utc).isoformat(),
        "authentication": {"spf": auth.spf, "dkim": auth.dkim, "dmarc": auth.dmarc, "semantics_key": auth.key, "establishes": auth.establishes, "does_not_establish": auth.does_not_establish, "investigation_effect": auth.effect},
        "delivery_path": received_hops(headers),
        "origin": {"candidate_ip": next((hop["ip"] for hop in received_hops(headers) if hop["ip"]), None), "confidence": "Limited", "caveat": "No external enrichment is performed on the offline demonstration path."},
        "urls": urls,
        "attachments": {"count": attachment_count, "status": "static inspection pending" if attachment_count else "none"},
        "detections": {"social_engineering_cues": cues, "lookalike_signals": lookalikes},
        "score": {"value": score, "verdict": verdict, "confidence": "Medium" if contributions else "Low", "contributions": [{"signal": name, "points": points, "reason": reason} for name, points, reason in contributions], "disclaimer": "This score is an explainable prioritisation aid, not a determination of sender identity or malicious intent."},
        "conflicts": conflicts,
    }


def campaign_summary(analyses: list[tuple[str, dict]]) -> list[dict]:
    indicators: dict[str, list[str]] = {}
    for message_id, analysis in analyses:
        for url in analysis.get("urls", []):
            if url.get("host"):
                indicators.setdefault(f"domain:{url['host']}", []).append(message_id)
    return [{"indicator": indicator, "message_ids": ids, "sighting_count": len(ids), "confidence": "Moderate" if len(ids) > 1 else "Limited"} for indicator, ids in indicators.items()]
