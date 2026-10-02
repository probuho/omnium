#!/usr/bin/env python3
"""
Omnium Suite - Universal Video Downloader TUI
Estilo opencode: single-screen, input protagonista, header ASCII grande.
"""

import sys
import os
import asyncio
import subprocess
import re
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Input, Label, Static,
    DataTable, Log, ProgressBar, Collapsible, OptionList, TextArea
)
from textual.widgets._option_list import Option
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual import work
from textual.message import Message

SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

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
    "custom_audio_formats": [],
    "custom_video_qualities": [],
    "custom_image_formats": [],
}

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> None:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando config: {e}")

config = load_config()
DOWNLOAD_DIR = Path(config["download_dir"])
COOKIES_FILE = Path(config["cookies_file"])
FFMPEG_DIR = Path(config["ffmpeg_dir"])


class ErrorCategory(Enum):
    NETWORK = "network"
    AUTH = "auth"
    NOT_FOUND = "not_found"
    FORMAT = "format"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


@dataclass
class DownloadError:
    category: ErrorCategory
    message: str
    suggestion: str


ERROR_MAPPINGS = {
    "ffmpeg is not installed": DownloadError(ErrorCategory.UNKNOWN, "FFmpeg no encontrado", "Verifica que ffmpeg.exe esté en la carpeta del proyecto"),
    "merge": DownloadError(ErrorCategory.FORMAT, "Error al fusionar video/audio", "Intenta con otra calidad o formato"),
    "private video": DownloadError(ErrorCategory.AUTH, "Video privado o restringido", "Verifica que tus cookies estén actualizadas"),
    "sign in": DownloadError(ErrorCategory.AUTH, "Requiere autenticación", "Exporta cookies actualizadas desde tu navegador"),
    "not available": DownloadError(ErrorCategory.NOT_FOUND, "Video no disponible", "El video puede haber sido eliminado"),
    "network": DownloadError(ErrorCategory.NETWORK, "Error de conexión", "Verifica tu conexión a internet"),
    "forbidden": DownloadError(ErrorCategory.PERMISSION, "Acceso denegado", "No tienes permisos para descargar este video"),
}


SITES_LIST = """
Video Principales:
  YouTube, Vimeo, Dailymotion, Twitch, TikTok, Twitter/X, Instagram, Facebook, Reddit, Pinterest

Audio / Musica:
  SoundCloud, Bandcamp, Mixcloud, Audiomack, Spotify (podcasts), Apple Music (previews)

Streaming / TV:
  Crunchyroll, Funimation, Netflix*, Hulu*, HBO Max*, Disney+*, Amazon Prime*, PBS, BBC iPlayer, ARTE, SVT, DRTV, RaiPlay, France TV, ZDF, ORF

Educativos / Tech:
  Coursera*, Udemy*, edX*, Khan Academy, TED, MIT OpenCourseWare, YouTube Edu, Vimeo, Wistia, Brightcove, Panopto, Kaltura

News / Deportes:
  ESPN, CBS Sports, NBC Sports, ABC, CNN, Fox News, MSNBC, Bloomberg, Reuters, AP, MLB.tv*, NFL*, NBA*, NHL*, FIFA+

Adultos:
  Pornhub, xHamster, xvideos, RedTube, YouPorn, OnlyFans*, ManyVids*, Fansly*

Otros Populares:
  Bilibili, Niconico, FC2, Miaopai, PearVideo, Weibo, Douyin, Kuaishou, Xigua, AcFun, Rutube, VK, OK.ru, Mail.ru, Yandex, Tumblr, 9GAG, Imgur, Gfycat, Streamable, Clippit, MediathekView, Zattoo, Joyn, TVNow, RTL+, ProSiebenSat.1, Mitele, Atresplayer, RTVE, TV3, Canal Sur, ETB, TVG, CMM, IB3

* Requieren cookies.txt con sesion valida

Total: 1000+ extractores (ver lista completa: yt-dlp --list-extractors)
"""


ACCESSIBILITY_TEXT = """
Atajos Globales (disponibles en todas las pantallas):
  ESC           - Volver / Salir
  Q             - Salir de la aplicacion
  Enter         - Descargar (en pantalla principal)
  Ctrl+V        - Pegar URL del portapapeles
  Ctrl+C        - Copiar URL actual
  Ctrl+L        - Limpiar campo URL
  Tab / Shift+Tab - Cambiar pestaña (Video/Audio/Imagen)
  Flechas       - Navegar entre botones y opciones
  H             - Abrir Historial
  S             - Abrir Configuracion
  I             - Abrir Sitios Compatibles
  A             - Abrir Accesibilidad (desde Configuracion)
  C             - Abrir Creditos (desde Configuracion)

Pantalla Principal:
  Flechas Izq/Der - Navegar entre botones de accion
  Flechas Arr/Ab - Cambiar foco entre input y botones
  Enter en boton  - Ejecutar accion del boton

Pantalla de Historial:
  R             - Actualizar lista
  Delete        - Eliminar archivo seleccionado
  Flechas Arr/Ab - Navegar filas de la tabla

Pantalla de Configuracion:
  Flechas Arr/Ab - Navegar entre campos y botones
  Enter en Input  - Editar valor
  Enter en Boton  - Ejecutar accion
  A             - Abrir Accesibilidad
  C             - Abrir Creditos

Pantalla de Sitios Compatibles:
  Flechas Arr/Ab - Scroll en la lista
  Page Up/Down  - Scroll rapido

Pantalla de Accesibilidad / Creditos:
  Flechas Arr/Ab - Scroll en el texto
  Page Up/Down  - Scroll rapido
"""


