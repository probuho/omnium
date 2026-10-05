"""Servicio de detección de calidades disponibles."""

import asyncio
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ..config import get_cookies_file

MediaType = Literal["video", "audio", "image"]


@dataclass(frozen=True)
class FormatInfo:
    format_id: str
    ext: str
    resolution: str
    note: str
    filesize: str | None
    vcodec: str | None
    acodec: str | None


def parse_formats_output(output: str) -> list[FormatInfo]:
    """Parsea la salida de yt-dlp --list-formats."""
    formats: list[FormatInfo] = []
    lines = output.strip().split("\n")

    # Buscar la tabla de formatos (despues de la linea con "ID" y "EXT")
    in_table = False
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detectar inicio de tabla
        if re.match(r"^\s*ID\s+EXT\s+", line):
            in_table = True
            continue

        if not in_table:
            continue

        # Fin de tabla (linea vacia o separador)
        if line.startswith("[") or line.startswith("Formato") or not line:
            continue

        # Parsear linea de formato
        # Formato típico: "137       mp4       1920x1080  1080p  30fps  5.4MiB  avc1.640028  video only"
        parts = re.split(r"\s{2,}", line)
        if len(parts) < 4:
            continue

        format_id = parts[0].strip()
        ext = parts[1].strip()
        resolution = parts[2].strip()

        # Extraer note/codec/filesize del resto
        note = ""
        filesize = None
        vcodec = None
        acodec = None

        remaining = " ".join(parts[3:]) if len(parts) > 3 else ""

        # Extraer filesize (formato: 5.4MiB, 1024KiB, etc.)
        fs_match = re.search(r"(\d+\.?\d*\s*[KMGT]?i?B)", remaining)
        if fs_match:
            filesize = fs_match.group(1)
            remaining = remaining.replace(filesize, "").strip()

        # Extraer vcodec/acodec
        vc_match = re.search(r"(avc1\.\w+|vp9\.\w+|hev1\.\w+|hvc1\.\w+)", remaining)
        if vc_match:
            vcodec = vc_match.group(1)
            remaining = remaining.replace(vcodec, "").strip()

        ac_match = re.search(r"(mp4a\.\w+|opus\.\w+|vorbis\.\w+)", remaining)
        if ac_match:
            acodec = ac_match.group(1)
            remaining = remaining.replace(acodec, "").strip()

        note = remaining.strip()

        formats.append(FormatInfo(
            format_id=format_id,
            ext=ext,
            resolution=resolution,
            note=note,
            filesize=filesize,
            vcodec=vcodec,
            acodec=acodec,
        ))

    return formats


async def detect_available_formats(
    url: str,
    media_type: Literal["video", "audio", "image"] = "video",
    use_cookies: bool = True,
) -> list[FormatInfo]:
    """Detecta formatos disponibles para una URL."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--list-formats",
        "--no-warnings",
    ]

    if use_cookies:
        cookies_file = get_cookies_file()
        if cookies_file.exists():
            cmd.extend(["--cookies", str(cookies_file)])

    cmd.append(url)

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error = stderr.decode(errors="ignore") if stderr else "Error desconocido"
            raise RuntimeError(f"Error detectando formatos: {error}")

        output = stdout.decode(errors="ignore")
        return parse_formats_output(output)
    except Exception as e:
        raise RuntimeError(f"Error detectando formatos: {e}") from e


def filter_formats_by_type(
    formats: list[FormatInfo],
    media_type: Literal["video", "audio", "image"],
) -> list[FormatInfo]:
    """Filtra formatos segun el tipo de medio."""
    if media_type == "video":
        # Video: tiene video codec y preferiblemente audio codec
        return [f for f in formats if f.vcodec and f.vcodec != "none"]
    elif media_type == "audio":
        # Audio: solo audio codec
        return [f for f in formats if f.acodec and f.acodec != "none" and (not f.vcodec or f.vcodec == "none")]
    elif media_type == "image":
        # Imagen: extensiones de imagen
        image_exts = {"jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"}
        return [f for f in formats if f.ext.lower() in image_exts]
    return formats
