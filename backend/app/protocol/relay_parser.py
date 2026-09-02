"""M3: Relay Chain & Received Header Parser.

Reconstructs chronological hop-by-hop message transit from 'Received' headers,
computes inter-hop delays, extracts TLS cipher states, and identifies IP candidates.
"""
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any


IPV4_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
IPV6_PATTERN = re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b")
FROM_PATTERN = re.compile(r"from\s+([^\s(;]+)", re.IGNORECASE)
BY_PATTERN = re.compile(r"by\s+([^\s(;]+)", re.IGNORECASE)
TLS_PATTERN = re.compile(r"(TLSv[\d\.]+|version=TLS[^\s;]+|using\s+TLS[^\s;]+)", re.IGNORECASE)


def _extract_ip(header_line: str) -> str | None:
    # First look inside square brackets
    bracketed = re.findall(r"\[([0-9a-fA-F:.]+)\]", header_line)
    for candidate in bracketed:
        if IPV4_PATTERN.fullmatch(candidate) or IPV6_PATTERN.fullmatch(candidate):
            return candidate
    # Otherwise check anywhere in the line
    v4_match = IPV4_PATTERN.search(header_line)
    if v4_match:
        return v4_match.group(0)
    v6_match = IPV6_PATTERN.search(header_line)
    if v6_match:
        return v6_match.group(0)
    return None


def _extract_timestamp(header_line: str) -> datetime | None:
    if ";" not in header_line:
        return None
    raw_date = header_line.rsplit(";", 1)[1].strip()
    try:
        dt = parsedate_to_datetime(raw_date)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def parse_relay_chain(headers: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Parse Received headers in chronological order (earliest/sender-side first)."""
    raw_received = headers.get("received", [])
    if not raw_received:
        return []

    # RFC 5322 prepends headers at each hop, so reverse order is chronological
    chronological_raw = list(reversed(raw_received))
    hops: list[dict[str, Any]] = []
    previous_dt: datetime | None = None

    for hop_no, raw_header in enumerate(chronological_raw, start=1):
        cleaned_header = " ".join(raw_header.split())
        ip = _extract_ip(cleaned_header)
        claimed_host_match = FROM_PATTERN.search(cleaned_header)
        by_host_match = BY_PATTERN.search(cleaned_header)
        tls_match = TLS_PATTERN.search(cleaned_header)
        timestamp = _extract_timestamp(cleaned_header)

        delay_seconds: float | None = None
        if timestamp and previous_dt:
            delta = (timestamp - previous_dt).total_seconds()
            delay_seconds = max(0.0, delta)
        if timestamp:
            previous_dt = timestamp

        hops.append({
            "hop_no": hop_no,
            "raw_header": cleaned_header,
            "claimed_host": claimed_host_match.group(1) if claimed_host_match else None,
            "by_host": by_host_match.group(1) if by_host_match else None,
            "real_ip": ip,
            "rdns": None,
            "tls_version": tls_match.group(0) if tls_match else None,
            "timestamp": timestamp.isoformat() if timestamp else None,
            "delay_seconds": delay_seconds,
            "trust_status": "unverified",
        })

    return hops
