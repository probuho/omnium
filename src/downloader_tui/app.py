"""Aplicación principal Omnium Suite."""

from textual.app import App
from textual.binding import Binding

from .screens.main import MainScreen
from .styles.css import MONOKAI_CSS


class OmniumSuiteApp(App):
    """Aplicación principal Omnium Suite."""

    TITLE = "Omnium Suite - Video Downloader"
    CSS = MONOKAI_CSS

    BINDINGS = [
        Binding("q", "quit", "Salir", show=True),
    ]

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

    def action_quit(self) -> None:
        self.exit()