CREDITS_TEXT = """
Omnium Suite - Universal Video Downloader
Version 1.0

Desarrollado con:
  - Python 3
  - Textual (TUI framework) - https://github.com/Textualize/textual
  - yt-dlp (descarga de video/audio) - https://github.com/yt-dlp/yt-dlp
  - FFmpeg (procesamiento multimedia) - https://ffmpeg.org/

Agradecimientos especiales:
  - Equipo de Textualize por Textual, un framework TUI excelente
  - Equipo de yt-dlp por el mejor descargador de video/audio
  - Comunidad de FFmpeg por el procesamiento multimedia estandar

Licencia: MIT
Este software se ejecuta 100% localmente en tu equipo.
No se recopilan, envian ni almacenan datos personales.
"""


def classify_error(error_text: str) -> DownloadError:
    error_lower = error_text.lower()
    for key, error in ERROR_MAPPINGS.items():
        if key in error_lower:
            return error
    return DownloadError(ErrorCategory.UNKNOWN, "Error desconocido", "Revisa el log para más detalles")


ASCII_LOGO = r"""
  ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ██████╗  ██████╗ ████████╗███████╗
 ██╔════╝██═══██╗████╗ ████║██╔══██╗██║     ██═══██╗██═══██╗╚══██══╝██════╝
 ██║     ██║   ██║██╔████╔██║██████═╝ ██║     ██║  ██║██═══██║   ██══╝  ╚════██║
 ██║     ██═══██══╝██══════╝╚══════╝╚══════╝╚══════╝╚══════╝    ╚══════╝╚══════╝
"""

class ConfirmDialog(ModalScreen[bool]):
    def __init__(self, title: str, message: str):
        super().__init__()
        self._title = title
        self._message = message

    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"[bold]{self._title}[/bold]", classes="dialog-title"),
            Static(self._message, classes="dialog-message"),
            Horizontal(
                Button("Si", variant="primary", id="confirm"),
                Button("No", variant="default", id="cancel"),
                classes="dialog-buttons"
            ),
            classes="dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")


