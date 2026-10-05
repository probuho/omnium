"""Pantalla de configuración."""

from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, OptionList, Static
from textual.widgets._option_list import Option

from downloader_tui.config import (
    DEFAULT_CONFIG,
    get_download_dir,
    load_config,
    save_config,
)
from downloader_tui.screens.base import BaseScreen
from downloader_tui.services.cookies import validate_cookies_file
from downloader_tui.services.ffmpeg import get_ffmpeg_status_message


class SettingsScreen(BaseScreen):
    """Pantalla de configuración con inputs editables."""

    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
        Binding("a", "accessibility", "Accesibilidad"),
        Binding("c", "credits", "Creditos"),
    ]

    def compose(self):
        config = load_config()
        yield Header(show_clock=True)
        yield Container(
            Static("[bold]Configuracion[/bold]", classes="title"),
            Vertical(
                Label("[bold]Carpeta de descargas:[/bold]"),
                Input(
                    value=config.get("download_dir", ""),
                    id="download_dir_input",
                    placeholder="Ruta de descargas"
                ),
                Label("[bold]Archivo de cookies:[/bold]"),
                Input(
                    value=config.get("cookies_file", ""),
                    id="cookies_file_input",
                    placeholder="Ruta cookies.txt"
                ),
                Label("[bold]Directorio FFmpeg:[/bold]"),
                Input(
                    value=config.get("ffmpeg_dir", ""),
                    id="ffmpeg_dir_input",
                    placeholder="Ruta ffmpeg"
                ),
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
            self.compose_nav_hint("ESC: Volver  |  A: Accesibilidad  |  C: Creditos  |  Flechas: Navegar"),
            classes="main-container"
        )
        yield Footer()

    def on_mount(self):
        self.config_status = self.query_one("#config_status", Static)
        self.theme_selector = self.query_one("#theme_selector", OptionList)

        # Establecer tema actual
        theme_map = {"textual-dark": 0, "textual-light": 1, "textual-ansi": 2}
        current_theme = load_config().get("theme", "textual-dark")
        if current_theme in theme_map:
            self.theme_selector.index = theme_map[current_theme]

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        if event.option_list.id == "theme_selector":
            theme_map = {0: "textual-dark", 1: "textual-light", 2: "textual-ansi"}
            theme = theme_map.get(event.option_index, "textual-dark")
            config = load_config()
            config["theme"] = theme
            save_config(config)
            self.app.theme = theme
            self.app.notify(f"Tema: {event.option.prompt}", severity="information")

    def on_button_pressed(self, event: Button.Pressed):
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

    def _save_config(self):
        config = load_config()
        config["download_dir"] = self.query_one("#download_dir_input", Input).value
        config["cookies_file"] = self.query_one("#cookies_file_input", Input).value
        config["ffmpeg_dir"] = self.query_one("#ffmpeg_dir_input", Input).value
        save_config(config)
        self.config_status.update("[green]Configuracion guardada[/green]")
        self.app.notify("Configuracion guardada correctamente", severity="information")

    def _reset_config(self):
        save_config(DEFAULT_CONFIG)
        self.query_one("#download_dir_input", Input).value = DEFAULT_CONFIG["download_dir"]
        self.query_one("#cookies_file_input", Input).value = DEFAULT_CONFIG["cookies_file"]
        self.query_one("#ffmpeg_dir_input", Input).value = DEFAULT_CONFIG["ffmpeg_dir"]
        self.theme_selector.index = 0
        self.app.theme = "textual-dark"
        self.config_status.update("[green]Configuracion restablecida[/green]")
        self.app.notify("Configuracion restablecida a valores por defecto", severity="information")

    def _check_cookies(self):
        existe, count, msg = validate_cookies_file()
        if existe:
            self.config_status.update(f"[green]{msg}[/green]")
        else:
            self.config_status.update(f"[red]{msg}[/red]")

    def _open_folder(self):
        try:
            import os
            download_dir = get_download_dir()
            if os.name == 'nt':
                os.startfile(download_dir)
            else:
                import subprocess
                subprocess.run(["xdg-open", str(download_dir)])
            self.config_status.update("[green]Carpeta abierta[/green]")
        except Exception as e:
            self.config_status.update(f"[red]Error: {e}[/red]")

    def _test_ffmpeg(self):
        self.config_status.update(get_ffmpeg_status_message())

    def action_accessibility(self):
        from .accessibility import AccessibilityScreen
        self.app.push_screen(AccessibilityScreen())

    def action_credits(self):
        from .credits import CreditsScreen
        self.app.push_screen(CreditsScreen())
