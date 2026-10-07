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


CONSEJO_COOKIES = (
    "Pon cookies_from_browser en Config (chrome, edge, firefox) para que yt-dlp "
    "lea las cookies del navegador, o reexporta cookies.txt"
)

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
    # Antes que "sign in": el mensaje del control antibot de YouTube contiene
    # las dos frases, y este es el consejo util para ese caso concreto.
    "not a bot": DownloadError(
        ErrorCategory.AUTH,
        "YouTube pide verificar que no eres un bot",
        CONSEJO_COOKIES,
    ),
    "rate-limited": DownloadError(
        ErrorCategory.NETWORK,
        "YouTube limito la sesion por demasiadas peticiones",
        "Espera una hora o usa cookies frescas del navegador: " + CONSEJO_COOKIES,
    ),
    "private video": DownloadError(
        ErrorCategory.AUTH,
        "Video privado o restringido",
        CONSEJO_COOKIES,
    ),
    "sign in": DownloadError(
        ErrorCategory.AUTH,
        "Requiere autenticacion",
        CONSEJO_COOKIES,
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
        CONSEJO_COOKIES,
    ),
    "login required": DownloadError(
        ErrorCategory.AUTH,
        "Requiere inicio de sesion",
        CONSEJO_COOKIES,
    ),
    # "unavailable" (una sola palabra) no coincide con "not available" por el
    # match de palabra completa, y es de los mensajes mas frecuentes de yt-dlp.
    "unavailable": DownloadError(
        ErrorCategory.NOT_FOUND,
        "Video no disponible",
        "Puede estar eliminado, ser privado o tener restriccion de pais",
    ),
    # El postprocesado de yt-dlp no debe hundir una descarga que ya funciono.
    # Desde que la caratula se adjunta aparte esto no deberia aparecer, pero si
    # aparece conviene decir que el audio probablemente ya esta.
    "unable to embed": DownloadError(
        ErrorCategory.FORMAT,
        "Fallo al insertar la caratula en el archivo",
        "El audio puede estar ya descargado; revisa la carpeta de descargas",
    ),
}


def _detalle_de_salida(texto: str) -> str:
    """Linea mas informativa de la salida de yt-dlp.

    Se prefiere la PRIMERA linea con el prefijo 'ERROR:' porque, cuando hay
    varios errores (por ejemplo al procesar una lista), la primera es la causa y
    las demas son consecuencia: con la ultima, una descarga que fallo por la
    caratula se reportaba como "video no disponible". Si ninguna linea lleva ese
    prefijo, se usa la ultima con 'error', que es el caso de argparse.
    """
    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
    if not lineas:
        return ""
    con_prefijo = [linea for linea in lineas if linea.startswith("ERROR:")]
    if con_prefijo:
        return con_prefijo[0][len("ERROR:"):].strip()
    con_error = [linea for linea in lineas if "error" in linea.lower()]
    elegida = con_error[-1] if con_error else lineas[-1]
    for prefijo in ("ERROR:", "error:"):
        if elegida.startswith(prefijo):
            return elegida[len(prefijo):].strip()
    return elegida


def classify_error(error_text: str) -> DownloadError:
    """Clasifica un error basandose en palabras clave (match de palabra completa)."""
    error_lower = error_text.lower()
    for key, error in ERROR_MAPPINGS.items():
        # Usar word boundaries para match mas preciso
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, error_lower):
            return error
    # Sin coincidencia: NO se descarta el texto de yt-dlp. Antes se devolvia
    # siempre "Error desconocido" y el motivo real se perdia, que es justo lo
    # contrario de lo que hace falta para diagnosticar.
    detalle = _detalle_de_salida(error_text)
    if detalle:
        return DownloadError(
            ErrorCategory.UNKNOWN,
            f"Error no clasificado: {detalle}",
            "El texto completo de yt-dlp esta en logs/; revisa su ultima linea ERROR",
        )
    return DownloadError(
        ErrorCategory.UNKNOWN,
        "Error desconocido (yt-dlp no devolvio ninguna linea)",
        "Revisa el log en logs/ para mas detalles",
    )
