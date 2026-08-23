from abc import ABC, abstractmethod

from PIL import Image


class OCRProvider(ABC):
    """Abstraction over an OCR backend.

    Kept separate from TesseractOCRProvider so Tesseract can be swapped for
    a hosted OCR API later (e.g. if a deployment target can't install the
    Tesseract system binary) without touching any calling code.
    """

    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        """Return the text found in `image`. Raises OCRFailureError on failure."""
