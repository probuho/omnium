"""Modal de confirmación."""

from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmDialog(ModalScreen[bool]):
    """Modal de confirmación Sí/No."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancelar"),
        Binding("enter", "confirm", "Confirmar"),
    ]

    def __init__(self, title: str, message: str):
        super().__init__()
        self._title = title
        self._message = message

    def compose(self):
        yield Container(
            Static(f"[bold]{self._title}[/bold]", classes="dialog-title"),
            Static(self._message, classes="dialog-message"),
            Horizontal(
                Button("Si", variant="primary", id="confirm"),
                Button("No", variant="default", id="cancel"),
                classes="dialog-buttons"
            ),
            classes="dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.dismiss(True)
        elif event.button.id == "cancel":
            self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)
