from PIL import Image

from app.services.ocr.preprocessing import MIN_DIMENSION_PX, preprocess_for_ocr
from app.services.ocr.tesseract_provider import TesseractOCRProvider
from app.utils.errors import OCRFailureError


def test_preprocess_converts_to_grayscale() -> None:
    image = Image.new("RGB", (500, 500), color=(200, 50, 50))
    result = preprocess_for_ocr(image)
    assert result.mode == "L"


def test_preprocess_upscales_small_images() -> None:
    image = Image.new("RGB", (100, 50), color="white")
    result = preprocess_for_ocr(image)
    assert min(result.width, result.height) >= MIN_DIMENSION_PX


def test_preprocess_leaves_large_images_unscaled() -> None:
    image = Image.new("RGB", (1500, 2000), color="white")
    result = preprocess_for_ocr(image)
    assert result.width == 1500
    assert result.height == 2000


def test_tesseract_provider_raises_friendly_error_when_binary_missing() -> None:
    # This environment doesn't have the Tesseract binary installed, which is
    # exactly the failure mode this test protects against: it must surface a
    # clean OCRFailureError, never an unhandled TesseractNotFoundError.
    provider = TesseractOCRProvider(tesseract_cmd="this-binary-does-not-exist")
    image = Image.new("RGB", (200, 80), color="white")

    try:
        provider.extract_text(image)
        raise AssertionError("Expected OCRFailureError when Tesseract binary is missing")
    except OCRFailureError as exc:
        assert "OCR is not available" in exc.message or "clearer scan" in exc.message
