"""M3 / M4: Trust Boundary Resolver.

Determines the earliest reliable transit node in the relay chain by evaluating
which receiving MTAs belong to the institution's trusted mail perimeter.
Hops outside the perimeter cannot be cryptographically trusted unless authenticated.
"""
import ipaddress
from typing import Any


def is_private_or_loopback_ip(ip_str: str | None) -> bool:
    if not ip_str:
        return False
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local
    except ValueError:
        return False


def resolve_trust_boundary(
    hops: list[dict[str, Any]],
    trusted_mta_hosts: list[str] | None = None,
    trusted_mta_subnets: list[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Annotate relay hops with trust statuses and select the earliest reliable originating node.

    Returns:
        (annotated_hops, earliest_reliable_summary)
    """
    if not hops:
        return [], {
            "candidate_ip": None,
            "hop_no": None,
            "justification": "No Received headers were found in the message.",
            "confidence": "Limited",
        }

    trusted_hosts = set(h.lower().strip() for h in (trusted_mta_hosts or []))
    trusted_nets = []
    for s in (trusted_mta_subnets or []):
        try:
            trusted_nets.append(ipaddress.ip_network(s.strip()))
        except ValueError:
            pass

    annotated = [dict(h) for h in hops]
    earliest_reliable_idx: int | None = None
    earliest_reliable_ip: str | None = None
    justification = ""

    # Search backwards from the destination (last hop is the final institutional recipient)
    # The first external hop observed by a trusted internal node is the earliest reliable point.
    found_trusted_boundary = False

    for idx in range(len(annotated) - 1, -1, -1):
        hop = annotated[idx]
        by_host = (hop.get("by_host") or "").lower()
        ip_str = hop.get("real_ip")

        is_internal_host = any(th in by_host for th in trusted_hosts) if trusted_hosts else False
        is_internal_ip = False
        if ip_str:
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                is_internal_ip = any(ip_obj in net for net in trusted_nets)
            except ValueError:
                pass

        if is_internal_host or is_internal_ip:
            hop["trust_status"] = "verified_internal"
            found_trusted_boundary = True
        elif found_trusted_boundary or (idx == 0):
            # This is the boundary node receiving from the outside Internet
            hop["trust_status"] = "earliest_reliable"
            earliest_reliable_idx = idx
            earliest_reliable_ip = hop.get("real_ip")
            justification = (
                f"Hop #{hop['hop_no']} represents the first ingress point recorded by the receiving "
                f"institution's border MTA ('{hop.get('by_host') or 'border mail gateway'}'). "
                f"Upstream headers before this hop were generated outside institutional control and are marked unverified."
            )
            break

    # If no specific internal MTA list was matched, default to the earliest public IP
    if earliest_reliable_ip is None:
        for idx, hop in enumerate(annotated):
            ip_str = hop.get("real_ip")
            if ip_str and not is_private_or_loopback_ip(ip_str):
                hop["trust_status"] = "earliest_reliable"
                earliest_reliable_idx = idx
                earliest_reliable_ip = ip_str
                justification = (
                    f"Hop #{hop['hop_no']} is the earliest observable public IP address ({ip_str}) "
                    f"in the delivery chain."
                )
                break

    # If still none found, select the first hop
    if earliest_reliable_ip is None and annotated:
        annotated[0]["trust_status"] = "earliest_reliable"
        earliest_reliable_idx = 0
        earliest_reliable_ip = annotated[0].get("real_ip")
        justification = "Hop #1 was selected as the sole candidate origin node."

    # Mark everything preceding the earliest reliable hop as unverified
    if earliest_reliable_idx is not None:
        for i in range(0, earliest_reliable_idx):
            annotated[i]["trust_status"] = "unverified"

    return annotated, {
        "candidate_ip": earliest_reliable_ip,
        "hop_no": annotated[earliest_reliable_idx]["hop_no"] if earliest_reliable_idx is not None else None,
        "justification": justification,
        "confidence": "Moderate" if earliest_reliable_ip else "Limited",
        "caveat": "Approximate infrastructure traceability based on relay headers; does not assert attacker physical location.",
    }
