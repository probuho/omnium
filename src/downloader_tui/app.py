"""Aplicación principal Omnium Suite."""

import logging

from textual.app import App
from textual.binding import Binding
from textual.theme import Theme

from .screens.main import MainScreen
from .styles.css import MONOKAI_CSS

logger = logging.getLogger("omnium")

MONOKAI_THEME = Theme(
    name="monokai",
    primary="#ae81ff",
    secondary="#66d9ef",
    accent="#a6e22e",
    background="#272822",
    surface="#3e3d32",
    panel="#1e1f1c",
    dark=True,
)


class OmniumSuiteApp(App):
    """Aplicación principal Omnium Suite."""

    TITLE = "Omnium Suite - Video Downloader"
    CSS = MONOKAI_CSS

    BINDINGS = [
        Binding("q", "quit", "Salir", show=True),
    ]

    def on_mount(self) -> None:
        self.register_theme(MONOKAI_THEME)
        self.register_theme(Theme("textual-dark", primary="#66d9ef", secondary="#a6e22e", background="#272822", dark=True))
        self.register_theme(Theme("textual-light", primary="#0066cc", secondary="#0099cc", background="#ffffff", dark=False))
        self.register_theme(Theme("textual-ansi", primary="#00aa00", secondary="#00aaaa", background="#000000", dark=True))
        self.theme = "monokai"
        logger.info("App mounted, pushing MainScreen")
        self.push_screen(MainScreen())

    def action_quit(self) -> None:
        logger.info("Quitting app")
        self.exit()
