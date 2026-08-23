from pathlib import PurePosixPath

from app.config.settings import Settings
from app.utils.errors import (
    CorruptedFileError,
    EmptyFileError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from app.utils.file_signature import EXTENSION_TO_SIGNATURE_TYPE, looks_like_text, sniff_file_type

_FRIENDLY_TYPES = "PDF, DOCX, TXT, JPG, JPEG, or PNG"


def validate_upload(filename: str, content: bytes, settings: Settings) -> str:
    """Validate an uploaded file's extension, size, and actual content.

    Returns the normalized extension (e.g. '.pdf') on success.
    Raises a `ValidationError` subclass with a user-safe message on failure.
    Never trusts the client-reported extension alone — the file's magic
    bytes must match it.
    """
    extension = PurePosixPath(filename.lower()).suffix

    if extension not in settings.allowed_extensions:
        raise UnsupportedFileTypeError(f"Please upload a {_FRIENDLY_TYPES} file.")

    if len(content) == 0:
        raise EmptyFileError("This file is empty. Please choose a different document.")

    if len(content) > settings.max_file_size:
        max_mb = settings.max_file_size / (1024 * 1024)
        raise FileTooLargeError(f"This file is larger than the {max_mb:.0f} MB limit.")

    if extension == ".txt":
        # Plain text has no magic-byte signature to sniff, unlike the other
        # accepted types - fall back to a "does this look like text" heuristic.
        if not looks_like_text(content):
            raise CorruptedFileError(
                "This doesn't look like a valid text file. It may be a renamed "
                "binary file."
            )
        return extension

    expected_type = EXTENSION_TO_SIGNATURE_TYPE[extension]
    sniffed_type = sniff_file_type(content)

    if sniffed_type != expected_type:
        raise CorruptedFileError(
            "This file doesn't look like a valid "
            f"{_FRIENDLY_TYPES} document. It may be corrupted or renamed."
        )

    return extension
