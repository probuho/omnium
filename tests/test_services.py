"""Tests para servicios."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from downloader_tui.services.cookies import validate_cookies_file
from downloader_tui.services.downloader import add_common_args, build_yt_dlp_cmd
from downloader_tui.services.ffmpeg import get_ffmpeg_status_message
from downloader_tui.services.quality import (
    FormatInfo,
    filter_formats_by_type,
    parse_formats_output,
)


def test_build_yt_dlp_cmd_video():
    """Test comando para video."""
    cmd = build_yt_dlp_cmd("https://example.com/video", "video")
    # sys.executable devuelve la ruta completa al ejecutable
    assert cmd[0].endswith("python.exe") or cmd[0] == "python"
    assert "-m" in cmd
    assert "yt_dlp" in cmd
    assert "--format" in cmd
    assert "--merge-output-format" in cmd
    assert "mp4" in cmd


def test_build_yt_dlp_cmd_audio():
    """Test comando para audio."""
    cmd = build_yt_dlp_cmd("https://example.com/audio", "audio")
    assert "--format" in cmd
    assert "--extract-audio" in cmd
    assert "--audio-format" in cmd
    assert "--audio-quality" in cmd


def test_build_yt_dlp_cmd_image():
    """Test comando para imagen."""
    cmd = build_yt_dlp_cmd("https://example.com/image", "image")
    assert "--format" in cmd


def test_build_yt_dlp_cmd_pinterest_image():
    """Test comando para imagen de Pinterest (formato best sin thumbnail)."""
    cmd = build_yt_dlp_cmd("https://pinterest.com/pin/123", "image")
    assert "--format" in cmd
    assert "best" in cmd
    # No debe tener --write-thumbnail para Pinterest
    assert "--write-thumbnail" not in cmd


def test_add_common_args():
    """Test argumentos comunes."""
    cmd = ["yt-dlp"]
    cmd = add_common_args(cmd, "https://example.com", use_cookies=False)
    assert "--ffmpeg-location" in cmd
    assert "--output" in cmd
    assert "--no-warnings" in cmd
    assert "--newline" in cmd


def test_parse_formats_output():
    """Test parsing de formatos."""
    sample_output = """
    ID  EXT  RESOLUTION  FPS  FILESIZE  VCODEC        ACODEC  NOTE
    137  mp4  1920x1080  30   5.4MiB    avc1.640028   none    video only
    140  m4a  audio only        1.2MiB    none        mp4a.40.2  audio only
    """
    formats = parse_formats_output(sample_output)
    assert len(formats) >= 1
    assert formats[0].format_id == "137"
    assert formats[0].ext == "mp4"
    assert formats[0].resolution == "1920x1080"


def test_filter_formats_by_type():
    """Test filtrado por tipo."""
    formats = [
        FormatInfo("137", "mp4", "1920x1080", "video only", "5.4MiB", "avc1.640028", None),
        FormatInfo("140", "m4a", "audio only", "audio only", "1.2MiB", None, "mp4a.40.2"),
        FormatInfo("18", "mp4", "640x360", "video", "2.1MiB", "avc1.42001E", "mp4a.40.2"),
    ]

    video_formats = filter_formats_by_type(formats, "video")
    audio_formats = filter_formats_by_type(formats, "audio")

    assert len(video_formats) >= 1
    assert len(audio_formats) >= 1
    assert all(f.vcodec for f in video_formats)
    assert all(f.acodec for f in audio_formats)


def test_validate_cookies_file():
    """Test validación de cookies (mock)."""
    # Solo test que la funcion existe y retorna tupla
    existe, count, msg = validate_cookies_file()
    assert isinstance(existe, bool)
    assert isinstance(count, int)
    assert isinstance(msg, str)


def test_get_ffmpeg_status_message():
    """Test mensaje de estado FFmpeg."""
    msg = get_ffmpeg_status_message()
    assert isinstance(msg, str)
    assert len(msg) > 0