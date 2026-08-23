"""DOCX text extraction using python-docx."""

from __future__ import annotations

import io

import docx

from app.utils.errors import CorruptedFileError


def extract_docx_text(content: bytes) -> str:
    try:
        document = docx.Document(io.BytesIO(content))
    except Exception as exc:  # python-docx raises assorted errors for a non-docx zip
        raise CorruptedFileError(
            "This DOCX file could not be read. It may be corrupted."
        ) from exc

    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)
