"""Modelos de datos."""

from .errors import ERROR_MAPPINGS, DownloadError, ErrorCategory, classify_error

__all__ = [
    "ERROR_MAPPINGS",
    "DownloadError",
    "ErrorCategory",
    "classify_error",
]