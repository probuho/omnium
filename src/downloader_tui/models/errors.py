"""Modelos de errores y clasificacion."""

import re
from dataclasses import dataclass
from enum import Enum


class ErrorCategory(Enum):
    NETWORK = "network"
    AUTH = "auth"
    NOT_FOUND = "not_found"
    FORMAT = "format"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DownloadError:
    category: ErrorCategory
    message: str
    suggestion: str


ERROR_MAPPINGS: dict[str, DownloadError] = {
    "ffmpeg is not installed": DownloadError(
        ErrorCategory.UNKNOWN,
        "FFmpeg no encontrado",
        "Verifica que ffmpeg.exe este en la carpeta del proyecto",
    ),
    "merge": DownloadError(
        ErrorCategory.FORMAT,
        "Error al fusionar video/audio",
        "Intenta con otra calidad o formato",
    ),
    "private video": DownloadError(
        ErrorCategory.AUTH,
        "Video privado o restringido",
        "Verifica que tus cookies esten actualizadas",
    ),
    "sign in": DownloadError(
        ErrorCategory.AUTH,
        "Requiere autenticacion",
        "Exporta cookies actualizadas desde tu navegador",
    ),
    "not available": DownloadError(
        ErrorCategory.NOT_FOUND,
        "Video no disponible",
        "El video puede haber sido eliminado",
    ),
    "network": DownloadError(
        ErrorCategory.NETWORK,
        "Error de conexion",
        "Verifica tu conexion a internet",
    ),
    "forbidden": DownloadError(
        ErrorCategory.PERMISSION,
        "Acceso denegado",
        "No tienes permisos para descargar este video",
    ),
    "age": DownloadError(
        ErrorCategory.AUTH,
        "Contenido con restriccion de edad",
        "Requiere cookies con sesion autenticada",
    ),
    "login required": DownloadError(
        ErrorCategory.AUTH,
        "Requiere inicio de sesion",
        "Exporta cookies actualizadas desde tu navegador",
    ),
}


def classify_error(error_text: str) -> DownloadError:
    """Clasifica un error basandose en palabras clave (match de palabra completa)."""
    error_lower = error_text.lower()
    for key, error in ERROR_MAPPINGS.items():
        # Usar word boundaries para match mas preciso
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, error_lower):
            return error
    return DownloadError(
        ErrorCategory.UNKNOWN,
        "Error desconocido",
        "Revisa el log para mas detalles",
    )