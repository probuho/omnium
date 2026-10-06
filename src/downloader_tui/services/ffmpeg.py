"""Servicio de detección y validación de FFmpeg."""

import asyncio

from ..config import get_ffmpeg_dir
from ..logger import logger


async def test_ffmpeg() -> tuple[bool, str]:
    """
    Prueba si FFmpeg funciona correctamente.

    Returns:
        tuple: (funciona, mensaje)
    """
    ffmpeg_dir = get_ffmpeg_dir()
    ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"

    if not ffmpeg_exe.exists():
        return False, f"FFmpeg no encontrado en: {ffmpeg_exe}"

    try:
        process = await asyncio.create_subprocess_exec(
            str(ffmpeg_exe), "-version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            version_line = stdout.decode(errors="ignore").split("\n")[0]
            logger.info(f"FFmpeg OK: {version_line}")
            return True, f"FFmpeg OK: {version_line}"
        else:
            error = stderr.decode(errors="ignore")
            return False, f"FFmpeg error: {error}"
    except Exception as e:
        logger.error(f"FFmpeg test failed: {e}")
        return False, f"Error ejecutando FFmpeg: {e}"


def get_ffmpeg_status_message() -> str:
    """Retorna mensaje de estado para UI (version sincrona simple)."""
    ffmpeg_dir = get_ffmpeg_dir()
    ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"

    if not ffmpeg_exe.exists():
        return "[red]FFmpeg no encontrado[/red]"

    try:
        import subprocess
        result = subprocess.run(
            [str(ffmpeg_exe), "-version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split("\n")[0]
            return f"[green]FFmpeg OK: {version}[/green]"
        return "[red]FFmpeg no funciona[/red]"
    except Exception:
        return "[red]Error verificando FFmpeg[/red]"
