"""Pantalla de accesibilidad."""

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static

from downloader_tui.constants import ACCESSIBILITY_TEXT
from downloader_tui.screens.base import BaseScreen


class AccessibilityScreen(BaseScreen):
    """Pantalla de accesibilidad con lista de atajos."""

    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def compose(self):
        yield Header(show_clock=True)
        yield Container(
            Static("[bold]Accesibilidad - Atajos de Teclado[/bold]", classes="title"),
            Static(ACCESSIBILITY_TEXT, classes="sites-content"),
            self.compose_nav_hint("ESC: Volver  |  Flechas: Scroll"),
            classes="main-container"
        )
        yield Footer()
