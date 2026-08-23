"""Magic-byte sniffing for the small, fixed set of file types this app accepts.

Deliberately hand-rolled instead of a dependency like `python-magic`: it
needs the system libmagic library, which complicates local Windows setup
and container builds for no benefit given we only need to recognize a
handful of signatures.
"""

from __future__ import annotations

_PDF = b"%PDF-"
_JPEG = b"\xff\xd8\xff"
_PNG = b"\x89PNG\r\n\x1a\n"
# .docx is a ZIP archive internally - this is the same signature every
# ZIP-based format shares (xlsx, pptx, plain .zip), so it can't fully
# distinguish "genuine docx" from "some other zip renamed to .docx" on
# magic bytes alone. python-docx raising on a non-docx zip at extraction
# time is the actual validation backstop for that case.
_DOCX = b"PK\x03\x04"

# Maps a sniffed signature to the extensions it's valid for.
_SIGNATURES: list[tuple[bytes, str]] = [
    (_PDF, "pdf"),
    (_JPEG, "jpeg"),
    (_PNG, "png"),
    (_DOCX, "docx"),
]


def sniff_file_type(content: bytes) -> str | None:
    """Return 'pdf' | 'jpeg' | 'png' | 'docx' based on the file's magic bytes, or None."""
    for signature, file_type in _SIGNATURES:
        if content.startswith(signature):
            return file_type
    return None


def looks_like_text(content: bytes) -> bool:
    """Loose "is this plausibly a text file" check for .txt uploads.

    Plain text has no magic-byte signature, so this is a heuristic instead:
    reject anything containing null bytes (a strong binary-file signal) and
    require it to be decodable. latin-1 decoding never actually fails
    (every byte maps to a codepoint), so in practice this mainly filters
    out null-byte-containing binary files - intentionally simple.
    """
    sample = content[:8000]
    if b"\x00" in sample:
        return False
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            content.decode("latin-1")
        except UnicodeDecodeError:
            return False
    return True


EXTENSION_TO_SIGNATURE_TYPE = {
    ".pdf": "pdf",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".png": "png",
    ".docx": "docx",
}
