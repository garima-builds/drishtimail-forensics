"""M9: Safe Redirect Expander with SSRF Protection.

Follows HTTP redirect chains for shortened URLs with strict guards against
internal network scanning, RFC 1918 subnets, and cloud metadata endpoints.
"""
import ipaddress
import logging
import socket
from urllib.parse import urlsplit
import httpx

logger = logging.getLogger(__name__)

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]


def is_ssrf_risk(hostname: str) -> bool:
    """Check if a hostname resolves to a restricted private or loopback IP."""
    if not hostname:
        return True
    try:
        resolved_ips = socket.getaddrinfo(hostname, None)
        for entry in resolved_ips:
            ip_str = entry[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if any(ip_obj in net for net in BLOCKED_NETWORKS):
                return True
        return False
    except Exception:
        return True  # Block if cannot resolve safely


def expand_redirect_chain(
    url: str,
    max_hops: int = 5,
    timeout_seconds: float = 2.5,
    enabled: bool = False,
) -> list[str]:
    """Follow HTTP redirect chain if enabled, otherwise return single hop."""
    chain: list[str] = [url]
    if not enabled or not url.startswith(("http://", "https://")):
        return chain

    current_url = url
    try:
        with httpx.Client(follow_redirects=False, timeout=timeout_seconds, verify=False) as client:
            for _ in range(max_hops):
                parsed = urlsplit(current_url)
                host = parsed.hostname or ""
                if is_ssrf_risk(host):
                    break

                resp = client.head(current_url)
                if resp.is_redirect and "location" in resp.headers:
                    next_url = resp.headers["location"]
                    if not next_url.startswith(("http://", "https://")):
                        # Handle relative redirects
                        base = f"{parsed.scheme}://{parsed.netloc}"
                        next_url = f"{base.rstrip('/')}/{next_url.lstrip('/')}"
                    if next_url not in chain:
                        chain.append(next_url)
                        current_url = next_url
                    else:
                        break  # Redirect loop
                else:
                    break
    except Exception as exc:
        logger.debug("Redirect expansion stopped: %s", exc)

    return chain
