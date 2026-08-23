import os

# Tests must be hermetic and never depend on whatever happens to be in the
# developer's real backend/.env (a real AI_API_KEY there would make these
# tests fire live network requests at Groq). Environment variables take
# priority over .env file values in pydantic-settings, so setting these
# before `app.main` is imported below (which instantiates Settings at
# module load time) guarantees the fallback provider is what runs in tests.
os.environ["AI_API_KEY"] = ""
os.environ["AI_PROVIDER"] = "fallback"

import io

import docx
import fitz
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """A small, real, text-extractable PDF built with PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 72),
        "This is a sample document used for backend tests. "
        "It has enough words to exercise word-count and summary logic.",
    )
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture
def sample_png_bytes() -> bytes:
    image = Image.new("RGB", (200, 80), color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def sample_jpeg_bytes() -> bytes:
    image = Image.new("RGB", (200, 80), color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def sample_docx_bytes() -> bytes:
    document = docx.Document()
    document.add_paragraph(
        "This is a sample DOCX document used for backend tests. It has enough "
        "words to exercise word-count and summary logic."
    )
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


@pytest.fixture
def sample_txt_bytes() -> bytes:
    return (
        b"This is a sample TXT document used for backend tests. "
        b"It has enough words to exercise word-count and summary logic."
    )
