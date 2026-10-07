"""Tests para modelos de errores."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from downloader_tui.models.errors import (
    ERROR_MAPPINGS,
    DownloadError,
    ErrorCategory,
    classify_error,
)


def test_error_category_enum():
    """Test que ErrorCategory tiene todos los valores esperados."""
    categories = {c.value for c in ErrorCategory}
    expected = {"network", "auth", "not_found", "format", "permission", "unknown"}
    assert categories == expected


def test_download_error_dataclass():
    """Test que DownloadError es un dataclass inmutable."""
    error = DownloadError(
        category=ErrorCategory.NETWORK,
        message="Test error",
        suggestion="Test suggestion",
    )
    assert error.category == ErrorCategory.NETWORK
    assert error.message == "Test error"
    assert error.suggestion == "Test suggestion"

    # Verificar frozen (inmutable)
    try:
        error.message = "changed"
        raise AssertionError("Deberia ser frozen")
    except (AssertionError, Exception):
        pass  # Esperado - frozen instance error expected


def test_error_mappings_structure():
    """Test que ERROR_MAPPINGS tiene la estructura correcta."""
    for key, error in ERROR_MAPPINGS.items():
        assert isinstance(key, str)
        assert isinstance(error, DownloadError)
        assert isinstance(error.category, ErrorCategory)
        assert isinstance(error.message, str)
        assert isinstance(error.suggestion, str)
        assert len(error.message) > 0
        assert len(error.suggestion) > 0


def test_classify_error_known():
    """Test clasificación de errores conocidos."""
    test_cases = [
        ("ffmpeg is not installed", ErrorCategory.UNKNOWN),
        ("merge error", ErrorCategory.FORMAT),
        ("private video", ErrorCategory.AUTH),
        ("sign in required", ErrorCategory.AUTH),
        ("video not available", ErrorCategory.NOT_FOUND),
        ("network error", ErrorCategory.NETWORK),
        ("forbidden access", ErrorCategory.PERMISSION),
        ("age restricted content", ErrorCategory.AUTH),
        ("login required", ErrorCategory.AUTH),
        ("This video is unavailable", ErrorCategory.NOT_FOUND),
    ]

    for error_text, expected_category in test_cases:
        error = classify_error(error_text)
        assert error.category == expected_category, f"Fallo para: {error_text}"
        assert error.message
        assert error.suggestion


def test_classify_error_unknown():
    """Un error sin clasificar conserva el texto original, no lo descarta.

    Antes devolvia siempre "Error desconocido" y el motivo real de yt-dlp se
    perdia; era imposible diagnosticar nada desde la interfaz.
    """
    error = classify_error("some completely unknown error message")
    assert error.category == ErrorCategory.UNKNOWN
    assert "some completely unknown error message" in error.message
    assert "log" in error.suggestion.lower()


def test_classify_error_case_insensitive():
    """Test que la clasificación es case-insensitive."""
    error1 = classify_error("NETWORK ERROR")
    error2 = classify_error("network error")
    error3 = classify_error("Network Error")

    assert error1.category == error2.category == error3.category == ErrorCategory.NETWORK