class QualityDetectionModal(ModalScreen[dict]):
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.formats = []

    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold]Calidades Disponibles[/bold]", classes="dialog-title"),
            Static(f"URL: {self.url}", classes="dialog-message"),
            Static("[dim]Detectando formatos disponibles...[/dim]", id="detection_status"),
            Static("", id="formats_list"),
            Horizontal(
                Button("Descargar con seleccion", variant="primary", id="download_selected"),
                Button("Cancelar", variant="default", id="cancel"),
                classes="dialog-buttons"
            ),
            classes="dialog"
        )

    def on_mount(self) -> None:
        self.run_worker(self._detect_formats(), exclusive=True)

    async def _detect_formats(self) -> None:
        try:
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--list-formats",
                "--no-warnings",
                self.url
            ]
            if COOKIES_FILE.exists():
                cmd.extend(["--cookies", str(COOKIES_FILE)])

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(SCRIPT_DIR)
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                output = stdout.decode(errors="ignore")
                self.formats = self._parse_formats(output)
                self._update_formats_display()
            else:
                error = stderr.decode(errors="ignore")
                self.query_one("#detection_status", Static).update(f"[red]Error: {error}[/red]")
        except Exception as e:
            self.query_one("#detection_status", Static).update(f"[red]Error: {e}[/red]")

    def _parse_formats(self, output: str) -> list:
        formats = []
        lines = output.split("\n")
        for line in lines:
            if "video only" in line or "audio only" in line or "video" in line and "audio" in line:
                parts = line.split()
                if len(parts) >= 4:
                    fmt_id = parts[0]
                    ext = parts[1] if len(parts) > 1 else ""
                    resolution = parts[2] if len(parts) > 2 else ""
                    formats.append({
                        "id": fmt_id,
                        "ext": ext,
                        "resolution": resolution,
                        "line": line.strip()
                    })
        return formats[:30]

    def _update_formats_display(self) -> None:
        if not self.formats:
            self.query_one("#formats_list", Static).update("[dim]No se detectaron formatos[/dim]")
            return

        text = ""
        for i, fmt in enumerate(self.formats):
            text += f"  {i+1}. ID: {fmt['id']}  Ext: {fmt['ext']}  Res: {fmt['resolution']}\n"

        self.query_one("#formats_list", Static).update(text)
        self.query_one("#detection_status", Static).update(f"[green]Se detectaron {len(self.formats)} formatos[/green]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download_selected":
            self.dismiss({"formats": self.formats, "url": self.url})
        elif event.button.id == "cancel":
            self.dismiss(None)


class MainScreen(Screen):
    BINDINGS = [
        Binding("escape", "quit", "Salir"),
        Binding("enter", "download", "Descargar"),
        Binding("ctrl+v", "paste", "Pegar"),
        Binding("ctrl+c", "copy", "Copiar"),
        Binding("ctrl+l", "clear", "Limpiar"),
        Binding("h", "history", "Historial"),
        Binding("s", "settings", "Config"),
        Binding("i", "sites", "Sitios"),
        Binding("tab", "next_tab", "Pestaña sig."),
        Binding("shift+tab", "prev_tab", "Pestaña ant."),
        Binding("up", "focus_prev", "Anterior"),
        Binding("down", "focus_next", "Siguiente"),
        Binding("left", "focus_prev", "Anterior"),
        Binding("right", "focus_next", "Siguiente"),
    ]

    MEDIA_TYPES = [
        ("video", "Video", "bestvideo+bestaudio/best", "mp4"),
        ("audio", "Audio", "bestaudio/best", "m4a"),
        ("image", "Imagen", "best", "jpg"),
    ]

    AUDIO_FORMATS = [
        ("m4a", "M4A (AAC) - Compatible, buena calidad"),
        ("mp3", "MP3 - Universal, compatible"),
        ("opus", "OPUS - Mejor calidad/tamaño"),
        ("flac", "FLAC - Sin pérdida"),
        ("wav", "WAV - Sin compresión"),
    ]

    VIDEO_QUALITIES = [
        ("bestvideo+bestaudio/best", "Mejor disponible (auto)"),
        ("bestvideo[height<=4320]+bestaudio/best[height<=4320]", "8K (4320p)"),
        ("bestvideo[height<=2160]+bestaudio/best[height<=2160]", "4K (2160p)"),
        ("bestvideo[height<=1440]+bestaudio/best[height<=1440]", "2K (1440p)"),
        ("bestvideo[height<=1080]+bestaudio/best[height<=1080]", "Full HD (1080p)"),
        ("bestvideo[height<=720]+bestaudio/best[height<=720]", "HD (720p)"),
        ("bestvideo[height<=480]+bestaudio/best[height<=480]", "SD (480p)"),
        ("worstvideo+worstaudio/worst", "Peor calidad (archivo pequeño)"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(ASCII_LOGO, classes="ascii-logo"),
            Static("═" * 80, classes="divider"),
            Vertical(
                Static("[bold]URL:[/bold]", classes="url-label"),
                Input(placeholder="https://youtube.com/watch?v=...  •  pegar con Ctrl+V", id="url_input"),
                Static("", id="url_validation", classes="validation"),
                Static(
                    "[dim]Funciona con: posts, stories, reels, videos, audio, imagenes de Instagram, TikTok, YouTube, Twitter/X, Facebook, Reddit, Pinterest, SoundCloud, Bandcamp y 1000+ sitios[/dim]",
                    classes="sites-hint"
                ),
                classes="input-group"
            ),
            Static("─" * 80, classes="divider"),
            Horizontal(
                Button("Video", id="tab_video", variant="primary"),
                Button("Audio", id="tab_audio", variant="default"),
                Button("Imagen", id="tab_image", variant="default"),
                classes="tab-group"
            ),
            Static("[dim]Calidad y formato se configuran en Config (S)[/dim]", classes="sites-hint"),
            Static("─" * 80, classes="divider"),
            Horizontal(
                Button("Descargar (Enter)", variant="primary", id="download_btn"),
                Button("Limpiar (Ctrl+L)", variant="default", id="clear_btn"),
                Button("Pegar (Ctrl+V)", variant="default", id="paste_btn"),
                Button("Sitios (I)", variant="default", id="sites_btn"),
                Button("Historial (H)", variant="default", id="history_btn"),
                Button("Config (S)", variant="default", id="settings_btn"),
                classes="button-group"
            ),
            Static("", id="status", classes="status"),
            ProgressBar(total=100, show_eta=False, id="progress"),
            Collapsible(
                Log(id="download_log", classes="log"),
                title="Log de descarga",
                collapsed=True,
                id="log_collapsible"
            ),
            Static(
                "[dim]Privacidad: Esta herramienta se ejecuta 100% en tu equipo. No se envian datos, URLs, ni credenciales a servidores externos. "
                "Solo yt-dlp (local) contacta directamente al sitio de origen para descargar el contenido que tu solicitas.[/dim]",
                classes="privacy-notice"
            ),
            classes="main-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.url_input = self.query_one("#url_input", Input)
        self.url_validation = self.query_one("#url_validation", Static)
        self.progress_bar = self.query_one("#progress", ProgressBar)
        self.status = self.query_one("#status", Static)
        self.log_widget = self.query_one("#download_log", Log)
        self.download_btn = self.query_one("#download_btn", Button)

        self.tab_buttons = [
            self.query_one("#tab_video", Button),
            self.query_one("#tab_audio", Button),
            self.query_one("#tab_image", Button),
        ]

        self.buttons = [
            self.query_one("#download_btn", Button),
            self.query_one("#clear_btn", Button),
            self.query_one("#paste_btn", Button),
            self.query_one("#sites_btn", Button),
            self.query_one("#history_btn", Button),
            self.query_one("#settings_btn", Button),
        ]
        self.focus_index = 0
        self.current_media = "video"
        self.downloading = False
        self.url_input.focus()
        self._update_button_focus()
        self._show_media_options("video")

    def _update_button_focus(self) -> None:
        for i, btn in enumerate(self.buttons):
            if i == self.focus_index:
                btn.add_class("focused")
            else:
                btn.remove_class("focused")

    def _show_media_options(self, media: str) -> None:
        self.current_media = media
        for btn in self.tab_buttons:
            btn.variant = "default"

        if media == "video":
            self.tab_buttons[0].variant = "primary"
        elif media == "audio":
            self.tab_buttons[1].variant = "primary"
        elif media == "image":
            self.tab_buttons[2].variant = "primary"

    def action_next_tab(self) -> None:
        idx = ["video", "audio", "image"].index(self.current_media)
        self._show_media_options(["video", "audio", "image"][(idx + 1) % 3])

    def action_prev_tab(self) -> None:
        idx = ["video", "audio", "image"].index(self.current_media)
        self._show_media_options(["video", "audio", "image"][(idx - 1) % 3])

    def action_focus_next(self) -> None:
        if self.url_input.has_focus:
            self.focus_index = 0
            self.buttons[0].focus()
        else:
            self.focus_index = (self.focus_index + 1) % len(self.buttons)
            self.buttons[self.focus_index].focus()
        self._update_button_focus()

    def action_focus_prev(self) -> None:
        if self.url_input.has_focus:
            return
        self.focus_index = (self.focus_index - 1) % len(self.buttons)
        self.buttons[self.focus_index].focus()
        self._update_button_focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        url = event.value.strip()
        if url:
            is_valid = self._validate_url(url)
            if is_valid:
                self.url_validation.update("[green]✓ URL válida[/green]")
            else:
                self.url_validation.update("[yellow] URL no reconocida[/yellow]")
        else:
            self.url_validation.update("")

    def _validate_url(self, url: str) -> bool:
        patterns = [
            r'(https?://)?(www\.)?(youtube|youtu)\.(com|be)/.+$',
            r'(https?://)?(www\.)?vimeo\.com/.+$',
            r'(https?://)?(www\.)?tiktok\.com/.+$',
            r'(https?://)?(www\.)?twitter\.com/.+$',
            r'(https?://)?(www\.)?instagram\.com/.+$',
            r'(https?://)?(www\.)?facebook\.com/.+$',
            r'(https?://)?(www\.)?dailymotion\.com/.+$',
            r'(https?://)?(www\.)?twitch\.tv/.+$',
            r'(https?://)?(www\.)?pinterest\.com/.+$',
            r'(https?://)?pin\.it/.+$',
        ]
        return any(re.match(p, url) for p in patterns)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download_btn":
            self.action_download()
        elif event.button.id == "clear_btn":
            self.action_clear()
        elif event.button.id == "paste_btn":
            self._paste()
        elif event.button.id == "sites_btn":
            self.action_sites()
        elif event.button.id == "history_btn":
            self.action_history()
        elif event.button.id == "settings_btn":
            self.action_settings()
        elif event.button.id == "tab_video":
            self._show_media_options("video")
        elif event.button.id == "tab_audio":
            self._show_media_options("audio")
        elif event.button.id == "tab_image":
            self._show_media_options("image")

    def on_button_focus(self, event) -> None:
        for i, btn in enumerate(self.buttons):
            if btn == event.widget:
                self.focus_index = i
                self._update_button_focus()
                break

    def _paste(self) -> None:
        try:
            import pyperclip
            text = pyperclip.paste()
            self.url_input.value = text
            self.url_input.cursor_position = len(self.url_input.value)
            if text.strip() and self._validate_url(text.strip()):
                self.app.push_screen(QualityDetectionModal(text.strip()))
        except ImportError:
            self.notify("Instala pyperclip: pip install pyperclip", severity="error")

    def action_paste(self) -> None:
        self._paste()

    def action_copy(self) -> None:
        try:
            import pyperclip
            pyperclip.copy(self.url_input.value)
            self.notify("Copiado al portapapeles", severity="information")
        except ImportError:
            self.notify("Instala pyperclip", severity="error")

    def action_clear(self) -> None:
        self.url_input.value = ""
        self.status.update("")
        self.progress_bar.progress = 0
        self.log_widget.clear()
        self.url_validation.update("")
        self.url_input.focus()

    def action_download(self) -> None:
        url = self.url_input.value.strip()
        if not url:
            self.status.update("[red] Ingresa una URL[/red]")
            return
        if self.downloading:
            return

        use_cookies = COOKIES_FILE.exists()
        if not use_cookies:
            self.notify(
                "Sin cookies.txt: contenido publico OK, pero fallaran privados/edad-restringidos (YouTube, FB, IG, Twitter, streaming de pago)",
                severity="warning",
                timeout=8
            )

        fmt, quality = self._get_selected_format()
        self.downloading = True
        self.download_btn.disabled = True
        self.download_btn.label = "Descargando..."
        self.status.update(f"[yellow]Iniciando descarga ({self.current_media})...[/yellow]")
        self.progress_bar.progress = 0
        self.log_widget.clear()
        self.log_widget.write_line(f"[cyan]URL:[/cyan] {url}")
        self.log_widget.write_line(f"[cyan]Tipo:[/cyan] {self.current_media.upper()}")
        self.log_widget.write_line(f"[cyan]Formato:[/cyan] {fmt}")
        self.log_widget.write_line(f"[cyan]Calidad:[/cyan] {quality}")
        self.log_widget.write_line(f"[cyan]Destino:[/cyan] {DOWNLOAD_DIR}")
        self.log_widget.write_line("---")

        self.run_worker(self._do_download(url, use_cookies, fmt, quality), exclusive=True)

    def _get_selected_format(self) -> tuple[str, str]:
        if self.current_media == "video":
            fmt = config.get("video_quality", "bestvideo+bestaudio/best")
            return fmt, "auto"
        elif self.current_media == "audio":
            fmt = config.get("audio_format", "m4a")
            quality = config.get("audio_quality", "0")
            return fmt, quality
        elif self.current_media == "image":
            fmt = config.get("image_format", "jpg")
            return fmt, "original"
        return "bestvideo+bestaudio/best", "auto"

    async def _do_download(self, url: str, use_cookies: bool, fmt: str, quality: str) -> None:
            try:
                cmd = [sys.executable, '-m', 'yt_dlp']

                if self.current_media == 'video':
                    cmd.extend(['--format', fmt, '--merge-output-format', 'mp4'])
                elif self.current_media == 'audio':
                    cmd.extend([
                        '--format', 'bestaudio/best',
                        '--extract-audio', '--audio-format', fmt,
                        '--audio-quality', quality,
                    ])
                elif self.current_media == 'image':
                    if 'pinterest.com' in url or 'pin.it' in url:
                        cmd.extend(['--format', 'best'])
                    else:
                        cmd.extend([
                            '--format', fmt,
                            '--write-thumbnail', '--convert-thumbnails', fmt,
                        ])

                if use_cookies:
                    cmd.extend(['--cookies', str(COOKIES_FILE)])

                cmd.extend([
                    '--ffmpeg-location', str(FFMPEG_DIR),
                    '--output', str(DOWNLOAD_DIR / '%(playlist_index)s - %(title)s.%(ext)s'),
                    '--no-warnings',
                    '--newline',
                    url
                ])

                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(SCRIPT_DIR)
                )

                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    files = list(DOWNLOAD_DIR.glob('*'))
                    if files:
                        latest = max(files, key=lambda f: f.stat().st_mtime)
                        self.status.update('[green]Descarga completada[/green]')
                        self.log_widget.write_line(f'[green]Archivo:[/green] {latest}')
                        self.app.notify(f'Descarga completada: {latest.name}', severity='information')
                    else:
                        self.status.update('[green]Descarga completada[/green]')
                        self.app.notify('Descarga completada', severity='information')
                    self.progress_bar.progress = 100
                else:
                    error_text = stderr.decode(errors='ignore') if stderr else 'Error desconocido'
                    error = classify_error(error_text)
                    self.status.update(f'[red]{error.message}[/red]')
                    self.log_widget.write_line(f'[red]{error.message}[/red]')
                    self.log_widget.write_line(f'[yellow]Sugerencia:[/yellow] {error.suggestion}')
                    self.app.notify(f'{error.message}: {error.suggestion}', severity='error')

            except asyncio.CancelledError:
                self.status.update('[yellow]Descarga cancelada[/yellow]')
            except Exception as e:
                error = classify_error(str(e))
                self.status.update(f'[red]{error.message}[/red]')
                self.log_widget.write_line(f'[red]{error.message}[/red]')
                self.log_widget.write_line(f'[yellow]Sugerencia:[/yellow] {error.suggestion}')
            finally:
                self.downloading = False
                self.download_btn.disabled = False
                self.download_btn.label = 'Descargar (Enter)'

        def action_history(self) -> None:
                self.app.push_screen(HistoryScreen())
            def action_settings(self) -> None:
            self.app.push_screen(SettingsScreen())
            def action_sites(self) -> None:
        def action_sites(self) -> None:
            def action_quit(self) -> None:
        def action_quit(self) -> None:

        class SitesScreen(Screen):
            BINDINGS = [
                Binding("escape", "go_back", "Volver"),
                Binding("up", "cursor_up", "Arriba"),
                Binding("down", "cursor_down", "Abajo"),
            ]

            def compose(self) -> ComposeResult:
                yield Header(show_clock=True)
                yield Container(
                    Static("[bold]Sitios Compatibles (1000+)[/bold]", classes="title"),
                    Static(SITES_LIST, classes="sites-content"),
                    Static("[dim]ESC: Volver  |  Flechas: Scroll[/dim]", classes="nav-hint"),
                    classes="main-container"
                )
                yield Footer()

            def action_go_back(self) -> None:
                self.app.pop_screen()


        class HistoryScreen(Screen):
            BINDINGS = [
                Binding("escape", "go_back", "Volver"),
                Binding("r", "refresh", "Actualizar"),
                Binding("delete", "delete_file", "Eliminar"),
                Binding("up", "cursor_up", "Arriba"),
                Binding("down", "cursor_down", "Abajo"),
            ]

            def compose(self) -> ComposeResult:
                yield Header(show_clock=True)
                yield Container(
                    Static("[bold]Historial de Descargas[/bold]", classes="title"),
                    DataTable(id="history_table", cursor_type="row"),
                    Static("[dim]ESC: Volver  |  R: Actualizar  |  Del: Eliminar  |  Flechas: Navegar[/dim]", classes="nav-hint"),
                    classes="main-container"
                )
                yield Footer()

            def on_mount(self) -> None:
                self.table = self.query_one("#history_table", DataTable)
                self.table.add_columns("Fecha", "Archivo", "Tamaño")
                self.action_refresh()

            def action_refresh(self) -> None:
                self.table.clear()
                if DOWNLOAD_DIR.exists():
                    files = sorted(DOWNLOAD_DIR.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
                    for f in files[:100]:
                        stat = f.stat()
                        date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                        size = self._format_size(stat.st_size)
                        self.table.add_row(date, f.name, size)

            def _format_size(self, bytes_: int) -> str:
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if bytes_ < 1024:
                        return f"{bytes_:.1f} {unit}"
                    bytes_ /= 1024
                return f"{bytes_:.1f} TB"

            def action_delete_file(self) -> None:
                if self.table.cursor_row is not None:
                    row = self.table.get_row_at(self.table.cursor_row)
                    if row:
                        filename = row[1]
                        filepath = DOWNLOAD_DIR / filename
                        if filepath.exists():
                            try:
                                filepath.unlink()
                                self.action_refresh()
                                self.app.notify(f"Eliminado: {filename}", severity="information")
                            except Exception as e:
                                self.app.notify(f"Error: {e}", severity="error")

            def action_go_back(self) -> None:
                self.app.pop_screen()


        class SettingsScreen(Screen):
            BINDINGS = [
                Binding("escape", "go_back", "Volver"),
                Binding("up", "cursor_up", "Arriba"),
                Binding("down", "cursor_down", "Abajo"),
                Binding("a", "accessibility", "Accesibilidad"),
                Binding("c", "credits", "Creditos"),
            ]

            def compose(self) -> ComposeResult:
                yield Header(show_clock=True)
                yield Container(
                    Static("[bold]Configuracion[/bold]", classes="title"),
                    Vertical(
                        Label("[bold]Carpeta de descargas:[/bold]"),
                        Input(value=str(DOWNLOAD_DIR), id="download_dir_input", placeholder="Ruta de descargas"),
                        Label("[bold]Archivo de cookies:[/bold]"),
                        Input(value=str(COOKIES_FILE), id="cookies_file_input", placeholder="Ruta cookies.txt"),
                        Label("[bold]Directorio FFmpeg:[/bold]"),
                        Input(value=str(FFMPEG_DIR), id="ffmpeg_dir_input", placeholder="Ruta ffmpeg"),
                        Label(""),
                        Label("[bold]Tema:[/bold]"),
                        OptionList(
                            Option("Oscuro (textual-dark)", id="dark"),
                            Option("Claro (textual-light)", id="light"),
                            Option("Sistema (textual-ansi)", id="system"),
                            id="theme_selector"
                        ),
                        Label(""),
                        Horizontal(
                            Button("Guardar", variant="primary", id="save_config"),
                            Button("Restablecer", variant="default", id="reset_config"),
                            classes="button-group"
                        ),
                        Label(""),
                        Horizontal(
                            Button("Verificar cookies", id="check_cookies"),
                            Button("Abrir carpeta descargas", id="open_folder"),
                            Button("Probar ffmpeg", id="test_ffmpeg"),
                            classes="button-group"
                        ),
                        Label(""),
                        Horizontal(
                            Button("Accesibilidad (A)", id="accessibility_btn"),
                            Button("Creditos (C)", id="credits_btn"),
                            classes="button-group"
                        ),
                        classes="settings-list"
                    ),
                    Static("", id="config_status", classes="status"),
                    Static("[dim]ESC: Volver  |  A: Accesibilidad  |  C: Creditos  |  Flechas: Navegar[/dim]", classes="nav-hint"),
                    classes="main-container"
                )
                yield Footer()

            def on_mount(self) -> None:
                self.config_status = self.query_one("#config_status", Static)
                self.theme_selector = self.query_one("#theme_selector", OptionList)
                # Set current theme
                theme_to_index = {"textual-dark": 0, "textual-light": 1, "textual-ansi": 2}
                current_theme = config.get("theme", "textual-dark")
                if current_theme in theme_to_index:
                    self.theme_selector.highlighted = theme_to_index[current_theme]

            def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
                if event.option_list.id == "theme_selector":
                    theme_map = {"dark": "textual-dark", "light": "textual-light", "system": "textual-ansi"}
                    theme = theme_map.get(event.option.id, "textual-dark")
                    config["theme"] = theme
                    self.app.theme = theme
                    self.app.notify(f"Tema: {event.option.prompt}", severity="information")

            def on_button_pressed(self, event: Button.Pressed) -> None:
                if event.button.id == "check_cookies":
                    self._check_cookies()
                elif event.button.id == "open_folder":
                    self._open_folder()
                elif event.button.id == "test_ffmpeg":
                    self._test_ffmpeg()
                elif event.button.id == "save_config":
                    self._save_config()
                elif event.button.id == "reset_config":
                    self._reset_config()
                elif event.button.id == "accessibility_btn":
                    self.action_accessibility()
                elif event.button.id == "credits_btn":
                    self.action_credits()

            def _save_config(self) -> None:
                global DOWNLOAD_DIR, COOKIES_FILE, FFMPEG_DIR, config
                config["download_dir"] = self.query_one("#download_dir_input", Input).value
                config["cookies_file"] = self.query_one("#cookies_file_input", Input).value
                config["ffmpeg_dir"] = self.query_one("#ffmpeg_dir_input", Input).value
                save_config(config)
                DOWNLOAD_DIR = Path(config["download_dir"])
                COOKIES_FILE = Path(config["cookies_file"])
                FFMPEG_DIR = Path(config["ffmpeg_dir"])
                self.config_status.update("[green]Configuracion guardada[/green]")
                self.app.notify("Configuracion guardada correctamente", severity="information")

            def _reset_config(self) -> None:
                global DOWNLOAD_DIR, COOKIES_FILE, FFMPEG_DIR, config
                config = DEFAULT_CONFIG.copy()
                save_config(config)
                DOWNLOAD_DIR = Path(config["download_dir"])
                COOKIES_FILE = Path(config["cookies_file"])
                FFMPEG_DIR = Path(config["ffmpeg_dir"])
                self.query_one("#download_dir_input", Input).value = str(DOWNLOAD_DIR)
                self.query_one("#cookies_file_input", Input).value = str(COOKIES_FILE)
                self.query_one("#ffmpeg_dir_input", Input).value = str(FFMPEG_DIR)
                self.theme_selector.highlighted = "dark"
                self.app.theme = "textual-dark"
                config["theme"] = "textual-dark"
                self.config_status.update("[green]Configuracion restablecida[/green]")
                self.app.notify("Configuracion restablecida a valores por defecto", severity="information")

            def _check_cookies(self) -> None:
                if COOKIES_FILE.exists():
                    lines = COOKIES_FILE.read_text(encoding="utf-8", errors="ignore").strip().split("\n")
                    cookie_lines = [l for l in lines if l and not l.startswith("#")]
                    self.config_status.update(f"[green]cookies.txt ({len(cookie_lines)} cookies)[/green]")
                else:
                    self.config_status.update("[red]cookies.txt NO encontrado[/red]")

            def _open_folder(self) -> None:
                try:
                    if sys.platform == "win32":
                        os.startfile(DOWNLOAD_DIR)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", DOWNLOAD_DIR])
                    else:
                        subprocess.run(["xdg-open", DOWNLOAD_DIR])
                    self.config_status.update("[green]Carpeta abierta[/green]")
                except Exception as e:
                    self.config_status.update(f"[red]Error: {e}[/red]")

            def _test_ffmpeg(self) -> None:
                try:
                    result = subprocess.run(
                        [str(FFMPEG_DIR / "ffmpeg.exe"), "-version"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        self.config_status.update("[green]FFmpeg OK[/green]")
                    else:
                        self.config_status.update("[red]FFmpeg no funciona[/red]")
                except Exception as e:
                    self.config_status.update(f"[red]Error: {e}[/red]")

            def action_accessibility(self) -> None:
                self.app.push_screen(AccessibilityScreen())

            def action_credits(self) -> None:
                self.app.push_screen(CreditsScreen())

            def action_go_back(self) -> None:
                self.app.pop_screen()


        class AccessibilityScreen(Screen):
            BINDINGS = [
                Binding("escape", "go_back", "Volver"),
                Binding("up", "cursor_up", "Arriba"),
                Binding("down", "cursor_down", "Abajo"),
            ]

            def compose(self) -> ComposeResult:
                yield Header(show_clock=True)
                yield Container(
                    Static("[bold]Accesibilidad - Atajos de Teclado[/bold]", classes="title"),
                    Static(ACCESSIBILITY_TEXT, classes="sites-content"),
                    Static("[dim]ESC: Volver  |  Flechas: Scroll[/dim]", classes="nav-hint"),
                    classes="main-container"
                )
                yield Footer()

            def action_go_back(self) -> None:
                self.app.pop_screen()


        class CreditsScreen(Screen):
            BINDINGS = [
                Binding("escape", "go_back", "Volver"),
                Binding("up", "cursor_up", "Arriba"),
                Binding("down", "cursor_down", "Abajo"),
            ]

            def compose(self) -> ComposeResult:
                yield Header(show_clock=True)
                yield Container(
                    Static("[bold]Creditos[/bold]", classes="title"),
                    Static(CREDITS_TEXT, classes="sites-content"),
                    Static("[dim]ESC: Volver  |  Flechas: Scroll[/dim]", classes="nav-hint"),
                    classes="main-container"
                )
                yield Footer()

            def action_go_back(self) -> None:
                self.app.pop_screen()


        class OmniumSuiteApp(App):
            TITLE = "Omnium Suite - Video Downloader"
            CSS = """
            Screen {
                background: #272822;
                color: #f8f8f2;
            }

            .ascii-logo {
                text-align: center;
                color: #ae81ff;
                padding: 1 0;
                height: 8;
                overflow: hidden;
            }

            .subtitle {
                text-align: center;
                color: #75715e;
                margin-bottom: 1;
            }

            .divider {
                color: #75715e;
                text-align: center;
                margin: 0 0 1 0;
            }

            .main-container {
                width: 100%;
                height: 100%;
                padding: 0 2;
            }

            .url-label {
                color: #f8f8f2;
                margin-top: 1;
                margin-bottom: 0;
            }

            .input-group {
                margin: 0 0 1 0;
            }

            Input {
                background: #3e3d32;
                border: solid #75715e;
                color: #f8f8f2;
                padding: 0 1;
            }

            Input:focus {
                border: solid #ae81ff;
            }

            .validation {
                height: 1;
                margin: 0 0 1 0;
            }

            .sites-hint {
                height: 2;
                margin: 0 0 1 0;
                text-align: center;
                text-wrap: wrap;
            }

            .tab-group {
                margin: 1 0;
                height: 3;
            }

            .tab-group Button {
                margin-right: 1;
                min-width: 16;
            }

            .option-group {
                margin: 1 0;
            }

            .option-group.hidden {
                display: none;
            }

            .option-label {
                color: #ae81ff;
                margin: 1 0 0 0;
            }

            OptionList {
                background: #3e3d32;
                border: solid #75715e;
                color: #f8f8f2;
                margin: 0 0 1 0;
            }

            OptionList:focus {
                border: solid #ae81ff;
            }

            OptionList > .option-list--option-highlighted {
                background: #ae81ff;
                color: #272822;
            }

            .privacy-notice {
                margin-top: 2;
                padding: 1;
                background: #1e1f1c;
                border: solid #75715e;
                text-align: center;
                text-wrap: wrap;
            }

            .nav-hint {
                margin-top: 1;
                padding: 1;
                background: #1e1f1c;
                border: solid #75715e;
                text-align: center;
                color: #75715e;
            }

            .button-group {
                margin: 1 0;
                width: 100%;
                height: auto;
            }

            .button-group Button {
                margin-right: 1;
                background: #3e3d32;
                border: solid #75715e;
                color: #f8f8f2;
            }

            .button-group Button:hover {
                background: #4e4d3e;
                border: solid #ae81ff;
            }

            .button-group Button:focus {
                background: #4e4d3e;
                border: solid #ae81ff;
            }

            .button-group Button.focused {
                background: #4e4d3e;
                border: solid #ae81ff;
            }

            .button-group Button.-primary {
                background: #ae81ff;
                border: solid #ae81ff;
                color: #272822;
            }

            .button-group Button.-primary:hover {
                background: #cc99ff;
                border: solid #cc99ff;
            }

            .status {
                margin: 1 0;
                height: 1;
            }

            #progress {
                margin: 1 0;
                background: #3e3d32;
                color: #ae81ff;
            }

            .log {
                height: 18;
                background: #1e1f1c;
                border: solid #75715e;
                color: #f8f8f2;
                margin-top: 1;
                padding: 1;
            }

            .title {
                text-align: center;
                color: #ae81ff;
                padding: 1;
                margin-bottom: 1;
            }

            .settings-list {
                margin: 1 0;
            }

            .settings-list Label {
                margin-top: 1;
                color: #ae81ff;
            }

            .config-value {
                padding-left: 2;
                color: #75715e;
                overflow: hidden;
            }

            .sites-content {
                padding: 1 2;
                color: #f8f8f2;
                overflow-y: auto;
                height: 100%;
            }

            DataTable {
                height: 100%;
                background: #272822;
            }

            DataTable > .datatable--header {
                background: #3e3d32;
                color: #ae81ff;
                text-style: bold;
            }

            DataTable > .datatable--cursor {
                background: #ae81ff;
                color: #272822;
            }

            .dialog {
                width: 60;
                height: auto;
                padding: 2;
                border: solid #ae81ff;
                background: #3e3d32;
            }

            .dialog-title {
                text-align: center;
                color: #ae81ff;
                margin-bottom: 1;
            }

            .dialog-message {
                text-align: center;
                color: #f8f8f2;
                margin-bottom: 2;
            }

            .dialog-buttons {
                width: 100%;
            }

            .dialog-buttons Button {
                margin: 0 1;
            }

            Header {
                background: #272822;
                color: #75715e;
                border: solid #75715e;
                height: 1;
            }

            Footer {
                background: #272822;
                color: #75715e;
                border: solid #75715e;
            }

            Footer .key {
                color: #ae81ff;
            }

            Collapsible {
                border: solid #75715e;
                background: #272822;
            }

            Collapsible.-collapsed {
                border: solid #75715e;
            }

            CollapsibleTitle {
                color: #ae81ff;
                background: #3e3d32;
            }
            """

            BINDINGS = [
                Binding("q", "quit", "Salir", show=True),
            ]

            def on_mount(self) -> None:
                self.push_screen(MainScreen())

            def action_quit(self) -> None:
                self.exit()


def main():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app = OmniumSuiteApp()
    app.run()


if __name__ == "__main__":
    main()