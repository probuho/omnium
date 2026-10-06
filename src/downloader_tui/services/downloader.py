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
from ..logger import logger
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
        if "pinterest.com" in url or "pin.it" in url:
            cmd.extend(["--format", "best"])
        else:
            fmt = image_format or get_image_format()
            cmd.extend([
                "--format", fmt,
                "--write-thumbnail", "--convert-thumbnails", fmt,
            ])

    return cmd


def add_common_args(cmd: list[str], url: str, use_cookies: bool) -> list[str]:
    """Agrega argumentos comunes a yt-dlp."""
    cookies_file = get_cookies_file()
    ffmpeg_dir = get_ffmpeg_dir()
    download_dir = get_download_dir()

    if use_cookies and cookies_file.exists():
        cmd.extend(["--cookies", str(cookies_file)])

    safe_title = "%(playlist_index)s - %(title).%(ext)s"
    cmd.extend([
        "--ffmpeg-location", str(ffmpeg_dir),
        "--output", str(download_dir / safe_title),
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
    logger.info(f"run_download called: url={url[:80]}, media_type={media_type}")
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
        logger.info(f"Executing command: {' '.join(cmd)}")
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(script_dir)
        )
        stdout, stderr = await process.communicate()
        logger.info(f"Process completed: returncode={process.returncode}")

        if process.returncode == 0:
            files = [f for f in download_dir.glob("*") if f.is_file()]
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                logger.info(f"Download successful: {latest.name}")
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
            logger.error(f"Download failed: {error_text[:200]}")
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
