"""Pantalla base con navegación común."""

from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static


class BaseScreen(Screen):
    """Pantalla base con navegación común y hint visual."""

    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
        Binding("left", "cursor_left", "Izquierda"),
        Binding("right", "cursor_right", "Derecha"),
    ]

    def compose_nav_hint(self, hint_text: str) -> Static:
        """Crea un hint de navegación consistente."""
        return Static(hint_text, classes="nav-hint")

    def action_go_back(self) -> None:
        """Volver a la pantalla anterior."""
        self.app.pop_screen()

    def action_cursor_up(self) -> None:
        """Navegar arriba (para listas/tablas)."""

    def action_cursor_down(self) -> None:
        """Navegar abajo (para listas/tablas)."""

    def action_cursor_left(self) -> None:
        """Navegar izquierda (para tabs/botones)."""

    def action_cursor_right(self) -> None:
        """Navegar derecha (para tabs/botones)."""
