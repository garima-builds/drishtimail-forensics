import re
from typing import Any
from ..domain_utils import get_organizational_domain


def _extract_domain(email_str: str | None) -> str | None:
    if not email_str:
        return None
    match = re.search(r"@([a-zA-Z0-9.\-_]+)", email_str)
    return match.group(1).lower().rstrip(".") if match else None



def detect_header_anomalies(
    headers: dict[str, list[str]],
    hops: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Inspect headers and hops for structural or temporal anomalies."""
    anomalies: list[dict[str, Any]] = []

    from_header = headers.get("from", [""])[0]
    reply_to_header = headers.get("reply-to", [""])[0]
    return_path_header = headers.get("return-path", [""])[0]
    message_id_header = headers.get("message-id", [""])[0]

    from_domain = _extract_domain(from_header)
    reply_to_domain = _extract_domain(reply_to_header)
    return_path_domain = _extract_domain(return_path_header)

    # 1. Reply-To Divergence
    if reply_to_domain and from_domain:
        if get_organizational_domain(reply_to_domain) != get_organizational_domain(from_domain):
            anomalies.append({
                "type": "reply_to_divergence",
                "severity": "High",
                "title": "Reply-To Header Divergence",
                "description": (
                    f"Reply-To domain '{reply_to_domain}' does not match From domain '{from_domain}'. "
                    f"Responses will be routed to a different recipient organization."
                ),
                "header_name": "Reply-To",
            })

    # 2. Return-Path Divergence (Envelope vs Header Sender)
    if return_path_domain and from_domain:
        if get_organizational_domain(return_path_domain) != get_organizational_domain(from_domain):
            anomalies.append({
                "type": "return_path_divergence",
                "severity": "Medium",
                "title": "Return-Path (Envelope) Divergence",
                "description": (
                    f"Envelope Return-Path domain '{return_path_domain}' differs from Header From domain '{from_domain}'."
                ),
                "header_name": "Return-Path",
            })

    # 3. Message-ID Anomalies
    if not message_id_header:
        anomalies.append({
            "type": "missing_message_id",
            "severity": "Low",
            "title": "Missing Message-ID Header",
            "description": "The message lacks a standard RFC 5322 Message-ID header.",
            "header_name": "Message-ID",
        })
    elif not re.search(r"<.+@.+>", message_id_header):
        anomalies.append({
            "type": "malformed_message_id",
            "severity": "Low",
            "title": "Malformed Message-ID Header",
            "description": f"Message-ID '{message_id_header}' does not follow standard <id@domain> format.",
            "header_name": "Message-ID",
        })

    # 4. Relay Timing Anomalies
    negative_delays = [h for h in hops if (h.get("delay_seconds") is not None and h["delay_seconds"] < 0)]
    if negative_delays:
        anomalies.append({
            "type": "negative_hop_delay",
            "severity": "Medium",
            "title": "Impossible Relay Hop Timestamp",
            "description": "Observed negative transit time between hops, indicating skewed clock or forged timestamps.",
            "header_name": "Received",
        })

    # 5. Excessive Hop Count
    if len(hops) > 12:
        anomalies.append({
            "type": "excessive_hops",
            "severity": "Low",
            "title": "High Relay Hop Count",
            "description": f"Message traversed {len(hops)} intermediate MTAs, which may indicate complex relaying or proxying.",
            "header_name": "Received",
        })

    return anomalies
