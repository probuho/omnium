"""Pantalla de créditos."""

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static

from downloader_tui.constants import CREDITS_TEXT
from downloader_tui.screens.base import BaseScreen


class CreditsScreen(BaseScreen):
    """Pantalla de créditos."""

    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def compose(self):
        yield Header(show_clock=True)
        yield Container(
            Static("[bold]Creditos[/bold]", classes="title"),
            Static(CREDITS_TEXT, classes="sites-content"),
            self.compose_nav_hint("ESC: Volver  |  Flechas: Scroll"),
            classes="main-container"
        )
        yield Footer()
