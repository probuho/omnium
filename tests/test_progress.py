"""Tests del progreso en vivo y del formateo de magnitudes.

Las lineas que se usan aqui como entrada NO son inventadas: se capturaron de una
ejecucion real de yt-dlp con esta misma plantilla (--progress-template).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from downloader_tui.services.downloader import (
    PROGRESO_PREFIJO,
    add_common_args,
    build_yt_dlp_cmd,
    parsear_destino,
    parsear_progreso,
)
from downloader_tui.utils import formatear_bytes, formatear_eta, formatear_velocidad

# Salida real de yt-dlp (recortada de una descarga contra un servidor local).
LINEAS_REALES = [
    "OMNIUM_PROGRESS 1024 499555 NA NA NA",
    "OMNIUM_PROGRESS 3072 499555 NA 5781686.744615384 0",
    "OMNIUM_PROGRESS 499555 499555 NA 135406845.98164663 0",
]


def test_parsea_una_linea_real_de_progreso() -> None:
    avance = parsear_progreso(LINEAS_REALES[1])
    assert avance is not None
    assert avance.descargado == 3072
    assert avance.total == 499555
    assert avance.velocidad is not None and avance.velocidad > 0
    assert avance.eta == 0
    # 3072 de 499555
    assert avance.porcentaje is not None
    assert abs(avance.porcentaje - 0.615) < 0.01


def test_progreso_sin_velocidad_ni_eta_no_inventa_datos() -> None:
    avance = parsear_progreso(LINEAS_REALES[0])
    assert avance is not None
    assert avance.velocidad is None
    assert avance.eta is None
    assert avance.descargado == 1024


def test_progreso_al_cien_por_ciento() -> None:
    avance = parsear_progreso(LINEAS_REALES[2])
    assert avance is not None
    assert avance.porcentaje == 100.0


def test_usa_el_total_estimado_cuando_falta_el_total() -> None:
    avance = parsear_progreso(f"{PROGRESO_PREFIJO}500 NA 1000 NA NA")
    assert avance is not None
    assert avance.total == 1000
    assert avance.porcentaje == 50.0


def test_progreso_sin_ningun_dato_no_da_porcentaje() -> None:
    avance = parsear_progreso(f"{PROGRESO_PREFIJO}NA NA NA NA NA")
    assert avance is not None
    assert avance.porcentaje is None
    assert avance.descargado is None
    assert avance.total is None


def test_lineas_ajenas_o_incompletas_se_ignoran() -> None:
    assert parsear_progreso("[download] Destination: C:\\x\\v.mp4") is None
    assert parsear_progreso(f"{PROGRESO_PREFIJO}1024 499555") is None
    assert parsear_progreso("") is None


def test_extrae_la_ruta_de_descarga_y_de_fusion() -> None:
    assert parsear_destino(r"[download] Destination: C:\x\v.mp4") == Path(r"C:\x\v.mp4")
    assert parsear_destino(
        r'[Muxer] Merging formats into "C:\x\Salida.mp4"'
    ) == Path(r"C:\x\Salida.mp4")
    assert parsear_destino(
        r"[ExtractAudio] Destination: C:\x\Cancion.mp3"
    ) == Path(r"C:\x\Cancion.mp3")


def test_un_archivo_ya_descargado_tambien_da_su_ruta() -> None:
    assert parsear_destino(
        r"[download] C:\x\v.mp4 has already been downloaded"
    ) == Path(r"C:\x\v.mp4")


def test_lineas_sin_ruta_se_ignoran() -> None:
    assert parsear_destino("[info] Descargando 1 formato(s): 399+251") is None
    assert parsear_destino("[download]  12.3% of 499.55KiB") is None


def test_el_comando_pide_el_progreso_en_formato_propio() -> None:
    cmd = add_common_args(build_yt_dlp_cmd("https://ejemplo/x", "video"), "https://ejemplo/x", False)
    assert "--progress-template" in cmd
    plantilla = cmd[cmd.index("--progress-template") + 1]
    assert plantilla.startswith("download:" + PROGRESO_PREFIJO)


def test_formateo_de_bytes() -> None:
    assert formatear_bytes(None) == "--"
    assert formatear_bytes(0) == "0 B"
    assert formatear_bytes(500) == "500 B"
    assert formatear_bytes(499555) == "487.8 KB"
    assert formatear_bytes(1048576) == "1.0 MB"


def test_formateo_de_velocidad() -> None:
    assert formatear_velocidad(None) == ""
    assert formatear_velocidad(0) == ""
    assert formatear_velocidad(5781686.744) == "5.5 MB/s"


def test_formateo_de_eta() -> None:
    assert formatear_eta(None) == ""
    assert formatear_eta(65) == "1:05"
    assert formatear_eta(3725) == "1:02:05"
