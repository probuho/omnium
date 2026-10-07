"""Tests de importacion de todas las pantallas.

Estas pantallas se importan de forma perezosa (dentro de los action_* de
MainScreen), asi que un import roto en ellas no rompe la app al arrancar ni lo
detecta ningun otro test: solo falla cuando el usuario pulsa la tecla. Eso es
exactamente lo que pasaba con SitesScreen e HistoryScreen, que importaban
`..base` (downloader_tui.base, inexistente) en lugar de `.base`.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

MODULOS = [
    "downloader_tui.screens.main",
    "downloader_tui.screens.sites",
    "downloader_tui.screens.history",
    "downloader_tui.screens.settings",
    "downloader_tui.screens.accessibility",
    "downloader_tui.screens.credits",
    "downloader_tui.screens.base",
    "downloader_tui.screens.modals",
    "downloader_tui.screens.modals.confirm",
    "downloader_tui.screens.modals.quality",
]


@pytest.mark.parametrize("modulo", MODULOS)
def test_modulo_de_pantalla_importa(modulo: str) -> None:
    """Cada modulo de pantalla debe poder importarse por si solo."""
    import importlib

    importlib.import_module(modulo)


def test_todas_las_pantallas_se_construyen() -> None:
    """Las pantallas deben poder instanciarse sin argumentos obligatorios."""
    from downloader_tui.screens.accessibility import AccessibilityScreen
    from downloader_tui.screens.credits import CreditsScreen
    from downloader_tui.screens.history import HistoryScreen
    from downloader_tui.screens.settings import SettingsScreen
    from downloader_tui.screens.sites import SitesScreen

    for pantalla in (
        SitesScreen,
        HistoryScreen,
        SettingsScreen,
        AccessibilityScreen,
        CreditsScreen,
    ):
        assert pantalla() is not None


async def test_el_log_se_puede_copiar_aunque_este_colapsado() -> None:
    """Ctrl+C copia el log completo, sin markup y sin desplegarlo antes.

    Se lee de un buffer propio y no del widget a proposito: el log arranca
    colapsado y RichLog no materializa sus lineas hasta tener tamano, asi que
    leer del widget devolveria vacio justo cuando hace falta.
    """
    from downloader_tui.app import OmniumSuiteApp

    app = OmniumSuiteApp()
    async with app.run_test(size=(100, 32)) as pilot:
        await pilot.pause()
        pantalla = app.screen
        pantalla._escribir_log("[cyan]URL:[/cyan] https://ejemplo/x")
        pantalla._escribir_log("[red]Error:[/red] algo salio mal")

        # El log sigue colapsado, asi que el widget no tiene lineas...
        assert pantalla.log_widget.lines == []
        # ...pero el buffer copiable si tiene el texto.
        texto = pantalla._texto_del_log()
        assert "URL: https://ejemplo/x" in texto
        assert "Error: algo salio mal" in texto
        # Sin las etiquetas de color, que ensuciarian el texto pegado.
        assert "[cyan]" not in texto
        assert "[red]" not in texto
