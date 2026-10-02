"""Modal de detección de calidades disponibles."""

from typing import Literal

from textual import work
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListItem, ListView, Static

from ...services.quality import detect_available_formats

MediaType = Literal["video", "audio", "image"]


class QualityDetectionModal(ModalScreen[dict | None]):
    """Modal que detecta y muestra formatos disponibles."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancelar"),
        Binding("enter", "select", "Seleccionar"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def __init__(self, url: str, media_type: MediaType = "video", use_cookies: bool = True):
        super().__init__()
        self.url = url
        self.media_type = media_type
        self.use_cookies = use_cookies
        self.formats: list = []
        self.selected_index = 0

    def compose(self):
        yield Container(
            Static("[bold]Calidades Disponibles[/bold]", classes="dialog-title"),
            Static(f"URL: {self.url}", classes="dialog-message"),
            Static("[dim]Detectando formatos disponibles...[/dim]", id="detection_status"),
            ListView(id="formats_list"),
            Horizontal(
                Button("Descargar", variant="primary", id="download_selected"),
                Button("Cancelar", variant="default", id="cancel"),
                classes="dialog-buttons"
            ),
            classes="dialog"
        )

    def on_mount(self):
        self.run_worker(self._detect_formats(), exclusive=True)

    @work(exclusive=True)
    async def _detect_formats(self):
        try:
            formats = await detect_available_formats(
                self.url, self.media_type, True
            )
            self.formats = formats
            self._update_formats_list()
            self.query_one("#detection_status", Static).update(
                f"[green]Se detectaron {len(formats)} formatos[/green]"
            )
        except Exception as e:
            self.query_one("#detection_status", Static).update(f"[red]Error: {e}[/red]")

    def _update_formats_list(self):
        list_view = self.query_one("#formats_list", ListView)
        list_view.clear()

        for i, fmt in enumerate(self.formats):
            note = f" ({fmt.note})" if fmt.note else ""
            filesize = f" - {fmt.filesize}" if fmt.filesize else ""
            item = ListItem(
                Label(f"{i+1}. ID: {fmt.format_id}  Ext: {fmt.ext}  Res: {fmt.resolution}{note}{filesize}"),
                id=f"fmt_{i}"
            )
            list_view.append(item)

        if self.formats:
            list_view.index = 0
            self.selected_index = 0

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        if event.item and event.item.id:
            self.selected_index = int(event.item.id.split("_")[1])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download_selected":
            if self.formats and 0 <= self.selected_index < len(self.formats):
                selected = self.formats[self.selected_index]
                self.dismiss({
                    "format_id": selected.format_id,
                    "ext": selected.ext,
                    "resolution": selected.resolution,
                    "url": self.url,
                    "media_type": self.media_type,
                })
        elif event.button.id == "cancel":
            self.dismiss(None)

    def action_select(self) -> None:
        self.query_one("#download_selected", Button).press()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_cursor_up(self) -> None:
        list_view = self.query_one("#formats_list", ListView)
        if self.formats:
            self.selected_index = max(0, self.selected_index - 1)
            list_view.index = self.selected_index

    def action_cursor_down(self) -> None:
        list_view = self.query_one("#formats_list", ListView)
        if self.formats:
            self.selected_index = min(len(self.formats) - 1, self.selected_index + 1)
            list_view.index = self.selected_index