"""Pantalla base: navegacion comun y la estructura de layout compartida."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

# Alto minimo de ventana para centrar el bloque verticalmente. La pantalla mas
# alta (la principal) mide unas 33 filas de contenido, asi que por debajo de 40
# no hay holgura real y centrar solo quitaria filas utiles.
ALTO_PARA_CENTRAR = 40


class BaseScreen(Screen):
    """Pantalla base con navegacion comun y la misma estructura que la principal."""

    # Textual enfoca solo el primer widget enfocable (App.AUTO_FOCUS = '*') y al
    # enfocarlo DESPLAZA el area para dejarlo visible: en una pantalla con el
    # contenido centrado eso lo descuadra (medido en la principal: scroll_y 4.8,
    # el logo cortado). Vacio = sin auto-foco; donde interese, se pone a mano.
    AUTO_FOCUS = ""

    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
        Binding("left", "cursor_left", "Izquierda"),
        Binding("right", "cursor_right", "Derecha"),
    ]

    def compose_pantalla(self, *contenido) -> ComposeResult:
        """Estructura comun de todas las pantallas.

        Cabecera y pie fijos, y en medio la misma columna que la pantalla
        principal: 80 columnas como maximo, centrada en horizontal, con el mismo
        ritmo de espaciado. Los dos espaciadores elasticos reparten el alto
        sobrante, asi que el bloque queda centrado tambien en vertical cuando la
        ventana tiene holgura; cuando no la tiene se ocultan (ver
        _ajustar_espaciadores) y el area simplemente se desplaza.
        """
        yield Header(show_clock=True)
        yield Vertical(
            Container(
                Static("", classes="relleno-flexible"),
                *contenido,
                Static("", classes="relleno-flexible"),
                classes="main-container",
            ),
            classes="composer-area",
        )
        yield Footer()

    def compose_nav_hint(self, hint_text: str) -> Static:
        """Crea un hint de navegación consistente."""
        return Static(hint_text, classes="nav-hint")

    def on_resize(self, event) -> None:
        self._ajustar_espaciadores(event.size.height)

    def _ajustar_espaciadores(self, alto: int) -> None:
        """Muestra los espaciadores elasticos solo cuando sobra altura.

        `1fr` en Textual tiene suelo de una fila, asi que en una ventana sin
        holgura los dos espaciadores roban dos filas utiles: medido en la
        principal, el progreso caia a la fila 23 y quedaba recortado.
        """
        centrar = alto >= ALTO_PARA_CENTRAR
        for relleno in self.query(".relleno-flexible"):
            relleno.display = centrar

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
