"""Pantalla de historial de descargas."""

from datetime import datetime

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import DataTable, Footer, Header, Static

from ...config import get_download_dir
from ..base import BaseScreen


class HistoryScreen(BaseScreen):  # type: ignore[misc]
    """Pantalla de historial de descargas."""

    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("r", "refresh", "Actualizar"),
        Binding("delete", "delete_file", "Eliminar"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def compose(self):
        yield Header(show_clock=True)
        yield Container(
            Static("[bold]Historial de Descargas[/bold]", classes="title"),
            DataTable(id="history_table", cursor_type="row"),
            self.compose_nav_hint("ESC: Volver  |  R: Actualizar  |  Del: Eliminar  |  Flechas: Navegar"),
            classes="main-container"
        )
        yield Footer()

    def on_mount(self):
        self.table = self.query_one("#history_table", DataTable)
        self.table.add_columns("Fecha", "Archivo", "Tamaño")
        self.action_refresh()

    def action_refresh(self):
        self.table.clear()
        download_dir = get_download_dir()
        if download_dir.exists():
            files = sorted(
                (f for f in download_dir.glob("*") if f.is_file()),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            for f in files[:100]:
                stat = f.stat()
                date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                size = self._format_size(stat.st_size)
                self.table.add_row(date, f.name, size)

    def _format_size(self, bytes_: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_ < 1024:
                return f"{bytes_:.1f} {unit}"
            bytes_ /= 1024
        return f"{bytes_:.1f} TB"

    def action_delete_file(self):
        if self.table.cursor_row is not None:
            row = self.table.get_row_at(self.table.cursor_row)
            if row:
                filename = row[1]
                filepath = get_download_dir() / filename
                if filepath.exists():
                    try:
                        filepath.unlink()
                        self.action_refresh()
                        self.app.notify(f"Eliminado: {filename}", severity="information")
                    except Exception as e:
                        self.app.notify(f"Error: {e}", severity="error")
