"""M5: Indicator of Compromise (IOC) Extractor.

Extracts typed indicators (IPs, domains, URLs, file hashes, sender identities,
structural skeleton hashes) for correlation, graphing, and threat-sharing export.
"""
from dataclasses import dataclass
from typing import Any
import tldextract


@dataclass(frozen=True)
class ExtractedIndicator:
    indicator_type: str  # 'ip', 'domain', 'url', 'file_hash', 'structural_hash', 'sender_email'
    value: str
    provenance: str


def extract_all_iocs(
    *,
    sender: str,
    headers: dict[str, list[str]],
    origin_ip: str | None,
    relay_hops: list[dict[str, Any]],
    urls: list[dict[str, Any]],
    attachments: list[dict[str, Any]],
    structural_hash: str | None,
) -> list[ExtractedIndicator]:
    """Extract distinct typed indicators from all message components."""
    iocs: list[ExtractedIndicator] = []
    seen: set[tuple[str, str]] = set()

    def add(t: str, val: str | None, prov: str):
        if not val:
            return
        v = val.strip().lower()
        if (t, v) not in seen:
            seen.add((t, v))
            iocs.append(ExtractedIndicator(indicator_type=t, value=v, provenance=prov))

    # 1. Sender email and domain
    if "@" in sender:
        clean_email = sender.split("<")[-1].strip(">").strip()
        add("sender_email", clean_email, "from_header")
        domain = clean_email.split("@")[-1]
        add("domain", domain, "sender_domain")

    # 2. Reply-To and Return-Path
    reply_to = headers.get("reply-to", [""])[0]
    if "@" in reply_to:
        clean_reply = reply_to.split("<")[-1].strip(">").strip()
        add("sender_email", clean_reply, "reply_to_header")
        add("domain", clean_reply.split("@")[-1], "reply_to_domain")

    # 3. Origin IP & Relay IPs
    if origin_ip:
        add("ip", origin_ip, "origin_ip")
    for hop in relay_hops:
        hop_ip = hop.get("real_ip")
        if hop_ip and hop_ip != origin_ip:
            add("ip", hop_ip, f"relay_hop_{hop.get('hop_no')}")

    # 4. URLs and destination hosts
    for u in urls:
        norm_url = u.get("normalized_url")
        dest_host = u.get("destination_host")
        prov = u.get("provenance", "body")
        if norm_url:
            add("url", norm_url, prov)
        if dest_host:
            add("domain", dest_host, f"{prov}_host")

    # 5. Attachment file hashes
    for att in attachments:
        sha = att.get("sha256")
        if sha:
            add("file_hash", sha, f"attachment:{att.get('filename')}")

    # 6. Structural HTML signature
    if structural_hash:
        add("structural_hash", structural_hash, "html_skeleton")

    return iocs
