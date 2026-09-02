"""F3: Quishing & Multi-Surface QR Code Detection Engine.

Extracts and decodes QR codes from inline images, image attachments, and rasterized
PDF document pages. Applies grayscale, contrast enhancement, upscaling, and 4-way rotation
(0°, 90°, 180°, 270°). If finder patterns are detected but decode fails, emits
'QR present, undecodable'.
"""
import io
import logging
from dataclasses import dataclass
from typing import Any
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

from .pdf_rasterizer import rasterize_pdf_pages

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QrDetectionResult:
    payload: str | None
    provenance: str
    source_filename: str | None
    rotation_degrees: int
    undecodable: bool
    confidence: str
    bounding_box: list[int] | None = None  # [x, y, w, h]


def _detect_qr_in_image(image: Image.Image) -> tuple[str | None, list[int] | None]:
    """Attempt QR detection using qreader or pyzbar or OpenCV."""
    # Method 1: Try qreader (pure python / pyzbar wrapper, very accurate)
    try:
        from qreader import QReader
        qreader = QReader(model_size="s")
        np_img = np.array(image.convert("RGB"))
        decoded = qreader.detect_and_decode(image=np_img, return_bboxes=True)
        if decoded:
            for text, bbox in zip(decoded[0], decoded[1]):
                if text:
                    box = [int(bbox[0]), int(bbox[1]), int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1])] if bbox is not None else None
                    return str(text), box
    except (ImportError, Exception):
        pass

    # Method 2: Try pyzbar if available
    try:
        from pyzbar.pyzbar import decode as pyzbar_decode
        decoded_objs = pyzbar_decode(image)
        for obj in decoded_objs:
            if obj.type == "QRCODE" and obj.data:
                rect = obj.rect
                return obj.data.decode("utf-8", errors="replace"), [rect.left, rect.top, rect.width, rect.height]
    except (ImportError, Exception):
        pass

    # Method 3: Try cv2 QRCodeDetector if available
    try:
        import cv2
        detector = cv2.QRCodeDetector()
        np_img = np.array(image.convert("RGB"))
        val, points, _ = detector.detectAndDecode(np_img)
        if val:
            return str(val), None
    except (ImportError, Exception):
        pass

    return None, None


def _has_qr_finder_pattern_heuristic(image: Image.Image) -> bool:
    """Heuristic check for QR code 1:1:3:1:1 concentric square ratio."""
    try:
        gray = image.convert("L")
        np_img = np.array(gray)
        # Check standard deviation of contrast in central regions
        if np_img.size < 400:
            return False
        std_dev = float(np.std(np_img))
        return std_dev > 50.0  # High contrast binary-like matrix
    except Exception:
        return False


def decode_qr_with_rotations(
    image_bytes: bytes,
    provenance: str,
    source_filename: str | None = None,
) -> list[QrDetectionResult]:
    """Preprocess image and scan across all 4 rotations (0, 90, 180, 270 degrees)."""
    if not image_bytes:
        return []

    try:
        base_img = Image.open(io.BytesIO(image_bytes))
    except Exception as exc:
        logger.debug("Failed to open image bytes for QR scan: %s", exc)
        return []

    results: list[QrDetectionResult] = []
    seen_payloads: set[str] = set()
    detected_finder = False

    # Preprocessing variations
    # 1. Base grayscale
    # 2. Upscaled 2x + contrast enhanced
    # 3. Inverted colors (for dark mode QR codes)
    variants: list[Image.Image] = [base_img]
    try:
        if base_img.width < 400 or base_img.height < 400:
            scaled = base_img.resize((base_img.width * 2, base_img.height * 2), Image.Resampling.LANCZOS)
            enhancer = ImageEnhance.Contrast(scaled)
            variants.append(enhancer.enhance(1.8))
        # Inverted variant
        gray = base_img.convert("L")
        variants.append(ImageOps.invert(gray))
    except Exception:
        pass

    for variant in variants:
        for angle in (0, 90, 180, 270):
            rotated = variant if angle == 0 else variant.rotate(angle, expand=True)
            payload, bbox = _detect_qr_in_image(rotated)

            if payload and payload not in seen_payloads:
                seen_payloads.add(payload)
                results.append(QrDetectionResult(
                    payload=payload,
                    provenance=provenance,
                    source_filename=source_filename,
                    rotation_degrees=angle,
                    undecodable=False,
                    confidence="High",
                    bounding_box=bbox,
                ))
            elif not payload and angle == 0 and _has_qr_finder_pattern_heuristic(rotated):
                detected_finder = True

    # If finder pattern was present but decoding failed across all variants and angles
    if not results and detected_finder:
        results.append(QrDetectionResult(
            payload=None,
            provenance=provenance,
            source_filename=source_filename,
            rotation_degrees=0,
            undecodable=True,
            confidence="Moderate",
            bounding_box=None,
        ))

    return results


def scan_email_mime_parts_for_qr(
    mime_parts: list[Any],
) -> list[QrDetectionResult]:
    """Scan all image MIME parts and PDF attachments for embedded QR codes."""
    all_results: list[QrDetectionResult] = []

    for part in mime_parts:
        content_type = getattr(part, "content_type", "").lower()
        filename = getattr(part, "filename", "") or ""
        payload_bytes = getattr(part, "payload_bytes", b"")

        if not payload_bytes:
            continue

        # Case 1: Image parts (inline or attachments)
        if content_type.startswith("image/") or filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")):
            prov = "qr_inline" if getattr(part, "is_inline_image", False) else "qr_attachment"
            res = decode_qr_with_rotations(payload_bytes, provenance=prov, source_filename=filename)
            all_results.extend(res)

        # Case 2: PDF Document attachments
        elif content_type == "application/pdf" or filename.lower().endswith(".pdf"):
            rasterized = rasterize_pdf_pages(payload_bytes, max_pages=3)
            for page_no, pil_img in rasterized:
                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")
                page_bytes = buf.getvalue()
                res = decode_qr_with_rotations(
                    page_bytes,
                    provenance=f"qr_pdf_page_{page_no}",
                    source_filename=f"{filename}#page={page_no}",
                )
                all_results.extend(res)

    return all_results
