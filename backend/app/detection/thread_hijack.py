"""M2: Thread Hijack & Reply-Chain Spoofing Detector.

Detects fake conversation continuations where subject lines start with 'Re:' or 'Fwd:'
without corresponding In-Reply-To or References threading headers.
"""
import re
from typing import Any


def detect_thread_hijack(
    subject: str,
    headers: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """Check if a message claims to be part of an existing thread without RFC threading headers."""
    findings: list[dict[str, Any]] = []

    subj_clean = (subject or "").strip()
    is_reply_subject = bool(re.match(r"^(?:re|fwd|fw)\s*:\s*", subj_clean, re.IGNORECASE))

    if not is_reply_subject:
        return []

    in_reply_to = headers.get("in-reply-to", [])
    references = headers.get("references", [])

    if not in_reply_to and not references:
        findings.append({
            "type": "unthreaded_reply_subject",
            "severity": "High",
            "title": "Suspected Conversation Thread Hijack",
            "subject": subj_clean,
            "description": (
                f"Subject line starts with a reply prefix ('{subj_clean[:6]}') but lacks standard "
                f"RFC 5322 'In-Reply-To' or 'References' headers. Often used to induce trust by mimicking an ongoing thread."
            ),
        })

    return findings
