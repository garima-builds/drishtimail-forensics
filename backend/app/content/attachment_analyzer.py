"""M9: Static Attachment Analyzer.

Inspects attachment payloads using static magic-byte verification, extension-mismatch detection,
and macro indicator regexes. Never executes files.
"""
import hashlib
import re
from dataclasses import dataclass
from typing import Any

MAGIC_SIGNATURES = [
    (b"%PDF", "application/pdf"),
    (b"MZ", "application/x-dosexec"),
    (b"\x7fELF", "application/x-elf"),
    (b"PK\x03\x04", "application/zip"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "application/x-ole-storage"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"RIFF", "image/webp"),
]

DANGEROUS_EXTENSIONS = {
    ".exe", ".dll", ".scr", ".bat", ".cmd", ".vbs", ".vbe", ".js", ".jse",
    ".wsf", ".wsh", ".ps1", ".hta", ".iso", ".img", ".lnk", ".cpl", ".jar"
}

MACRO_PATTERNS = [
    re.compile(b"vbaProject\\.bin", re.IGNORECASE),
    re.compile(b"AutoOpen", re.IGNORECASE),
    re.compile(b"Workbook_Open", re.IGNORECASE),
    re.compile(b"Shell\\(", re.IGNORECASE),
    re.compile(b"WScript\\.Shell", re.IGNORECASE),
    re.compile(b"powershell", re.IGNORECASE),
]


def detect_true_mime(payload_bytes: bytes) -> str:
    """Identify true MIME type from file header magic bytes."""
    if not payload_bytes:
        return "application/octet-stream"
    for magic, mime in MAGIC_SIGNATURES:
        if payload_bytes.startswith(magic):
            return mime
    # Check for text/plain
    try:
        payload_bytes[:512].decode("utf-8")
        return "text/plain"
    except UnicodeError:
        pass
    return "application/octet-stream"


def analyze_attachment_static(
    filename: str,
    declared_mime: str | None,
    payload_bytes: bytes,
) -> dict[str, Any]:
    """Perform static inspection of attachment metadata and binary content."""
    filename_lower = filename.lower() if filename else "unnamed_attachment"
    true_mime = detect_true_mime(payload_bytes)
    digest = hashlib.sha256(payload_bytes).hexdigest()
    indicators: list[dict[str, Any]] = []

    # 1. Dangerous Extension Check
    has_dangerous_ext = any(filename_lower.endswith(ext) for ext in DANGEROUS_EXTENSIONS)
    if has_dangerous_ext:
        indicators.append({
            "type": "dangerous_extension",
            "severity": "Critical",
            "description": f"Attachment uses high-risk executable or script extension: '{filename}'.",
        })

    # 2. Magic Byte Extension Mismatch
    if true_mime == "application/x-dosexec" and not filename_lower.endswith((".exe", ".dll")):
        indicators.append({
            "type": "disguised_executable",
            "severity": "Critical",
            "description": (
                f"Attachment '{filename}' contains executable (MZ) binary headers but is disguised with a non-executable extension."
            ),
        })
    elif true_mime == "application/pdf" and not filename_lower.endswith(".pdf"):
        indicators.append({
            "type": "extension_mismatch",
            "severity": "Low",
            "description": f"File '{filename}' contains PDF format header.",
        })

    # 3. Macro & Script Detection in Office/ZIP Archives
    if true_mime in {"application/zip", "application/x-ole-storage"} or filename_lower.endswith((".docm", ".xlsm", ".pptm", ".doc", ".xls")):
        found_macros = []
        for pat in MACRO_PATTERNS:
            if pat.search(payload_bytes):
                found_macros.append(pat.pattern.decode(errors="ignore"))
        if found_macros:
            indicators.append({
                "type": "embedded_macro",
                "severity": "High",
                "description": f"Document contains embedded VBA macro or script triggers: {', '.join(found_macros)}",
            })

    return {
        "filename": filename,
        "declared_mime": declared_mime,
        "true_mime": true_mime,
        "byte_size": len(payload_bytes),
        "sha256": digest,
        "static_indicators": indicators,
        "is_suspicious": any(ind["severity"] in {"High", "Critical"} for ind in indicators),
    }
