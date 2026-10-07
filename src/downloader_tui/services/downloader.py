"""Servicio de descarga: construccion de comandos y ejecucion."""

import asyncio
import os
import re
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ..config import (
    get_audio_format,
    get_audio_quality,
    get_cookies_file,
    get_download_dir,
    get_ffmpeg_dir,
    get_image_format,
    get_video_quality,
    load_config,
)
from ..logger import logger
from ..models.errors import DownloadError, ErrorCategory, classify_error

MediaType = Literal["video", "audio", "image"]



@dataclass(frozen=True)
class DownloadResult:
    success: bool
    file_path: Path | None
    error: DownloadError | None
    message: str


@dataclass(frozen=True)
class DownloadProgress:
    """Una actualizacion de progreso de yt-dlp."""

    porcentaje: float | None
    descargado: int | None
    total: int | None
    velocidad: float | None
    eta: int | None


# Prefijo propio dentro de la plantilla de progreso: asi el parseo no depende
# del texto humano de yt-dlp (que cambia entre versiones).
PROGRESO_PREFIJO = "OMNIUM_PROGRESS "
PROGRESO_TEMPLATE = (
    "download:"
    + PROGRESO_PREFIJO
    + "%(progress.downloaded_bytes)s %(progress.total_bytes)s "
    + "%(progress.total_bytes_estimate)s %(progress.speed)s %(progress.eta)s"
)

# Lineas de yt-dlp que llevan la ruta del archivo. Vale la ULTIMA que aparezca:
# despues de descargar puede fusionar (Muxer) o extraer el audio (ExtractAudio),
# y el archivo definitivo es el de ese ultimo paso.
_RE_DESTINO = re.compile(
    r'^\[(?:download|Muxer|ffmpeg|ExtractAudio|FixupM4a|VideoConvertor)\]'
    r'\s+(?:Destination:|Merging formats into)\s+"?(.+?)"?\s*$'
)
_RE_YA_ESTABA = re.compile(r"^\[download\]\s+(.+?)\s+has already been downloaded\s*$")


def _a_numero(texto: str) -> float | None:
    """yt-dlp escribe NA (o None) cuando el dato no se conoce."""
    if texto in ("NA", "None", ""):
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def parsear_progreso(linea: str) -> DownloadProgress | None:
    """Convierte una linea de progreso de yt-dlp en un DownloadProgress.

    Si la linea no es de progreso, o no tiene los 5 campos esperados, devuelve
    None: nunca se inventa un avance.
    """
    if not linea.startswith(PROGRESO_PREFIJO):
        return None
    partes = linea[len(PROGRESO_PREFIJO):].split()
    if len(partes) != 5:
        return None
    descargado, total, estimado, velocidad, eta = (_a_numero(p) for p in partes)
    total_real = total if total is not None else estimado
    porcentaje = None
    if descargado is not None and total_real:
        porcentaje = min(100.0, descargado / total_real * 100.0)
    return DownloadProgress(
        porcentaje=porcentaje,
        descargado=None if descargado is None else int(descargado),
        total=None if total_real is None else int(total_real),
        velocidad=velocidad,
        eta=None if eta is None else int(eta),
    )


def parsear_destino(linea: str) -> Path | None:
    """Extrae la ruta del archivo de una linea de yt-dlp, si la lleva."""
    for patron in (_RE_DESTINO, _RE_YA_ESTABA):
        coincidencia = patron.match(linea)
        if coincidencia:
            return Path(coincidencia.group(1).strip())
    return None


def _archivo_final(
    destino: Path | None, download_dir: Path, desde: float
) -> Path | None:
    """Ruta del archivo descargado.

    Se prefiere la que yt-dlp anuncio en su salida. Antes se cogia sin mas el
    archivo mas reciente del directorio de descargas, que puede ser cualquier
    otro: si la descarga no creaba nada nuevo, la app informaba de un archivo
    ajeno como si acabara de descargarlo.
    """
    if destino is not None and destino.exists():
        return destino
    candidatos = [
        f for f in download_dir.glob("*") if f.is_file() and f.stat().st_mtime >= desde
    ]
    if candidatos:
        return max(candidatos, key=lambda f: f.stat().st_mtime)
    return None


