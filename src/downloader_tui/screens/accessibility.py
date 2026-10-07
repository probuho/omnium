"""Pantalla de accesibilidad."""

from textual.binding import Binding
from textual.widgets import Static

from downloader_tui.constants import ACCESSIBILITY_TEXT
from downloader_tui.logger import logger
from downloader_tui.screens.base import BaseScreen


class AccessibilityScreen(BaseScreen):
    """Pantalla de accesibilidad con atajos de teclado."""

    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def compose(self):
        logger.info("AccessibilityScreen composed")
        yield from self.compose_pantalla(
            Static("[bold]Accesibilidad - Atajos de Teclado[/bold]", classes="title"),
            Static(ACCESSIBILITY_TEXT, classes="sites-content"),
            self.compose_nav_hint("ESC: Volver  |  Flechas: Scroll"),
        )
