"""Punto de entrada principal."""

from downloader_tui.app import OmniumSuiteApp
from downloader_tui.config import load_config


def main():
    """Función principal."""
    load_config()  # Cargar config al inicio
    app = OmniumSuiteApp()
    app.run()


if __name__ == "__main__":
    main()
