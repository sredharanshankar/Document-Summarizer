import pytest

from app.config.settings import Settings
from app.utils.errors import (
    CorruptedFileError,
    EmptyFileError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from app.utils.file_signature import sniff_file_type
from app.utils.filenames import sanitize_display_filename
from app.utils.validation import validate_upload


@pytest.fixture
def settings() -> Settings:
    return Settings(ai_api_key="", max_file_size=1024 * 1024)


def test_accepts_valid_pdf(settings: Settings, sample_pdf_bytes: bytes) -> None:
    assert validate_upload("report.pdf", sample_pdf_bytes, settings) == ".pdf"


def test_accepts_valid_png(settings: Settings, sample_png_bytes: bytes) -> None:
    assert validate_upload("scan.png", sample_png_bytes, settings) == ".png"


def test_accepts_valid_docx(settings: Settings, sample_docx_bytes: bytes) -> None:
    assert validate_upload("report.docx", sample_docx_bytes, settings) == ".docx"


def test_accepts_valid_txt(settings: Settings, sample_txt_bytes: bytes) -> None:
    assert validate_upload("notes.txt", sample_txt_bytes, settings) == ".txt"


def test_rejects_binary_content_renamed_as_txt(settings: Settings, sample_png_bytes: bytes) -> None:
    with pytest.raises(CorruptedFileError):
        validate_upload("renamed.txt", sample_png_bytes, settings)


def test_rejects_renamed_image_as_docx(settings: Settings, sample_png_bytes: bytes) -> None:
    with pytest.raises(CorruptedFileError):
        validate_upload("renamed.docx", sample_png_bytes, settings)


def test_rejects_unsupported_extension(settings: Settings) -> None:
    with pytest.raises(UnsupportedFileTypeError):
        validate_upload("notes.exe", b"anything", settings)


def test_rejects_empty_file(settings: Settings) -> None:
    with pytest.raises(EmptyFileError):
        validate_upload("report.pdf", b"", settings)


def test_rejects_oversized_file(settings: Settings, sample_pdf_bytes: bytes) -> None:
    tiny_settings = Settings(ai_api_key="", max_file_size=10)
    with pytest.raises(FileTooLargeError):
        validate_upload("report.pdf", sample_pdf_bytes, tiny_settings)


def test_rejects_content_that_does_not_match_extension(settings: Settings) -> None:
    # A .pdf extension on content that is actually plain text should be
    # caught by magic-byte sniffing, not trusted from the filename alone.
    with pytest.raises(CorruptedFileError):
        validate_upload("fake.pdf", b"not really a pdf", settings)


def test_rejects_renamed_image_as_pdf(settings: Settings, sample_png_bytes: bytes) -> None:
    with pytest.raises(CorruptedFileError):
        validate_upload("renamed.pdf", sample_png_bytes, settings)


def test_sniff_file_type_unknown_returns_none() -> None:
    assert sniff_file_type(b"random bytes") is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("report.pdf", "report.pdf"),
        ("../../etc/passwd", "passwd"),
        ("..\\..\\windows\\system32\\evil.exe", "evil.exe"),
        ("my file (final) v2.pdf", "my_file_final_v2.pdf"),
    ],
)
def test_sanitize_display_filename(raw: str, expected: str) -> None:
    assert sanitize_display_filename(raw) == expected
