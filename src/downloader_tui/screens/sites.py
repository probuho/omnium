"""Pantalla de sitios compatibles."""

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static

from ...constants import SITES_LIST
from ..base import BaseScreen


class SitesScreen(BaseScreen):  # type: ignore[misc]
    """Pantalla de sitios compatibles."""

    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def compose(self):
        yield Header(show_clock=True)
        yield Container(
            Static("[bold]Sitios Compatibles (1000+)[/bold]", classes="title"),
            Static(SITES_LIST, classes="sites-content"),
            self.compose_nav_hint("ESC: Volver  |  Flechas: Scroll"),
            classes="main-container"
        )
        yield Footer()
