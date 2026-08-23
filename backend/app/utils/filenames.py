import re
from pathlib import PurePosixPath

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_display_filename(filename: str) -> str:
    """Strip any path components and unsafe characters, for safe display/logging/storage.

    Documents are processed entirely in memory (see document_processor.py),
    so this name is never used to build a filesystem path - only shown back
    to the user and used as an in-memory dict key.
    """
    name = PurePosixPath(filename.replace("\\", "/")).name or "document"
    name = _UNSAFE_CHARS.sub("_", name)
    return name[:255]
