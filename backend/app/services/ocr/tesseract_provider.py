import logging

import pytesseract
from PIL import Image

from app.services.ocr.base import OCRProvider
from app.services.ocr.preprocessing import preprocess_for_ocr
from app.utils.errors import OCRFailureError

logger = logging.getLogger("document_summary_assistant")


class TesseractOCRProvider(OCRProvider):
    def __init__(self, tesseract_cmd: str | None = None) -> None:
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image: Image.Image) -> str:
        try:
            preprocessed = preprocess_for_ocr(image)
            return pytesseract.image_to_string(preprocessed)
        except pytesseract.TesseractNotFoundError as exc:
            logger.error("Tesseract binary not found: %s", exc)
            raise OCRFailureError(
                "OCR is not available on this server right now. "
                "Please try a document with selectable text instead of a scanned image."
            ) from exc
        except Exception as exc:
            logger.exception("OCR failed")
            raise OCRFailureError(
                "We couldn't read text from this image. Please try a clearer scan or photo."
            ) from exc