def es_video_suelto_en_lista(url: str) -> bool:
    """True si es un video concreto dentro de una lista (watch?v=...&list=...).

    En ese caso hay que descargar SOLO ese video. Pegar una cancion de una radio
    automatica de YouTube (list=RD...) hacia que yt-dlp intentara bajar la lista
    entera: decenas de videos que nadie habia pedido, con sus errores llenando
    el log y ocultando el problema real.
    """
    return "watch" in url and "v=" in url and "list=" in url


def _ffmpeg_exe() -> Path:
    """Ruta al ffmpeg que viene con el proyecto."""
    return get_ffmpeg_dir() / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")


def _buscar_portada(archivo: Path) -> Path | None:
    """Caratula que yt-dlp dejo junto al audio, si la dejo."""
    for sufijo in (".jpg", ".jpeg", ".png", ".webp"):
        candidata = archivo.with_suffix(sufijo)
        if candidata.exists():
            return candidata
    return None


def _argumentos_caratula(sufijo: str) -> list[str] | None:
    """Argumentos de ffmpeg para adjuntar una caratula, segun el contenedor.

    Devuelve None para los contenedores donde ffmpeg no puede hacerlo solo
    (opus, flac, ogg): ahi la caratula se queda como archivo al lado.
    """
    if sufijo in (".m4a", ".mp4", ".m4v", ".mov"):
        return ["-map", "0", "-map", "1", "-c", "copy", "-disposition:1", "attached_pic"]
    if sufijo == ".mp3":
        return [
            "-map", "0", "-map", "1", "-c", "copy", "-id3v2_version", "3",
            "-metadata:s:v", "title=Album cover",
            "-metadata:s:v", "comment=Cover (front)",
        ]
    return None


