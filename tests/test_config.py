"""Tests para configuración."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from downloader_tui.config import (
    DEFAULT_CONFIG,
    get_audio_format,
    get_audio_quality,
    get_cookies_file,
    get_download_dir,
    get_ffmpeg_dir,
    get_image_format,
    get_theme,
    get_video_quality,
    load_config,
    save_config,
)


def test_default_config():
    """Test que la config por defecto tiene todos los campos."""
    config = DEFAULT_CONFIG
    assert "download_dir" in config
    assert "cookies_file" in config
    assert "ffmpeg_dir" in config
    assert "theme" in config
    assert "video_quality" in config
    assert "audio_format" in config
    assert "audio_quality" in config
    assert "image_format" in config


def test_load_config_creates_defaults():
    """Test que load_config retorna defaults cuando no hay archivo."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        # Monkeypatch CONFIG_FILE
        import downloader_tui.config as config_module
        original_config_file = config_module.CONFIG_FILE
        config_module.CONFIG_FILE = config_file
        config_module._config = None

        try:
            config = load_config()
            assert config == DEFAULT_CONFIG
        finally:
            config_module.CONFIG_FILE = original_config_file
            config_module._config = None


def test_save_and_load_config():
    """Test guardar y cargar config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        import downloader_tui.config as config_module
        original_config_file = config_module.CONFIG_FILE
        config_module.CONFIG_FILE = config_file
        config_module._config = None

        try:
            custom_config = {
                "download_dir": r"C:\Custom\Path",
                "cookies_file": r"C:\Custom\cookies.txt",
                "ffmpeg_dir": r"C:\Custom\ffmpeg",
                "theme": "textual-light",
                "video_quality": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "audio_format": "mp3",
                "audio_quality": "320",
                "image_format": "png",
            }
            save_config(custom_config)
            loaded = load_config()
            assert loaded == custom_config

            # Verificar getters
            assert get_download_dir() == Path(r"C:\Custom\Path")
            assert get_cookies_file() == Path(r"C:\Custom\cookies.txt")
            assert get_ffmpeg_dir() == Path(r"C:\Custom\ffmpeg")
            assert get_theme() == "textual-light"
            assert get_video_quality() == "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            assert get_audio_format() == "mp3"
            assert get_audio_quality() == "320"
            assert get_image_format() == "png"
        finally:
            config_module.CONFIG_FILE = original_config_file
            config_module._config = None


def test_config_persistence():
    """Test que la config persiste entre cargas."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        import downloader_tui.config as config_module
        original_config_file = config_module.CONFIG_FILE
        config_module.CONFIG_FILE = config_file
        config_module._config = None

        try:
            save_config({"theme": "textual-ansi"})
            config_module._config = None  # Forzar recarga
            loaded = load_config()
            assert loaded["theme"] == "textual-ansi"
        finally:
            config_module.CONFIG_FILE = original_config_file
            config_module._config = None
