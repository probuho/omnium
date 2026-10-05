"""Configuración persistente en JSON."""

import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE = SCRIPT_DIR / "config.json"

DEFAULT_CONFIG = {
    "download_dir": r"D:\Vídeo",
    "cookies_file": str(SCRIPT_DIR / "cookies.txt"),
    "ffmpeg_dir": str(SCRIPT_DIR),
    "theme": "textual-dark",
    "video_quality": "bestvideo+bestaudio/best",
    "audio_format": "m4a",
    "audio_quality": "0",
    "image_format": "jpg",
}

_config: dict[str, Any] | None = None


def load_config() -> dict[str, Any]:
    """Carga configuración desde JSON, completando con defaults."""
    global _config
    if _config is not None:
        return _config

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                loaded = json.load(f)
        except (json.JSONDecodeError, OSError):
            loaded = {}
    else:
        loaded = {}

    # Completar con defaults faltantes
    config = DEFAULT_CONFIG.copy()
    config.update(loaded)
    _config = config
    return _config


def save_config(config: dict[str, Any]) -> None:
    """Guarda configuración en JSON."""
    global _config
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        _config = config.copy()
    except OSError as e:
        raise RuntimeError(f"Error guardando config: {e}") from e


def get_download_dir() -> Path:
    return Path(load_config()["download_dir"])


def get_cookies_file() -> Path:
    return Path(load_config()["cookies_file"])


def get_ffmpeg_dir() -> Path:
    return Path(load_config()["ffmpeg_dir"])


def get_theme() -> str:
    return load_config()["theme"]


def get_video_quality() -> str:
    return load_config()["video_quality"]


def get_audio_format() -> str:
    return load_config()["audio_format"]


def get_audio_quality() -> str:
    return load_config()["audio_quality"]


def get_image_format() -> str:
    return load_config()["image_format"]


# Cargar al importar
load_config()
