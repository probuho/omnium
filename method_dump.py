    async def _do_download(self, url: str, use_cookies: bool, fmt: str, quality: str) -> None:
        try:
            cmd = [sys.executable, "-m", "yt_dlp"]
            if self.current_media == "video":
                cmd.extend(["--format", fmt, "--merge-output-format", "mp4"])
            elif self.current_media == "audio":
                cmd.extend([
                    "--format", "bestaudio/best",
                    "--extract-audio", "--audio-format", fmt,
                    "--audio-quality", quality,
                ])
            elif self.current_media == "image":
                # Pinterest: descargar imagen original directa sin thumbnail conversion
                if "pinterest.com" in url or "pin.it" in url:
                    cmd.extend(["--format", "best"])
                else:
                    cmd.extend([
                        "--format", fmt,
                        "--write-thumbnail", "--convert-thumbnails", fmt,
                    ])

                if use_cookies:
                    cmd.extend(["--cookies", str(COOKIES_FILE)])

                cmd.extend([
                    "--ffmpeg-location", str(FFMPEG_DIR),
                    "--output", str(DOWNLOAD_DIR / "%(playlist_index)s - %(title)s.%(ext)s"),
                    "--no-warnings",
                    "--newline",
                    url
                ])

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(SCRIPT_DIR)
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                files = list(DOWNLOAD_DIR.glob("*"))
                if files:
                    latest = max(files, key=lambda f: f.stat().st_mtime)
                    self.status.update("[green]Descarga completada[/green]")
                    self.log_widget.write_line(f"[green]Archivo:[/green] {latest}")
                    self.app.notify(f"Descarga completada: {latest.name}", severity="information")
                else:
                    self.status.update("[green]Descarga completada[/green]")
                    self.app.notify("Descarga completada", severity="information")
                self.progress_bar.progress = 100
            else:
                error_text = stderr.decode(errors="ignore") if stderr else "Error desconocido"
                error = classify_error(error_text)
                self.status.update(f"[red]{error.message}[/red]")
                self.log_widget.write_line(f"[red]{error.message}[/red]")
                self.log_widget.write_line(f"[yellow]Sugerencia:[/yellow] {error.suggestion}")
                self.app.notify(f"{error.message}: {error.suggestion}", severity="error")

            except asyncio.CancelledError:
                self.status.update("[yellow]Descarga cancelada[/yellow]")
            except Exception as e:
                error = classify_error(str(e))
                self.status.update(f"[red]{error.message}[/red]")
                self.log_widget.write_line(f"[red]{error.message}[/red]")
                self.log_widget.write_line(f"[yellow]Sugerencia:[/yellow] {error.suggestion}")
            finally:
                self.downloading = False
                self.download_btn.disabled = False
                self.download_btn.label = "Descargar (Enter)"

    def action_history(self) -> None:
        self.app.push_screen(HistoryScreen())

    def action_settings(self) -> None:
        self.app.push_screen(SettingsScreen())

    def action_sites(self) -> None:
        self.app.push_screen(SitesScreen())

    def action_quit(self) -> None:
        self.app.exit()


class SitesScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("[bold]Sitios Compatibles (1000+)[/bold]", classes="title"),
            Static(SITES_LIST, classes="sites-content"),
            Static("[dim]ESC: Volver  |  Flechas: Scroll[/dim]", classes="nav-hint"),
            classes="main-container"
        )
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()


class HistoryScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("r", "refresh", "Actualizar"),
        Binding("delete", "delete_file", "Eliminar"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("[bold]Historial de Descargas[/bold]", classes="title"),
            DataTable(id="history_table", cursor_type="row"),
            Static("[dim]ESC: Volver  |  R: Actualizar  |  Del: Eliminar  |  Flechas: Navegar[/dim]", classes="nav-hint"),
            classes="main-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.table = self.query_one("#history_table", DataTable)
        self.table.add_columns("Fecha", "Archivo", "Tamaño")
        self.action_refresh()

    def action_refresh(self) -> None:
        self.table.clear()
        if DOWNLOAD_DIR.exists():
            files = sorted(DOWNLOAD_DIR.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
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

    def action_delete_file(self) -> None:
        if self.table.cursor_row is not None:
            row = self.table.get_row_at(self.table.cursor_row)
            if row:
                filename = row[1]
                filepath = DOWNLOAD_DIR / filename
                if filepath.exists():
                    try:
                        filepath.unlink()
                        self.action_refresh()
                        self.app.notify(f"Eliminado: {filename}", severity="information")
                    except Exception as e:
                        self.app.notify(f"Error: {e}", severity="error")

    def action_go_back(self) -> None:
        self.app.pop_screen()


class SettingsScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
        Binding("a", "accessibility", "Accesibilidad"),
        Binding("c", "credits", "Creditos"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("[bold]Configuracion[/bold]", classes="title"),
            Vertical(
                Label("[bold]Carpeta de descargas:[/bold]"),
                Input(value=str(DOWNLOAD_DIR), id="download_dir_input", placeholder="Ruta de descargas"),
                Label("[bold]Archivo de cookies:[/bold]"),
                Input(value=str(COOKIES_FILE), id="cookies_file_input", placeholder="Ruta cookies.txt"),
                Label("[bold]Directorio FFmpeg:[/bold]"),
                Input(value=str(FFMPEG_DIR), id="ffmpeg_dir_input", placeholder="Ruta ffmpeg"),
                Label(""),
                Label("[bold]Tema:[/bold]"),
                OptionList(
                    Option("Oscuro (textual-dark)", id="dark"),
                    Option("Claro (textual-light)", id="light"),
                    Option("Sistema (textual-ansi)", id="system"),
                    id="theme_selector"
                ),
                Label(""),
                Horizontal(
                    Button("Guardar", variant="primary", id="save_config"),
                    Button("Restablecer", variant="default", id="reset_config"),
                    classes="button-group"
                ),
                Label(""),
                Horizontal(
                    Button("Verificar cookies", id="check_cookies"),
                    Button("Abrir carpeta descargas", id="open_folder"),
                    Button("Probar ffmpeg", id="test_ffmpeg"),
                    classes="button-group"
                ),
                Label(""),
                Horizontal(
                    Button("Accesibilidad (A)", id="accessibility_btn"),
                    Button("Creditos (C)", id="credits_btn"),
                    classes="button-group"
                ),
                classes="settings-list"
            ),
            Static("", id="config_status", classes="status"),
            Static("[dim]ESC: Volver  |  A: Accesibilidad  |  C: Creditos  |  Flechas: Navegar[/dim]", classes="nav-hint"),
            classes="main-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.config_status = self.query_one("#config_status", Static)
        self.theme_selector = self.query_one("#theme_selector", OptionList)
        # Set current theme
        theme_to_index = {"textual-dark": 0, "textual-light": 1, "textual-ansi": 2}
        current_theme = config.get("theme", "textual-dark")
        if current_theme in theme_to_index:
            self.theme_selector.highlighted = theme_to_index[current_theme]

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id == "theme_selector":
            theme_map = {"dark": "textual-dark", "light": "textual-light", "system": "textual-ansi"}
            theme = theme_map.get(event.option.id, "textual-dark")
            config["theme"] = theme
            self.app.theme = theme
            self.app.notify(f"Tema: {event.option.prompt}", severity="information")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "check_cookies":
            self._check_cookies()
        elif event.button.id == "open_folder":
            self._open_folder()
        elif event.button.id == "test_ffmpeg":
            self._test_ffmpeg()
        elif event.button.id == "save_config":
            self._save_config()
        elif event.button.id == "reset_config":
            self._reset_config()
        elif event.button.id == "accessibility_btn":
            self.action_accessibility()
        elif event.button.id == "credits_btn":
            self.action_credits()

    def _save_config(self) -> None:
        global DOWNLOAD_DIR, COOKIES_FILE, FFMPEG_DIR, config
        config["download_dir"] = self.query_one("#download_dir_input", Input).value
        config["cookies_file"] = self.query_one("#cookies_file_input", Input).value
        config["ffmpeg_dir"] = self.query_one("#ffmpeg_dir_input", Input).value
        save_config(config)
        DOWNLOAD_DIR = Path(config["download_dir"])
        COOKIES_FILE = Path(config["cookies_file"])
        FFMPEG_DIR = Path(config["ffmpeg_dir"])
        self.config_status.update("[green]Configuracion guardada[/green]")
        self.app.notify("Configuracion guardada correctamente", severity="information")

    def _reset_config(self) -> None:
        global DOWNLOAD_DIR, COOKIES_FILE, FFMPEG_DIR, config
        config = DEFAULT_CONFIG.copy()
        save_config(config)
        DOWNLOAD_DIR = Path(config["download_dir"])
        COOKIES_FILE = Path(config["cookies_file"])
        FFMPEG_DIR = Path(config["ffmpeg_dir"])
        self.query_one("#download_dir_input", Input).value = str(DOWNLOAD_DIR)
        self.query_one("#cookies_file_input", Input).value = str(COOKIES_FILE)
        self.query_one("#ffmpeg_dir_input", Input).value = str(FFMPEG_DIR)
        self.theme_selector.highlighted = "dark"
        self.app.theme = "textual-dark"
        config["theme"] = "textual-dark"
        self.config_status.update("[green]Configuracion restablecida[/green]")
        self.app.notify("Configuracion restablecida a valores por defecto", severity="information")

    def _check_cookies(self) -> None:
        if COOKIES_FILE.exists():
            lines = COOKIES_FILE.read_text(encoding="utf-8", errors="ignore").strip().split("\n")
            cookie_lines = [l for l in lines if l and not l.startswith("#")]
            self.config_status.update(f"[green]cookies.txt ({len(cookie_lines)} cookies)[/green]")
        else:
            self.config_status.update("[red]cookies.txt NO encontrado[/red]")

    def _open_folder(self) -> None:
        try:
            if sys.platform == "win32":
                os.startfile(DOWNLOAD_DIR)
            elif sys.platform == "darwin":
                subprocess.run(["open", DOWNLOAD_DIR])
            else:
                subprocess.run(["xdg-open", DOWNLOAD_DIR])
            self.config_status.update("[green]Carpeta abierta[/green]")
        except Exception as e:
            self.config_status.update(f"[red]Error: {e}[/red]")

    def _test_ffmpeg(self) -> None:
        try:
            result = subprocess.run(
                [str(FFMPEG_DIR / "ffmpeg.exe"), "-version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.config_status.update("[green]FFmpeg OK[/green]")
            else:
                self.config_status.update("[red]FFmpeg no funciona[/red]")
        except Exception as e:
            self.config_status.update(f"[red]Error: {e}[/red]")

    def action_accessibility(self) -> None:
        self.app.push_screen(AccessibilityScreen())

    def action_credits(self) -> None:
        self.app.push_screen(CreditsScreen())

    def action_go_back(self) -> None:
        self.app.pop_screen()


class AccessibilityScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("[bold]Accesibilidad - Atajos de Teclado[/bold]", classes="title"),
            Static(ACCESSIBILITY_TEXT, classes="sites-content"),
            Static("[dim]ESC: Volver  |  Flechas: Scroll[/dim]", classes="nav-hint"),
            classes="main-container"
        )
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()


class CreditsScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Volver"),
        Binding("up", "cursor_up", "Arriba"),
        Binding("down", "cursor_down", "Abajo"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("[bold]Creditos[/bold]", classes="title"),
            Static(CREDITS_TEXT, classes="sites-content"),
            Static("[dim]ESC: Volver  |  Flechas: Scroll[/dim]", classes="nav-hint"),
            classes="main-container"
        )
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()


class OmniumSuiteApp(App):
    TITLE = "Omnium Suite - Video Downloader"
    CSS = """
    Screen {
        background: #272822;
        color: #f8f8f2;
    }

    .ascii-logo {
        text-align: center;
        color: #ae81ff;
        padding: 1 0;
        height: 8;
        overflow: hidden;
    }

    .subtitle {
        text-align: center;
        color: #75715e;
        margin-bottom: 1;
    }

    .divider {
        color: #75715e;
        text-align: center;
        margin: 0 0 1 0;
    }

    .main-container {
        width: 100%;
        height: 100%;
        padding: 0 2;
    }

    .url-label {
        color: #f8f8f2;
        margin-top: 1;
        margin-bottom: 0;
    }

    .input-group {
        margin: 0 0 1 0;
    }

    Input {
        background: #3e3d32;
        border: solid #75715e;
        color: #f8f8f2;
        padding: 0 1;
    }

    Input:focus {
        border: solid #ae81ff;
    }

    .validation {
        height: 1;
        margin: 0 0 1 0;
    }

    .sites-hint {
        height: 2;
        margin: 0 0 1 0;
        text-align: center;
        text-wrap: wrap;
    }

    .tab-group {
        margin: 1 0;
        height: 3;
    }

    .tab-group Button {
        margin-right: 1;
        min-width: 16;
    }

    .option-group {
        margin: 1 0;
    }

    .option-group.hidden {
        display: none;
    }

    .option-label {
        color: #ae81ff;
        margin: 1 0 0 0;
    }

    OptionList {
        background: #3e3d32;
        border: solid #75715e;
        color: #f8f8f2;
        margin: 0 0 1 0;
    }

    OptionList:focus {
        border: solid #ae81ff;
    }

    OptionList > .option-list--option-highlighted {
        background: #ae81ff;
        color: #272822;
    }

    .privacy-notice {
        margin-top: 2;
        padding: 1;
        background: #1e1f1c;
        border: solid #75715e;
        text-align: center;
        text-wrap: wrap;
    }

    .nav-hint {
        margin-top: 1;
        padding: 1;
        background: #1e1f1c;
        border: solid #75715e;
        text-align: center;
        color: #75715e;
    }

    .button-group {
        margin: 1 0;
        width: 100%;
        height: auto;
    }

    .button-group Button {
        margin-right: 1;
        background: #3e3d32;
        border: solid #75715e;
        color: #f8f8f2;
    }

    .button-group Button:hover {
        background: #4e4d3e;
        border: solid #ae81ff;
    }

    .button-group Button:focus {
        background: #4e4d3e;
        border: solid #ae81ff;
    }

    .button-group Button.focused {
        background: #4e4d3e;
        border: solid #ae81ff;
    }

    .button-group Button.-primary {
        background: #ae81ff;
        border: solid #ae81ff;
        color: #272822;
    }

    .button-group Button.-primary:hover {
        background: #cc99ff;
        border: solid #cc99ff;
    }

    .status {
        margin: 1 0;
        height: 1;
    }

    #progress {
        margin: 1 0;
        background: #3e3d32;
        color: #ae81ff;
    }

    .log {
        height: 18;
        background: #1e1f1c;
        border: solid #75715e;
        color: #f8f8f2;
        margin-top: 1;
        padding: 1;
    }

    .title {
        text-align: center;
        color: #ae81ff;
        padding: 1;
        margin-bottom: 1;
    }

    .settings-list {
        margin: 1 0;
    }

    .settings-list Label {
        margin-top: 1;
        color: #ae81ff;
    }

    .config-value {
        padding-left: 2;
        color: #75715e;
        overflow: hidden;
    }

    .sites-content {
        padding: 1 2;
        color: #f8f8f2;
        overflow-y: auto;
        height: 100%;
    }

    DataTable {
        height: 100%;
        background: #272822;
    }

    DataTable > .datatable--header {
        background: #3e3d32;
        color: #ae81ff;
        text-style: bold;
    }

    DataTable > .datatable--cursor {
        background: #ae81ff;
        color: #272822;
    }

    .dialog {
        width: 60;
        height: auto;
        padding: 2;
        border: solid #ae81ff;
        background: #3e3d32;
    }

    .dialog-title {
        text-align: center;
        color: #ae81ff;
        margin-bottom: 1;
    }

    .dialog-message {
        text-align: center;
        color: #f8f8f2;
        margin-bottom: 2;
    }

    .dialog-buttons {
        width: 100%;
    }

    .dialog-buttons Button {
        margin: 0 1;
    }

    Header {
        background: #272822;
        color: #75715e;
        border: solid #75715e;
        height: 1;
    }

    Footer {
        background: #272822;
        color: #75715e;
        border: solid #75715e;
    }

    Footer .key {
        color: #ae81ff;
    }

    Collapsible {
        border: solid #75715e;
        background: #272822;
    }

    Collapsible.-collapsed {
        border: solid #75715e;
    }

    CollapsibleTitle {
        color: #ae81ff;
        background: #3e3d32;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Salir", show=True),
    ]

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

    def action_quit(self) -> None:
        self.exit()


