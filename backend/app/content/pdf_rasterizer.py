"""M9: PDF Attachment Page Rasterizer.

Safely rasterizes PDF document pages into image buffers for static inspection
and QR-code symbol decoding using permissive libraries.
"""
import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)


def rasterize_pdf_pages(pdf_bytes: bytes, max_pages: int = 5, scale: float = 2.0) -> list[tuple[int, Image.Image]]:
    """Rasterize the first N pages of a PDF document to PIL Images.

    Returns:
        List of (page_number_1_indexed, PIL.Image)
    """
    if not pdf_bytes or not pdf_bytes.startswith(b"%PDF"):
        return []

    images: list[tuple[int, Image.Image]] = []

    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(pdf_bytes)
        num_pages = min(len(pdf), max_pages)

        for page_idx in range(num_pages):
            page = pdf[page_idx]
            pil_image = page.render(scale=scale).to_pil()
            images.append((page_idx + 1, pil_image))

        return images
    except ImportError:
        logger.debug("pypdfium2 is not installed; skipping PDF rasterization")
    except Exception as exc:
        logger.warning("Failed to rasterize PDF pages: %s", exc)

    return images
