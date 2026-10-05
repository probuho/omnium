"""Servicio de descarga: construccion de comandos y ejecucion."""

import asyncio
import sys
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
)
from ..models.errors import DownloadError, ErrorCategory, classify_error

MediaType = Literal["video", "audio", "image"]


@dataclass(frozen=True)
class DownloadResult:
    success: bool
    file_path: Path | None
    error: DownloadError | None
    message: str


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
        ])
    elif media_type == "image":
        # Pinterest: descargar imagen original directa sin thumbnail conversion
        if "pinterest.com" in url or "pin.it" in url:
            cmd.extend(["--format", "best"])
        else:
            fmt = image_format or get_image_format()
            cmd.extend([
                "--format", fmt,
                "--write-thumbnail", "--convert-thumbnails", fmt,
            ])
    elif media_type == "video":
        # Pinterest video: usar formato best para obtener la mejor calidad
        if "pinterest.com" in url or "pin.it" in url:
            cmd.extend(["--format", "best", "--merge-output-format", "mp4"])
        else:
            fmt = video_quality or get_video_quality()
            cmd.extend(["--format", fmt, "--merge-output-format", "mp4"])

    return cmd


def add_common_args(cmd: list[str], url: str, use_cookies: bool) -> list[str]:
    """Agrega argumentos comunes a yt-dlp."""
    cookies_file = get_cookies_file()
    ffmpeg_dir = get_ffmpeg_dir()
    download_dir = get_download_dir()

    if use_cookies and cookies_file.exists():
        cmd.extend(["--cookies", str(cookies_file)])

    cmd.extend([
        "--ffmpeg-location", str(ffmpeg_dir),
        "--output", str(download_dir / "%(playlist_index)s - %(title)s.%(ext)s"),
        "--no-warnings",
        "--newline",
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
) -> DownloadResult:
    """Ejecuta la descarga y retorna resultado."""
    cmd = build_yt_dlp_cmd(
        url, media_type,
        video_quality=video_quality,
        audio_format=audio_format,
        audio_quality=audio_quality,
        image_format=image_format,
    )
    cmd = add_common_args(cmd, url, use_cookies)

    download_dir = get_download_dir()
    script_dir = Path(__file__).parent.parent.parent

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(script_dir)
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            files = list(download_dir.glob("*"))
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                return DownloadResult(
                    success=True,
                    file_path=latest,
                    error=None,
                    message=f"Descarga completada: {latest.name}",
                )
            return DownloadResult(
                success=True,
                file_path=None,
                error=None,
                message="Descarga completada",
            )
        else:
            error_text = stderr.decode(errors="ignore") if stderr else "Error desconocido"
            error = classify_error(error_text)
            return DownloadResult(
                success=False,
                file_path=None,
                error=error,
                message=f"{error.message}: {error.suggestion}",
            )
    except asyncio.CancelledError:
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
