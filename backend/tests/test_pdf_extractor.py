import fitz
import pytest

from app.services.pdf_extractor import extract_pdf_text, open_pdf, render_page_to_image
from app.utils.errors import CorruptedFileError


def test_open_and_extract_text_pdf(sample_pdf_bytes: bytes) -> None:
    doc = open_pdf(sample_pdf_bytes)
    content = extract_pdf_text(doc)
    doc.close()

    assert len(content.page_texts) == 1
    assert "sample document" in content.page_texts[0]
    assert content.is_likely_scanned is False


def test_detects_scanned_pdf_with_no_extractable_text() -> None:
    doc = fitz.open()
    doc.new_page()  # blank page: no text layer, simulates a scanned PDF
    blank_pdf_bytes = doc.tobytes()
    doc.close()

    reopened = open_pdf(blank_pdf_bytes)
    content = extract_pdf_text(reopened)
    reopened.close()

    assert content.is_likely_scanned is True


def test_open_pdf_rejects_non_pdf_bytes() -> None:
    with pytest.raises(CorruptedFileError):
        open_pdf(b"this is not a pdf")


def test_render_page_to_image_returns_correct_type(sample_pdf_bytes: bytes) -> None:
    doc = open_pdf(sample_pdf_bytes)
    image = render_page_to_image(doc, 0)
    doc.close()

    assert image.mode == "RGB"
    assert image.width > 0
    assert image.height > 0
