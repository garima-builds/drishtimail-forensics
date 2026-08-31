import hashlib
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser


@dataclass(frozen=True)
class ParsedEmail:
    sender: str
    subject: str
    rfc_message_id: str | None
    headers: dict[str, list[str]]
    plain_text: str
    attachment_count: int
    header_ranges: dict[str, tuple[int, int]]
    body_range: tuple[int, int]
    dedupe_key: str


def _header_ranges(raw: bytes) -> tuple[dict[str, tuple[int, int]], tuple[int, int]]:
    separator = b"\r\n\r\n" if b"\r\n\r\n" in raw else b"\n\n"
    header_block, _, _ = raw.partition(separator)
    body_start = len(header_block) + len(separator)
    ranges: dict[str, tuple[int, int]] = {}
    cursor = 0
    for line in header_block.splitlines(keepends=True):
        if line[:1] not in (b" ", b"\t") and b":" in line:
            name = line.split(b":", 1)[0].decode("ascii", errors="replace").lower()
            ranges.setdefault(name, (cursor, cursor + len(line)))
        cursor += len(line)
    return ranges, (body_start, len(raw))


def parse_email(raw: bytes) -> ParsedEmail:
    """Parse an RFC 5322 message without rejecting malformed headers or payloads."""
    message = BytesParser(policy=policy.default).parsebytes(raw)
    headers: dict[str, list[str]] = {}
    for name, value in message.items():
        headers.setdefault(name.lower(), []).append(str(value))
    text_parts: list[str] = []
    attachments = 0
    for part in message.walk():
        if part.is_multipart():
            continue
        disposition = part.get_content_disposition()
        if disposition == "attachment" or part.get_filename():
            attachments += 1
            continue
        if part.get_content_type() == "text/plain":
            try:
                text_parts.append(part.get_content())
            except (LookupError, UnicodeError):
                payload = part.get_payload(decode=True) or b""
                text_parts.append(payload.decode("utf-8", errors="replace"))
    plain_text = "\n".join(text_parts)
    sender = str(message.get("From", "unknown sender"))
    subject = str(message.get("Subject", "(no subject)"))
    rfc_id = message.get("Message-ID")
    body_hash = hashlib.sha256(plain_text.encode("utf-8", errors="replace")).hexdigest()
    dedupe_source = f"{rfc_id or ''}:{body_hash}".encode()
    ranges, body_range = _header_ranges(raw)
    return ParsedEmail(sender=sender, subject=subject, rfc_message_id=str(rfc_id) if rfc_id else None, headers=headers, plain_text=plain_text, attachment_count=attachments, header_ranges=ranges, body_range=body_range, dedupe_key=hashlib.sha256(dedupe_source).hexdigest())
