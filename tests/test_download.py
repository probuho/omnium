"""Tests del comando de descarga y de la clasificacion de errores.

Cubren el fallo que tenia la app bloqueada: la plantilla del nombre de archivo
estaba mal escrita ("%(title).%(ext)s", sin la 's'), yt-dlp la rechazaba y
TODA descarga fallaba con exit 2 antes de empezar, con cualquier URL. Ningun
test lo detectaba porque la plantilla solo se valida al ejecutar yt-dlp.
"""

import sys
from pathlib import Path

from yt_dlp import YoutubeDL

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from downloader_tui.models.errors import ErrorCategory, classify_error
from downloader_tui.services.downloader import add_common_args, build_yt_dlp_cmd

URL = "https://www.youtube.com/watch?v=NQo91kZ7amM"


def _comando(url: str = URL) -> list[str]:
    return add_common_args(build_yt_dlp_cmd(url, "video"), url, use_cookies=False)


def _valor(cmd: list[str], opcion: str) -> str:
    return cmd[cmd.index(opcion) + 1]


def test_yt_dlp_acepta_la_plantilla_de_salida() -> None:
    """El validador real de yt-dlp debe aceptar la plantilla que arma la app."""
    plantilla = _valor(_comando(), "--output")
    error = YoutubeDL.validate_outtmpl(plantilla)
    assert error is None, f"yt-dlp rechaza la plantilla {plantilla!r}: {error}"


def test_nombre_de_archivo_sin_prefijo_NA() -> None:
    """Un video suelto no debe llevar prefijo, y una lista debe ir numerada."""
    plantilla = _valor(_comando(), "--output")
    ydl = YoutubeDL({"outtmpl": {"default": plantilla}, "quiet": True, "no_warnings": True})

    suelto = ydl.prepare_filename(
        {"title": "Cancion", "ext": "mp4", "playlist_index": None, "id": "abc"}
    )
    assert Path(suelto).name == "Cancion.mp4"

    en_lista = ydl.prepare_filename(
        {"title": "Cancion", "ext": "mp4", "playlist_index": 3, "id": "abc"}
    )
    assert Path(en_lista).name == "3 - Cancion.mp4"


def test_error_conocido_se_clasifica() -> None:
    error = classify_error("ERROR: Video not available in your country")
    assert error.category is ErrorCategory.NOT_FOUND


def test_error_no_clasificado_conserva_el_texto_de_yt_dlp() -> None:
    """Sin coincidencia en el mapa, el motivo real NO debe perderse."""
    salida = "ERROR: [youtube] NQo91kZ7amM: algo que yt-dlp explica y nadie mas sabe"
    error = classify_error(salida)
    assert error.category is ErrorCategory.UNKNOWN
    assert "algo que yt-dlp explica" in error.message
    assert error.message != "Error desconocido"


def test_plantilla_mal_escrita_se_reporta_con_su_motivo() -> None:
    """El error de plantilla invalida debe verse, no convertirse en 'desconocido'."""
    salida = (
        '__main__.py: error: invalid default output template "x %(title).%(ext)s": '
        "unsupported format character '%' (0x25) at index 5"
    )
    error = classify_error(salida)
    assert "unsupported format character" in error.message


def test_salida_vacia_no_inventa_un_motivo() -> None:
    error = classify_error("")
    assert error.category is ErrorCategory.UNKNOWN
    assert "no devolvio ninguna linea" in error.message


async def test_el_log_interpreta_el_markup() -> None:
    """El log debe mostrar 'URL:' en color, no el markup literal.

    Con el widget Log (texto plano) se veia "[cyan]URL:[/cyan] ..." en pantalla.
    """
    from textual.widgets import Collapsible, RichLog

    from downloader_tui.app import OmniumSuiteApp

    app = OmniumSuiteApp()
    async with app.run_test(size=(100, 32)) as pilot:
        await pilot.pause()
        # El log arranca colapsado y RichLog aplaza el render hasta tener
        # tamaño: hay que desplegarlo para que registre las lineas.
        app.screen.query_one("#log_collapsible", Collapsible).collapsed = False
        await pilot.pause()
        log = app.screen.query_one("#download_log", RichLog)
        log.write("[cyan]URL:[/cyan] https://ejemplo/x")
        await pilot.pause()
        texto = "".join(strip.text for strip in log.lines)
        assert "[cyan]" not in texto
        assert "URL:" in texto
