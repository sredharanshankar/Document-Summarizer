"""PDF text extraction using PyMuPDF (fitz).

Text is extracted per-page. If a PDF's average extractable text per page is
too low, it's treated as a scanned document and the caller should route its
rendered page images through OCR instead (see document_processor.py).
"""

from __future__ import annotations

from dataclasses import dataclass

import fitz  # PyMuPDF
from PIL import Image

from app.utils.errors import CorruptedFileError

# Below this average character count per page, a PDF is assumed to be a
# scan (image-only) rather than a text PDF, and gets routed through OCR.
SCANNED_PDF_CHAR_THRESHOLD = 20

# Resolution used when rasterizing pages for OCR - high enough for decent
# OCR accuracy without producing enormous images for large page counts.
OCR_RENDER_DPI = 200


@dataclass
class PdfContent:
    page_texts: list[str]
    is_likely_scanned: bool


def open_pdf(content: bytes) -> fitz.Document:
    try:
        doc = fitz.open(stream=content, filetype="pdf")
    except Exception as exc:  # PyMuPDF raises its own RuntimeError/ValueError subclasses
        raise CorruptedFileError(
            "This PDF could not be opened. It may be corrupted."
        ) from exc

    if doc.needs_pass:
        doc.close()
        raise CorruptedFileError("This PDF is password-protected and cannot be processed.")

    if doc.page_count == 0:
        doc.close()
        raise CorruptedFileError("This PDF has no pages.")

    return doc


def extract_pdf_text(doc: fitz.Document) -> PdfContent:
    page_texts = [page.get_text() for page in doc]
    total_chars = sum(len(text.strip()) for text in page_texts)
    avg_chars_per_page = total_chars / max(len(page_texts), 1)

    return PdfContent(
        page_texts=page_texts,
        is_likely_scanned=avg_chars_per_page < SCANNED_PDF_CHAR_THRESHOLD,
    )


def render_page_to_image(doc: fitz.Document, page_index: int) -> Image.Image:
    page = doc[page_index]
    zoom = OCR_RENDER_DPI / 72  # PDF points are 1/72 inch; fitz's default is 72 DPI
    pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
