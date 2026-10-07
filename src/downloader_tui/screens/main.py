"""Pantalla principal con input URL, tabs y botones."""

import asyncio
import re
import time
from typing import Literal

import pyperclip
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Collapsible,
    Footer,
    Header,
    Input,
    ProgressBar,
    RichLog,
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
from downloader_tui.services.downloader import DownloadProgress, run_download
from downloader_tui.utils import formatear_bytes, formatear_eta, formatear_velocidad

MediaType = Literal["video", "audio", "image"]


class MainScreen(BaseScreen):
    """Pantalla principal: input URL, tabs Video/Audio/Imagen, botones."""

    # AUTO_FOCUS vacio y el umbral de centrado vertical vienen de BaseScreen.
    # Aqui el foco lo pone _initial_focus, que no desplaza el area.

    BINDINGS = [
        Binding("escape", "quit", "Salir"),
        Binding("enter", "download", "Descargar"),
        Binding("ctrl+v", "paste", "Pegar"),
        # Ctrl+C copia el LOG, que es lo que se quiere casi siempre (por ejemplo
        # para pegarlo en un informe). Copiar la URL pasa a Ctrl+U.
        Binding("ctrl+c", "copiar_log", "Copiar log"),
        Binding("ctrl+u", "copy", "Copiar URL"),
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
        # El logo va DENTRO del area desplazable, como parte del bloque, para que
        # se centre junto al formulario: antes vivia fuera y quedaba clavado
        # arriba mientras el resto flotaba, que es lo que hacia la composicion
        # cabecera-pesada.
        yield Header(show_clock=True)
        # La columna del formulario se centra con esta envoltura intermedia.
        # Con hermanos presentes (Header, Footer), el align-horizontal del Screen
        # deja de centrar (medido: el contenedor quedaba en x=0 a 120 columnas);
        # el hijo unico de esta envoltura si se centra.
        yield Vertical(
            Container(
                # Espaciadores elasticos: se reparten el alto sobrante arriba y
                # abajo a partes iguales, asi que el bloque queda centrado
                # verticalmente en vez de amontonado arriba. Cuando no sobra
                # altura (80x24) se quedan en 0 y el area solo se desplaza.
                Static("", classes="relleno-flexible"),
                Static(ASCII_LOGO, classes="ascii-logo"),
                Vertical(
                    Input(
                        placeholder="Pegar enlace aquí...",
                        id="url_input"
                    ),
                    Static("", id="url_validation", classes="validation"),
                    Static(
                        "[dim]Instagram, TikTok, YouTube, X, Facebook, Reddit, Pinterest, SoundCloud y 1000+ sitios[/dim]",
                        classes="sites-hint"
                    ),
                    classes="input-group"
                ),
                Static("-" * 200, classes="divider"),
                # Cada fila a centrar lleva su propia envoltura: con varios
                # hermanos, el align-horizontal del contenedor padre NO centra al
                # hijo (comprobado con una prueba minima); el hijo unico de esta
                # envoltura si.
                Vertical(
                    Horizontal(
                        Button("Video", id="tab_video", variant="primary"),
                        Button("Audio", id="tab_audio", variant="default"),
                        Button("Imagen", id="tab_image", variant="default"),
                        classes="tab-group"
                    ),
                    classes="fila-centrada",
                ),
                Static("-" * 200, classes="divider"),
                # Etiquetas cortas a proposito: con los textos largos
                # ("Descargar (Enter)" = 21 columnas) la fila medía 113 columnas
                # y a 80 los botones Historial y Config quedaban fuera de
                # pantalla, sin forma de pulsarlos con el raton. Los atajos
                # siguen en el pie y en la pantalla de Accesibilidad (A).
                Vertical(
                    Horizontal(
                        Button("Descargar", variant="primary", id="download_btn"),
                        Button("Limpiar", variant="default", id="clear_btn"),
                        Button("Pegar", variant="default", id="paste_btn"),
                        Button("Sitios", variant="default", id="sites_btn"),
                        Button("Historial", variant="default", id="history_btn"),
                        Button("Config", variant="default", id="settings_btn"),
                        classes="button-group"
                    ),
                    classes="fila-centrada",
                ),
                Static("", id="status", classes="status"),
                Vertical(
                    ProgressBar(total=100, show_eta=False, id="progress"),
                    classes="fila-centrada",
                ),
                Collapsible(
                    # RichLog, no Log: el widget Log solo acepta texto plano y
                    # escribia el markup tal cual ("[cyan]URL:[/cyan] ..." se veia
                    # literal en pantalla). RichLog con markup=True interpreta el
                    # color, y wrap=True evita tener que desplazar en horizontal.
                    RichLog(
                        id="download_log",
                        classes="log",
                        wrap=True,
                        markup=True,
                    ),
                    title="Log de descarga",
                    collapsed=True,
                    id="log_collapsible"
                ),
                Static(
                    "[dim]Privacidad: Esta herramienta se ejecuta 100% en tu equipo. No se envian datos, URLs, ni credenciales a servidores externos. "
                    "Solo yt-dlp (local) contacta directamente al sitio de origen para descargar el contenido que tu solicitas.[/dim]",
                    classes="privacy-notice"
                ),
                Static("", classes="relleno-flexible"),
                classes="main-container"
            ),
            classes="composer-area",
        )
        yield Footer()

    def on_mount(self) -> None:
        logger.info("MainScreen mounted")
        self.url_input = self.query_one("#url_input", Input)
        self.url_validation = self.query_one("#url_validation", Static)
        self.progress_bar = self.query_one("#progress", ProgressBar)
        self.status = self.query_one("#status", Static)
        self.log_widget = self.query_one("#download_log", RichLog)
        self.download_btn = self.query_one("#download_btn", Button)
        self._ajustar_espaciadores(self.size.height)

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
        self._ultimo_aviso = 0.0
        self._lineas_log: list[str] = []
        self._update_button_focus()
        self._show_media_options("video")
        # No enfocamos el input aqui: durante on_mount el layout todavia mide 0,
        # Textual cree que no se ve, desplaza el contenedor y el logo acaba
        # fuera de pantalla (region y=-4 medido). Lo enfocamos tras el primer
        # refresco, cuando el input ya esta visible y no hace falta desplazar.
        self.call_after_refresh(self._initial_focus)

    def _initial_focus(self) -> None:
        self.query_one(".main-container").scroll_y = 0
        # scroll_visible=False: focus() encola el desplazamiento con call_later,
        # asi que un focus normal volveria a mover el contenedor despues de este
        # metodo y el logo se iria de pantalla. El input ya esta a la vista.
        self.url_input.focus(scroll_visible=False)

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
        if not url:
            self.url_validation.update("")
        elif not self._parece_url(url):
            self.url_validation.update("[red]No parece una URL[/red]")
        elif self._validate_url(url):
            self.url_validation.update("[green]Sitio conocido[/green]")
        else:
            # yt-dlp soporta mas de 1000 sitios: que uno no este en la lista de
            # _validate_url no lo invalida. Antes se respondia "URL no
            # reconocida" a cualquier sitio no listado, aunque fuera valido.
            self.url_validation.update(
                "[yellow]Sitio no verificado: se intentara igual[/yellow]"
            )

    @staticmethod
    def _parece_url(url: str) -> bool:
        """Tiene pinta de URL, sin exigir que sea de un sitio de la lista."""
        if url.lower().startswith(("http://", "https://")):
            return True
        return bool(re.match(r"^[\w.-]+\.[a-z]{2,}(/|$|\?|#)", url, re.IGNORECASE))

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
            self.notify("URL copiada al portapapeles", severity="information")
        except ImportError:
            self.notify("Instala pyperclip", severity="error")

    def _escribir_log(self, texto: str) -> None:
        """Anade una linea al log visible y al buffer que se puede copiar.

        Al buffer va el texto SIN markup: si se copiara el crudo, al pegarlo en
        un informe aparecerian las etiquetas [cyan]/[red] en medio.
        """
        self._lineas_log.append(Text.from_markup(texto).plain)
        self.log_widget.write(texto)

    def _texto_del_log(self) -> str:
        return "\n".join(self._lineas_log)

    def action_copiar_log(self) -> None:
        """Copia el log al portapapeles (Ctrl+C).

        Se copia del buffer propio y no del widget a proposito: el log arranca
        colapsado y RichLog no materializa sus lineas hasta que tiene tamano, asi
        que leer del widget devolveria vacio justo cuando hace falta.
        """
        texto = self._texto_del_log().strip()
        if not texto:
            self.notify("Todavia no hay nada en el log", severity="warning")
            return
        try:
            pyperclip.copy(texto)
            self.notify(
                f"Log copiado ({len(self._lineas_log)} lineas)",
                severity="information",
            )
        except Exception as e:
            self.notify(f"No se pudo copiar: {e}", severity="error")

    def action_clear(self) -> None:
        self.url_input.value = ""
        self.status.update("")
        self.progress_bar.progress = 0
        self.log_widget.clear()
        self._lineas_log.clear()
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
        self._preparar_log_descarga(url, fmt, quality)

        self.run_worker(self._do_download(url, use_cookies, fmt, quality), exclusive=True)

    def _preparar_log_descarga(self, url: str, fmt: str, quality: str) -> None:
        """Deja el log listo y DESPLEGADO al iniciar una descarga.

        Se despliega al empezar, no solo al fallar: durante la descarga es donde
        se ve que esta pasando, y al terminar queda como registro, tanto si salio
        bien como si no. Se separa de action_download para poder probarlo sin
        lanzar ninguna descarga de verdad.
        """
        self.log_widget.clear()
        self._lineas_log.clear()
        self._escribir_log(f"[cyan]URL:[/cyan] {url}")
        self._escribir_log(f"[cyan]Tipo:[/cyan] {self.current_media.upper()}")
        self._escribir_log(f"[cyan]Formato:[/cyan] {fmt}")
        self._escribir_log(f"[cyan]Calidad:[/cyan] {quality}")
        self._escribir_log(f"[cyan]Destino:[/cyan] {get_download_dir()}")
        self._escribir_log("---")
        self.query_one("#log_collapsible", Collapsible).collapsed = False

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

    def _actualizar_progreso(self, avance: DownloadProgress) -> None:
        """Refresca la barra y la linea de estado con cada aviso de yt-dlp.

        La barra se actualiza en cada aviso (es barato y Textual agrupa los
        refrescos de pantalla); la linea de estado se limita a ~3 por segundo
        para que no parpadee ni ensucie el log.
        """
        if avance.porcentaje is not None:
            self.progress_bar.progress = avance.porcentaje

        ahora = time.monotonic()
        if ahora - self._ultimo_aviso < 0.35:
            return
        self._ultimo_aviso = ahora

        partes: list[str] = []
        if avance.porcentaje is not None:
            partes.append(f"{avance.porcentaje:.1f}%")
        if avance.descargado is not None and avance.total is not None:
            partes.append(
                f"{formatear_bytes(avance.descargado)} de {formatear_bytes(avance.total)}"
            )
        velocidad = formatear_velocidad(avance.velocidad)
        if velocidad:
            partes.append(velocidad)
        eta = formatear_eta(avance.eta)
        if eta:
            partes.append(f"faltan {eta}")
        if partes:
            self.status.update("[yellow]Descargando: " + " | ".join(partes) + "[/yellow]")

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
                on_progress=self._actualizar_progreso,
            )

            logger.info(f"Download result: success={result.success}, file={result.file_path}, error={result.error}")
            if result.success:
                if result.file_path:
                    self.status.update("[green]Descarga completada[/green]")
                    self._escribir_log(f"[green]Archivo:[/green] {result.file_path}")
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
                self._escribir_log(f"[red]{error.message}[/red]")
                self._escribir_log(f"[yellow]Sugerencia:[/yellow] {error.suggestion}")
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
                message=f"{type(e).__name__}: {e}",
                suggestion="Revisa el log en logs/ para el detalle completo"
            )
            self.status.update(f"[red]{error.message}[/red]")
            self._escribir_log(f"[red]{error.message}[/red]")
            self._escribir_log(f"[yellow]Sugerencia:[/yellow] {error.suggestion}")
            self.app.notify(f"{error.message}: {error.suggestion}", severity="error")
            log_collapsible = self.query_one("#log_collapsible", Collapsible)
            log_collapsible.collapsed = False
        finally:
            self.downloading = False
            self.download_btn.disabled = False
            self.download_btn.label = "Descargar"

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
