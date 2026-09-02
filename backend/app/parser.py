import hashlib
import re
from dataclasses import dataclass, field
from email import policy
from email.parser import BytesParser


@dataclass(frozen=True)
class ParsedMimePart:
    part_index: int
    content_type: str
    filename: str | None
    content_id: str | None
    is_attachment: bool
    is_inline_image: bool
    byte_start: int
    byte_end: int
    sha256: str
    payload_bytes: bytes


@dataclass(frozen=True)
class ParsedEmail:
    sender: str
    subject: str
    rfc_message_id: str | None
    headers: dict[str, list[str]]
    plain_text: str
    html_body: str
    attachment_count: int
    header_ranges: dict[str, tuple[int, int]]
    body_range: tuple[int, int]
    dedupe_key: str
    mime_parts: list[ParsedMimePart] = field(default_factory=list)
    evidence_map: dict[str, list[int]] = field(default_factory=dict)


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


def _locate_payload_offsets(raw: bytes, payload_bytes: bytes, fallback_start: int, fallback_end: int) -> tuple[int, int]:
    """Locate the exact or approximate byte offset of a part payload in the raw email stream."""
    if not payload_bytes:
        return fallback_start, fallback_end
    pos = raw.find(payload_bytes)
    if pos != -1:
        return pos, pos + len(payload_bytes)
    # Search for base64 / encoded slice if needed
    digest = hashlib.sha256(payload_bytes).hexdigest()
    return fallback_start, fallback_end


def parse_email(raw: bytes) -> ParsedEmail:
    """Parse an RFC 5322 message without rejecting malformed headers or payloads."""
    message = BytesParser(policy=policy.default).parsebytes(raw)
    headers: dict[str, list[str]] = {}
    for name, value in message.items():
        headers.setdefault(name.lower(), []).append(str(value))

    text_parts: list[str] = []
    html_parts: list[str] = []
    parsed_parts: list[ParsedMimePart] = []
    attachments_count = 0
    part_index = 0

    header_ranges, body_range = _header_ranges(raw)
    evidence_map: dict[str, list[int]] = {name: list(rng) for name, rng in header_ranges.items()}
    evidence_map["body"] = list(body_range)

    for part in message.walk():
        if part.is_multipart():
            continue

        part_index += 1
        content_type = (part.get_content_type() or "application/octet-stream").lower()
        disposition = str(part.get_content_disposition() or "").lower()
        filename = part.get_filename()
        content_id = str(part.get("Content-ID") or "").strip("<>") or None

        raw_payload = part.get_payload(decode=True) or b""
        part_sha256 = hashlib.sha256(raw_payload).hexdigest()

        is_attachment = disposition == "attachment" or bool(filename)
        is_inline_image = content_type.startswith("image/") and (disposition == "inline" or bool(content_id) or not is_attachment)

        if is_attachment:
            attachments_count += 1

        # Extract text & html bodies
        if content_type == "text/plain" and not is_attachment:
            try:
                text_content = part.get_content()
            except (LookupError, UnicodeError, AttributeError):
                text_content = raw_payload.decode("utf-8", errors="replace")
            text_parts.append(text_content)
        elif content_type == "text/html" and not is_attachment:
            try:
                html_content = part.get_content()
            except (LookupError, UnicodeError, AttributeError):
                html_content = raw_payload.decode("utf-8", errors="replace")
            html_parts.append(html_content)

        part_start, part_end = _locate_payload_offsets(raw, raw_payload, body_range[0], body_range[1])
        evidence_map[f"part:{part_index}"] = [part_start, part_end]
        if filename:
            evidence_map[f"attachment:{filename}"] = [part_start, part_end]

        parsed_parts.append(ParsedMimePart(
            part_index=part_index,
            content_type=content_type,
            filename=filename,
            content_id=content_id,
            is_attachment=is_attachment,
            is_inline_image=is_inline_image,
            byte_start=part_start,
            byte_end=part_end,
            sha256=part_sha256,
            payload_bytes=raw_payload,
        ))

    plain_text = "\n".join(text_parts)
    html_body = "\n".join(html_parts)
    sender = str(message.get("From", "unknown sender"))
    subject = str(message.get("Subject", "(no subject)"))
    rfc_id = message.get("Message-ID")
    body_hash = hashlib.sha256(f"{plain_text}\n{html_body}".encode("utf-8", errors="replace")).hexdigest()
    dedupe_source = f"{rfc_id or ''}:{body_hash}".encode()

    return ParsedEmail(
        sender=sender,
        subject=subject,
        rfc_message_id=str(rfc_id) if rfc_id else None,
        headers=headers,
        plain_text=plain_text,
        html_body=html_body,
        attachment_count=attachments_count,
        header_ranges=header_ranges,
        body_range=body_range,
        dedupe_key=hashlib.sha256(dedupe_source).hexdigest(),
        mime_parts=parsed_parts,
        evidence_map=evidence_map
    )


def parse_raw_headers(headers_text: str) -> ParsedEmail:
    """Parse pasted raw email headers without a body."""
    raw = headers_text.encode("utf-8", errors="replace")
    if b"\r\n\r\n" not in raw and b"\n\n" not in raw:
        raw = raw + b"\n\n"
    return parse_email(raw)

