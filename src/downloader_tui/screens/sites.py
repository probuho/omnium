"""Pantalla de sitios compatibles."""

from textual.binding import Binding
from textual.widgets import Static

from ..constants import SITES_LIST
from ..logger import logger
from .base import BaseScreen


class SitesScreen(BaseScreen):
    """Pantalla de sitios compatibles."""

    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def compose(self):
        logger.info("SitesScreen composed")
        yield from self.compose_pantalla(
            Static("[bold]Sitios Compatibles (1000+)[/bold]", classes="title"),
            Static(SITES_LIST, classes="sites-content"),
            self.compose_nav_hint("ESC: Volver  |  Flechas: Scroll"),
        )
