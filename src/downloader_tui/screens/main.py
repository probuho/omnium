"""Pantalla principal con input URL, tabs y botones."""

import asyncio
import re
from typing import Literal

import pyperclip
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Collapsible,
    Footer,
    Header,
    Input,
    Log,
    ProgressBar,
    Static,
)

from downloader_tui.config import (
    get_audio_format,
    get_audio_quality,
    get_download_dir,
    get_image_format,
    get_video_quality,
    load_config,
)
from downloader_tui.constants import ASCII_LOGO
from downloader_tui.logger import logger
from downloader_tui.models.errors import DownloadError, ErrorCategory
from downloader_tui.screens.base import BaseScreen
from downloader_tui.screens.modals import QualityDetectionModal
from downloader_tui.services.downloader import run_download

MediaType = Literal["video", "audio", "image"]


class MainScreen(BaseScreen):
    """Pantalla principal: input URL, tabs Video/Audio/Imagen, botones."""

    BINDINGS = [
        Binding("escape", "quit", "Salir"),
        Binding("enter", "download", "Descargar"),
        Binding("ctrl+v", "paste", "Pegar"),
        Binding("ctrl+c", "copy", "Copiar"),
        Binding("ctrl+l", "clear", "Limpiar"),
        Binding("h", "history", "Historial"),
        Binding("s", "settings", "Config"),
        Binding("i", "sites", "Sitios"),
        Binding("tab", "next_tab", "Pestana sig."),
        Binding("shift+tab", "prev_tab", "Pestana ant."),
        Binding("up", "focus_prev", "Anterior"),
        Binding("down", "focus_next", "Siguiente"),
        Binding("left", "cursor_left", "Izquierda"),
        Binding("right", "cursor_right", "Derecha"),
    ]

    MEDIA_TYPES: list[tuple[MediaType, str]] = [
        ("video", "Video"),
        ("audio", "Audio"),
        ("image", "Imagen"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(ASCII_LOGO, classes="ascii-logo"),
            Static("=" * 80, classes="divider"),
            Vertical(
                Static("[bold]URL:[/bold]", classes="url-label"),
                Input(
                    placeholder="https://youtube.com/watch?v=...",
                    id="url_input"
                ),
                Static("", id="url_validation", classes="validation"),
                Static(
                    "[dim]Funciona con: posts, stories, reels, videos, audio, imagenes de Instagram, TikTok, YouTube, Twitter/X, Facebook, Reddit, Pinterest, SoundCloud, Bandcamp y 1000+ sitios[/dim]",
                    classes="sites-hint"
                ),
                classes="input-group"
            ),
            Static("-" * 80, classes="divider"),
            Horizontal(
                Button("Video", id="tab_video", variant="primary"),
                Button("Audio", id="tab_audio", variant="default"),
                Button("Imagen", id="tab_image", variant="default"),
                classes="tab-group"
            ),
            Static("[dim]Calidad y formato se configuran en Config (S)[/dim]", classes="sites-hint"),
            Static("-" * 80, classes="divider"),
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
                collapsed=False,
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
        logger.info("MainScreen mounted")
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
        self.current_media: MediaType = "video"
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

    def _show_media_options(self, media: MediaType) -> None:
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

    def action_cursor_left(self) -> None:
        if self.url_input.has_focus:
            return
        self.focus_index = (self.focus_index - 1) % len(self.buttons)
        self.buttons[self.focus_index].focus()
        self._update_button_focus()

    def action_cursor_right(self) -> None:
        if self.url_input.has_focus:
            self.focus_index = (self.focus_index + 1) % len(self.buttons)
            self.buttons[self.focus_index].focus()
            self._update_button_focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        url = event.value.strip()
        logger.debug(f"Input changed: {url[:50]}...")
        if url:
            is_valid = self._validate_url(url)
            if is_valid:
                self.url_validation.update("[green]URL valida[/green]")
            else:
                self.url_validation.update("[yellow]URL no reconocida[/yellow]")
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
        logger.info(f"Button pressed: {event.button.id}")
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
            if btn is event.widget:
                self.focus_index = i
                self._update_button_focus()
                break

    def _paste(self) -> None:
        try:
            text = pyperclip.paste().strip()
            if text and self._validate_url(text):
                self.url_input.value = text
                self.url_input.cursor_position = len(text)
                # Abrir modal de detección de calidades
                self.app.push_screen(QualityDetectionModal(text, self.current_media))
            elif text:
                self.url_input.value = text
                self.url_input.cursor_position = len(text)
        except ImportError:
            self.notify("Instala pyperclip: pip install pyperclip", severity="error")

    def action_paste(self) -> None:
        self._paste()

    def action_copy(self) -> None:
        try:
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
        logger.info(f"Download requested for: {url[:80]}")
        if not url:
            self.status.update("[red] Ingresa una URL[/red]")
            return
        if self.downloading:
            return

        use_cookies = load_config().get("use_cookies", True)

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
        self.log_widget.write_line(f"[cyan]Destino:[/cyan] {get_download_dir()}")
        self.log_widget.write_line("---")

        self.run_worker(self._do_download(url, use_cookies, fmt, quality), exclusive=True)

    def _get_selected_format(self) -> tuple[str, str]:
        if self.current_media == "video":
            fmt = get_video_quality()
            return fmt, "auto"
        elif self.current_media == "audio":
            fmt = get_audio_format()
            quality = get_audio_quality()
            return fmt, quality
        elif self.current_media == "image":
            fmt = get_image_format()
            return fmt, "original"
        return get_video_quality(), "auto"

    async def _do_download(self, url: str, use_cookies: bool, fmt: str, quality: str) -> None:
        logger.info(f"Starting download: url={url[:80]}, media={self.current_media}, fmt={fmt}, quality={quality}")
        try:
            result = await run_download(
                url=url,
                media_type=self.current_media,
                use_cookies=use_cookies,
                video_quality=fmt if self.current_media == "video" else None,
                audio_format=fmt if self.current_media == "audio" else None,
                audio_quality=quality if self.current_media == "audio" else None,
                image_format=fmt if self.current_media == "image" else None,
            )

            logger.info(f"Download result: success={result.success}, file={result.file_path}, error={result.error}")
            if result.success:
                if result.file_path:
                    self.status.update("[green]Descarga completada[/green]")
                    self.log_widget.write_line(f"[green]Archivo:[/green] {result.file_path}")
                    self.app.notify(f"Descarga completada: {result.file_path.name}", severity="information")
                else:
                    self.status.update("[green]Descarga completada[/green]")
                    self.app.notify("Descarga completada", severity="information")
                self.progress_bar.progress = 100
            else:
                error = result.error or DownloadError(
                    category=ErrorCategory.UNKNOWN,
                    message="Error desconocido",
                    suggestion="Revisa el log para mas detalles"
                )
                self.status.update(f"[red]{error.message}[/red]")
                self.log_widget.write_line(f"[red]{error.message}[/red]")
                self.log_widget.write_line(f"[yellow]Sugerencia:[/yellow] {error.suggestion}")
                self.app.notify(f"{error.message}: {error.suggestion}", severity="error")
                # Auto-expand log to show error
                log_collapsible = self.query_one("#log_collapsible", Collapsible)
                log_collapsible.collapsed = False

        except asyncio.CancelledError:
            logger.warning("Download cancelled")
            self.status.update("[yellow]Descarga cancelada[/yellow]")
        except Exception as e:
            logger.exception(f"Download failed: {e}")
            error = DownloadError(
                category=ErrorCategory.UNKNOWN,
                message=str(e),
                suggestion="Revisa el log para mas detalles"
            )
            self.status.update(f"[red]{error.message}[/red]")
            self.log_widget.write_line(f"[red]{error.message}[/red]")
            self.log_widget.write_line(f"[yellow]Sugerencia:[/yellow] {error.suggestion}")
            self.app.notify(f"{error.message}: {error.suggestion}", severity="error")
            log_collapsible = self.query_one("#log_collapsible", Collapsible)
            log_collapsible.collapsed = False
        finally:
            self.downloading = False
            self.download_btn.disabled = False
            self.download_btn.label = "Descargar (Enter)"

    def action_sites(self) -> None:
        logger.info("Navigating to SitesScreen")
        from .sites import SitesScreen
        self.app.push_screen(SitesScreen())

    def action_history(self) -> None:
        logger.info("Navigating to HistoryScreen")
        from .history import HistoryScreen
        self.app.push_screen(HistoryScreen())

    def action_settings(self) -> None:
        from .settings import SettingsScreen
        self.app.push_screen(SettingsScreen())

    def action_quit(self) -> None:
        self.app.exit()
