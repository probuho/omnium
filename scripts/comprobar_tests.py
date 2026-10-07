"""Comprueba que los tests detectan de verdad los bugs conocidos.

Un test que pasa no demuestra nada por si solo: lo que demuestra que sirve es
que falle cuando el bug vuelve. Este script reintroduce, uno a uno, los fallos
reales que ha tenido el proyecto y comprueba que la suite los detecta. Si
alguno pasa desapercibido, termina con error.

Uso:  python scripts/comprobar_tests.py        (o  make mutaciones)
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESCARGADOR = RAIZ / "src" / "downloader_tui" / "services" / "downloader.py"

# (descripcion, archivo, texto_actual, texto_con_el_bug, test_que_debe_fallar)
MUTACIONES = [
    (
        "Plantilla del nombre mal escrita (rompia TODA descarga, exit 2)",
        DESCARGADOR,
        "%(playlist_index&{} - |)s%(title)s.%(ext)s",
        "%(playlist_index)s - %(title).%(ext)s",
        "tests/test_download.py::test_yt_dlp_acepta_la_plantilla_de_salida",
    ),
    (
        "Etiqueta artist con el literal 'NA' (basura dentro del archivo)",
        DESCARGADOR,
        '"uploader:(?P<meta_artist>^(?!NA$).+)"',
        '"uploader:%(meta_artist)s"',
        "tests/test_e2e_descarga.py::test_el_audio_descargado_lleva_etiquetas",
    ),
    (
        "Sin plantilla de progreso (la barra se queda en 0%)",
        DESCARGADOR,
        '        "--progress-template", PROGRESO_TEMPLATE,\n',
        "",
        "tests/test_e2e_descarga.py::test_el_progreso_llega_en_streaming",
    ),
    (
        "Volver a 'el archivo mas reciente del directorio'",
        DESCARGADOR,
        "archivo = _archivo_final(destino, download_dir, desde)",
        "archivo = _archivo_final(None, download_dir, 0.0)",
        "tests/test_e2e_descarga.py::test_no_informa_de_un_archivo_ajeno",
    ),
    (
        "Log que se llama a si mismo (recursion infinita)",
        RAIZ / "src" / "downloader_tui" / "screens" / "main.py",
        "        self._lineas_log.append(Text.from_markup(texto).plain)\n"
        "        self.log_widget.write(texto)",
        "        self._lineas_log.append(texto)\n"
        "        self._escribir_log(texto)",
        "tests/test_screens.py::test_el_log_se_puede_copiar_aunque_este_colapsado",
    ),
]


def ejecutar(test: str) -> bool:
    """True si el test pasa."""
    resultado = subprocess.run(
        [sys.executable, "-m", "pytest", test, "-q", "--no-header", "-x"],
        cwd=str(RAIZ),
        capture_output=True,
        text=True,
    )
    return resultado.returncode == 0


def main() -> int:
    print("=== Cada bug reintroducido debe hacer fallar su test ===\n")
    fallos = 0
    for descripcion, archivo, actual, con_bug, test in MUTACIONES:
        original = archivo.read_text(encoding="utf-8")
        if original.count(actual) != 1:
            print(f"  SALTADA      {descripcion}")
            print(f"               el texto objetivo aparece {original.count(actual)} veces")
            fallos += 1
            continue
        try:
            archivo.write_text(original.replace(actual, con_bug), encoding="utf-8")
            paso = ejecutar(test)
        finally:
            archivo.write_text(original, encoding="utf-8")

        if paso:
            print(f"  NO DETECTADO {descripcion}")
            fallos += 1
        else:
            print(f"  DETECTADO    {descripcion}")

    print()
    if fallos:
        print(f"RESULTADO: {fallos} mutacion(es) sin detectar. La suite tiene agujeros.")
        return 1
    print(f"RESULTADO: las {len(MUTACIONES)} mutaciones fueron detectadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
