"""Application-specific exceptions.

Each maps to a specific HTTP status code and a user-safe message via the
handlers registered in `app.main`. Never let a raw exception's message or
traceback reach the client — catch it, log it, and raise (or let bubble)
one of these instead.
"""

from __future__ import annotations


class AppError(Exception):
    """Base class for all handled application errors."""

    status_code: int = 500
    error: str = "internal_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    status_code = 400
    error = "validation_error"


class UnsupportedFileTypeError(ValidationError):
    error = "unsupported_file_type"


class FileTooLargeError(ValidationError):
    error = "file_too_large"


class EmptyFileError(ValidationError):
    error = "empty_file"


class CorruptedFileError(ValidationError):
    error = "corrupted_file"


class ProcessingError(AppError):
    status_code = 422
    error = "processing_error"


class OCRFailureError(ProcessingError):
    error = "ocr_failure"


class EmptyTextError(ProcessingError):
    error = "empty_text"


class AIProviderError(AppError):
    status_code = 502
    error = "ai_provider_error"


class AITimeoutError(AppError):
    status_code = 504
    error = "ai_timeout"


class AIRateLimitError(AppError):
    status_code = 429
    error = "ai_rate_limit"


class NotFoundError(AppError):
    status_code = 404
    error = "not_found"
