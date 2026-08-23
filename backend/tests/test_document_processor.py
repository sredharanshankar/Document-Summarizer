import pytest

from app.config.settings import Settings
from app.services.document_processor import extract_document_text
from app.utils.errors import ProcessingError
from tests.helpers import FakeOCRProvider, blank_pdf_bytes


@pytest.fixture
def settings() -> Settings:
    return Settings(ai_api_key="", ocr_enabled=True)


def test_text_pdf_does_not_invoke_ocr(settings: Settings, sample_pdf_bytes: bytes) -> None:
    fake_ocr = FakeOCRProvider()
    pages, used_ocr = extract_document_text(sample_pdf_bytes, ".pdf", fake_ocr, settings)

    assert used_ocr is False
    assert fake_ocr.call_count == 0
    assert "sample document" in pages[0]


def test_scanned_pdf_routes_each_page_through_ocr(settings: Settings) -> None:
    fake_ocr = FakeOCRProvider()
    pages, used_ocr = extract_document_text(blank_pdf_bytes(3), ".pdf", fake_ocr, settings)

    assert used_ocr is True
    assert fake_ocr.call_count == 3
    assert pages == ["ocr extracted text"] * 3


def test_image_upload_always_uses_ocr(settings: Settings, sample_png_bytes: bytes) -> None:
    fake_ocr = FakeOCRProvider()
    pages, used_ocr = extract_document_text(sample_png_bytes, ".png", fake_ocr, settings)

    assert used_ocr is True
    assert fake_ocr.call_count == 1
    assert pages == ["ocr extracted text"]


def test_docx_upload_does_not_invoke_ocr(settings: Settings, sample_docx_bytes: bytes) -> None:
    fake_ocr = FakeOCRProvider()
    pages, used_ocr = extract_document_text(sample_docx_bytes, ".docx", fake_ocr, settings)

    assert used_ocr is False
    assert fake_ocr.call_count == 0
    assert "sample DOCX document" in pages[0]


def test_txt_upload_does_not_invoke_ocr(settings: Settings, sample_txt_bytes: bytes) -> None:
    fake_ocr = FakeOCRProvider()
    pages, used_ocr = extract_document_text(sample_txt_bytes, ".txt", fake_ocr, settings)

    assert used_ocr is False
    assert fake_ocr.call_count == 0
    assert "sample TXT document" in pages[0]


def test_scanned_pdf_with_ocr_disabled_raises(sample_pdf_bytes: bytes) -> None:
    disabled = Settings(ai_api_key="", ocr_enabled=False)
    with pytest.raises(ProcessingError):
        extract_document_text(blank_pdf_bytes(1), ".pdf", FakeOCRProvider(), disabled)


def test_image_with_ocr_disabled_raises(sample_png_bytes: bytes) -> None:
    disabled = Settings(ai_api_key="", ocr_enabled=False)
    with pytest.raises(ProcessingError):
        extract_document_text(sample_png_bytes, ".png", FakeOCRProvider(), disabled)