async def _adjuntar_caratula(archivo: Path) -> Path:
    """Mete la caratula descargada dentro del archivo de audio.

    Se hace aqui y no con --embed-thumbnail porque ese postprocesado de yt-dlp
    necesita mutagen o AtomicParsley para m4a y, si no estan, cae a un ffmpeg
    que fallaba en la practica, tumbando una descarga de audio ya correcta.
    Si adjuntar falla, la descarga SIGUE siendo un exito y la caratula se queda
    como archivo al lado: eso es informacion util, no un error.
    """
    portada = _buscar_portada(archivo)
    if portada is None:
        return archivo

    argumentos = _argumentos_caratula(archivo.suffix.lower())
    if argumentos is None:
        logger.info(f"Caratula no adjuntable en {archivo.suffix}: se deja {portada.name}")
        return archivo

    temporal = archivo.with_name(f"{archivo.stem}__con_caratula{archivo.suffix}")
    try:
        proceso = await asyncio.create_subprocess_exec(
            str(_ffmpeg_exe()), "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(archivo), "-i", str(portada),
            *argumentos, str(temporal),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, err = await proceso.communicate()
    except OSError as e:
        logger.error(f"No se pudo ejecutar ffmpeg para la caratula: {e}")
        return archivo

    if proceso.returncode != 0 or not temporal.exists():
        logger.error(
            "No se pudo adjuntar la caratula: "
            f"{err.decode(errors='ignore').strip()[:300]}"
        )
        temporal.unlink(missing_ok=True)
        return archivo

    temporal.replace(archivo)
    portada.unlink(missing_ok=True)
    logger.info(f"Caratula adjuntada a {archivo.name}")
    return archivo


def build_yt_dlp_cmd(
    url: str,
    media_type: MediaType,
    video_quality: str | None = None,
    audio_format: str | None = None,
    audio_quality: str | None = None,
    image_format: str | None = None,
) -> list[str]:
    """Construye el comando yt-dlp segun el tipo de medio."""
    cmd = [sys.executable, "-m", "yt_dlp"]

    if media_type == "video":
        fmt = video_quality or get_video_quality()
        cmd.extend(["--format", fmt, "--merge-output-format", "mp4"])
    elif media_type == "audio":
        fmt = audio_format or get_audio_format()
        quality = audio_quality or get_audio_quality()
        cmd.extend([
            "--format", "bestaudio/best",
            "--extract-audio", "--audio-format", fmt,
            "--audio-quality", quality,
            # Etiquetas dentro del archivo (titulo, artista, album).
            "--embed-metadata",
            # La caratula se DESCARGA aqui y se adjunta despues, en
            # _adjuntar_caratula(). Con --embed-thumbnail, yt-dlp necesita
            # mutagen o AtomicParsley para m4a y, si no estan, cae a un ffmpeg
            # que en la practica falla con "Unable to embed using ffprobe &
            # ffmpeg; Conversion failed!", tumbando una descarga de audio que ya
            # estaba perfecta.
            "--write-thumbnail",
            "--convert-thumbnails", "jpg",
            # En YouTube el artista real suele ser el canal que sube la cancion.
            # La regex descarta el literal "NA" con el que yt-dlp sustituye un
            # campo ausente: sin ella la etiqueta artist acababa valiendo "NA"
            # cuando el sitio no daba canal (comprobado con ffprobe).
            "--parse-metadata", "uploader:(?P<meta_artist>^(?!NA$).+)",
        ])
    elif media_type == "image":
        if "pinterest.com" in url or "pin.it" in url:
            cmd.extend(["--format", "best"])
        else:
            fmt = image_format or get_image_format()
            cmd.extend([
                "--format", fmt,
                "--write-thumbnail", "--convert-thumbnails", fmt,
            ])

    return cmd


def plantilla_de_salida(media_type: MediaType) -> str:
    """Plantilla del nombre de archivo segun el tipo de medio.

    El prefijo del indice de lista es opcional (%(playlist_index&{} - |)s): en un
    video suelto no imprime nada y en una lista numera las pistas.
    El audio usa "Artista - Titulo" porque es lo que hace util una biblioteca de
    musica; si el sitio no da artista se usa el canal y, en ultimo caso, un
    literal honesto en vez de un nombre vacio.
    """
    if media_type == "audio":
        return "%(artist,uploader,channel|Desconocido)s - %(title)s.%(ext)s"
    return "%(playlist_index&{} - |)s%(title)s.%(ext)s"


def add_common_args(
    cmd: list[str], url: str, use_cookies: bool, media_type: MediaType = "video"
) -> list[str]:
    """Agrega argumentos comunes a yt-dlp."""
    cookies_file = get_cookies_file()
    ffmpeg_dir = get_ffmpeg_dir()
    download_dir = get_download_dir()

    # Cookies: el navegador manda sobre el archivo. YouTube corta la sesion con
    # "Sign in to confirm you're not a bot" en cuanto el cookies.txt se queda
    # viejo, y leerlas del navegador siempre da cookies frescas.
    navegador = str(load_config().get("cookies_from_browser") or "").strip()
    if use_cookies and navegador:
        cmd.extend(["--cookies-from-browser", navegador])
    elif use_cookies and cookies_file.exists():
        cmd.extend(["--cookies", str(cookies_file)])

    if es_video_suelto_en_lista(url):
        cmd.append("--no-playlist")

    # Antes esta plantilla decia "%(playlist_index)s - %(title).%(ext)s", a la
    # que le faltaba la 's' de %(title)s. yt-dlp la validaba y abortaba con
    # "unsupported format character '%'": TODA descarga fallaba con exit 2 antes
    # de empezar, con cualquier URL, y el error se clasificaba como desconocido.
    safe_title = plantilla_de_salida(media_type)
    cmd.extend([
        "--ffmpeg-location", str(ffmpeg_dir),
        "--output", str(download_dir / safe_title),
        "--no-warnings",
        "--newline",
        "--progress-template", PROGRESO_TEMPLATE,
        url
    ])
    return cmd


async def run_download(
    url: str,
    media_type: MediaType,
    use_cookies: bool = True,
    video_quality: str | None = None,
    audio_format: str | None = None,
    audio_quality: str | None = None,
    image_format: str | None = None,
    on_progress: Callable[[DownloadProgress], None] | None = None,
) -> DownloadResult:
    """Ejecuta la descarga y retorna resultado.

    on_progress se llama con cada actualizacion de yt-dlp. La salida se lee en
    streaming, no con communicate(): esperar al final dejaba la barra de
    progreso clavada en 0% durante toda una descarga larga.
    """
    logger.info(f"run_download called: url={url[:80]}, media_type={media_type}")
    cmd = build_yt_dlp_cmd(
        url, media_type,
        video_quality=video_quality,
        audio_format=audio_format,
        audio_quality=audio_quality,
        image_format=image_format,
    )
    cmd = add_common_args(cmd, url, use_cookies, media_type)

    download_dir = get_download_dir()
    script_dir = Path(__file__).parent.parent.parent
    # Margen de 2 s: el sistema de archivos puede redondear la marca de tiempo.
    desde = time.time() - 2
    proceso: asyncio.subprocess.Process | None = None

    try:
        logger.info(f"Executing command: {' '.join(cmd)}")
        proceso = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(script_dir)
        )
        assert proceso.stdout is not None and proceso.stderr is not None

        lineas: list[str] = []
        destino: Path | None = None

        async def leer_stdout() -> None:
            nonlocal destino
            async for cruda in proceso.stdout:  # type: ignore[union-attr]
                linea = cruda.decode(errors="ignore").rstrip("\r\n")
                lineas.append(linea)
                ruta = parsear_destino(linea)
                if ruta is not None:
                    destino = ruta
                if on_progress is not None:
                    avance = parsear_progreso(linea)
                    if avance is not None:
                        on_progress(avance)

        # stdout y stderr se drenan a la vez: si solo se leyera uno, yt-dlp se
        # bloquearia al llenarse el buffer del otro.
        tarea_out = asyncio.create_task(leer_stdout())
        tarea_err = asyncio.create_task(proceso.stderr.read())
        await asyncio.gather(tarea_out, tarea_err)
        stderr = tarea_err.result()
        returncode = await proceso.wait()
        logger.info(f"Process completed: returncode={returncode}")

        if returncode == 0:
            archivo = _archivo_final(destino, download_dir, desde)
            if archivo is not None:
                if media_type == "audio":
                    archivo = await _adjuntar_caratula(archivo)
                logger.info(f"Download successful: {archivo}")
                return DownloadResult(
                    success=True,
                    file_path=archivo,
                    error=None,
                    message=f"Descarga completada: {archivo.name}",
                )
            return DownloadResult(
                success=True,
                file_path=None,
                error=None,
                message="Descarga completada",
            )
        else:
            # yt-dlp escribe el motivo en stderr, pero argparse y algunos avisos
            # salen por stdout: se miran los dos para no perder nunca el detalle
            # real del fallo.
            error_text = stderr.decode(errors="ignore").strip()
            if not error_text:
                error_text = "\n".join(lineas).strip()
            logger.error(
                f"Download failed (returncode={returncode}): {error_text[:2000]}"
            )
            error = classify_error(error_text)
            return DownloadResult(
                success=False,
                file_path=None,
                error=error,
                message=f"{error.message}: {error.suggestion}",
            )
    except asyncio.CancelledError:
        # Sin esto el proceso de yt-dlp se quedaba vivo y descargando en segundo
        # plano cuando el usuario cancelaba o lanzaba otra descarga.
        if proceso is not None and proceso.returncode is None:
            proceso.kill()
            await proceso.wait()
        logger.warning("Download cancelled; subprocess killed")
        return DownloadResult(
            success=False,
            file_path=None,
            error=DownloadError(
                ErrorCategory.UNKNOWN,
                "Descarga cancelada",
                "La descarga fue cancelada por el usuario",
            ),
            message="Descarga cancelada",
        )
    except Exception as e:
        error = classify_error(str(e))
        return DownloadResult(
            success=False,
            file_path=None,
            error=error,
            message=f"{error.message}: {error.suggestion}",
        )
