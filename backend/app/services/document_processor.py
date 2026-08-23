"""Document -> raw per-page text: type detection and PDF/OCR extraction.

Pure extraction logic only - text cleaning lives in text_cleaner.py, and
the full job orchestration (stage transitions, error handling, calling
into SummaryService) lives in pipeline.py.
"""

from __future__ import annotations

import io
from collections.abc import Callable

from PIL import Image

from app.config.settings import Settings
from app.models.schemas import JobStage
from app.services.docx_extractor import extract_docx_text
from app.services.ocr.base import OCRProvider
from app.services.ocr.tesseract_provider import TesseractOCRProvider
from app.services.pdf_extractor import extract_pdf_text, open_pdf, render_page_to_image
from app.utils.errors import ProcessingError

StageCallback = Callable[[JobStage], None]


def get_default_ocr_provider(settings: Settings) -> OCRProvider:
    return TesseractOCRProvider(tesseract_cmd=settings.tesseract_cmd)


def extract_document_text(
    content: bytes,
    extension: str,
    ocr_provider: OCRProvider,
    settings: Settings,
    on_stage: StageCallback | None = None,
) -> tuple[list[str], bool]:
    """Returns (per_page_text, used_ocr)."""

    if extension == ".pdf":
        doc = open_pdf(content)
        try:
            pdf_content = extract_pdf_text(doc)
            if not pdf_content.is_likely_scanned:
                return pdf_content.page_texts, False

            if not settings.ocr_enabled:
                raise ProcessingError(
                    "This PDF appears to be scanned, and OCR is currently disabled "
                    "on this server. Please try a PDF with selectable text."
                )

            if on_stage:
                on_stage(JobStage.OCR)

            return [
                ocr_provider.extract_text(render_page_to_image(doc, i))
                for i in range(doc.page_count)
            ], True
        finally:
            doc.close()

    if extension == ".docx":
        return [extract_docx_text(content)], False

    if extension == ".txt":
        return [_decode_text_file(content)], False

    # Image upload (.jpg/.jpeg/.png) always goes through OCR.
    if not settings.ocr_enabled:
        raise ProcessingError("OCR is currently disabled on this server, so image uploads can't be processed.")

    if on_stage:
        on_stage(JobStage.OCR)

    image = Image.open(io.BytesIO(content))
    return [ocr_provider.extract_text(image)], True


def _decode_text_file(content: bytes) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")
