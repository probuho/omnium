"""Tests end-to-end reales: descarga de verdad contra un servidor local.

Son los unicos que cubren la cadena completa (comando -> yt-dlp -> ffmpeg ->
archivo final). Los demas tests comprueban piezas sueltas; estos comprueban que
la app hace lo que dice hacer.

Por que existen: la plantilla del nombre de archivo estaba mal escrita y TODA
descarga fallaba con exit 2 antes de empezar. Los 19 tests de entonces pasaban
igual, porque ninguno ejecutaba yt-dlp. Verificar a mano una vez no protege
nada: esto si, porque corre en cada push.

Nada de red externa: el medio se genera con el ffmpeg incluido y se sirve por
HTTP en loopback.
"""

import functools
import http.server
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from downloader_tui import config
from downloader_tui.services.downloader import run_download

RAIZ = Path(__file__).parent.parent
FFMPEG = RAIZ / "ffmpeg.exe"
FFPROBE = RAIZ / "ffprobe.exe"

sin_ffmpeg = pytest.mark.skipif(
    not FFMPEG.exists() or not FFPROBE.exists(),
    reason="hacen falta los ffmpeg.exe/ffprobe.exe incluidos en el repositorio",
)


@pytest.fixture(scope="module")
def medio(tmp_path_factory) -> Path:
    """Genera un video corto con pista de audio usando el ffmpeg incluido."""
    carpeta = tmp_path_factory.mktemp("medio")
    destino = carpeta / "Mi Cancion de Prueba.mp4"
    subprocess.run(
        [
            str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=3:size=320x240:rate=15",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
            "-c:v", "libx264", "-c:a", "aac", "-shortest", str(destino),
        ],
        check=True,
    )
    return destino


class _Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:  # silencio en la salida de pytest
        pass


@pytest.fixture
def servidor(medio: Path) -> str:
    """Sirve la carpeta del medio por HTTP en loopback, en un puerto libre."""
    manejador = functools.partial(_Handler, directory=str(medio.parent))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), manejador)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}/{quote(medio.name)}"
    finally:
        httpd.shutdown()
        httpd.server_close()


@pytest.fixture
def descargas(tmp_path, monkeypatch) -> Path:
    """Apunta la descarga a un temporal: ni una escritura en D:\\Vídeo."""
    carpeta = tmp_path / "descargas"
    carpeta.mkdir()
    monkeypatch.setattr(
        config, "_config", dict(config.DEFAULT_CONFIG, download_dir=str(carpeta))
    )
    return carpeta


def _etiquetas(archivo: Path) -> dict[str, str]:
    """Lee las etiquetas del archivo con el ffprobe incluido."""
    salida = subprocess.run(
        [
            str(FFPROBE), "-hide_banner", "-loglevel", "error",
            "-show_entries", "format_tags", "-of", "default=noprint_wrappers=1",
            str(archivo),
        ],
        capture_output=True, text=True, check=True,
    ).stdout
    etiquetas: dict[str, str] = {}
    for linea in salida.splitlines():
        if linea.startswith("TAG:") and "=" in linea:
            clave, _, valor = linea[4:].partition("=")
            etiquetas[clave.lower()] = valor
    return etiquetas


@sin_ffmpeg
async def test_descarga_de_video_completa(servidor: str, descargas: Path) -> None:
    """La cadena entera: comando valido, descarga, archivo final en su sitio."""
    avances = []
    resultado = await run_download(
        servidor, "video", use_cookies=False, on_progress=avances.append
    )

    assert resultado.success is True, resultado.message
    assert resultado.file_path is not None, "no informo de ningun archivo"
    assert resultado.file_path.exists(), "el archivo informado no existe"
    assert resultado.file_path.parent == descargas


@sin_ffmpeg
async def test_el_progreso_llega_en_streaming(servidor: str, descargas: Path) -> None:
    """Sin streaming la barra se quedaba clavada en 0% toda la descarga."""
    avances = []
    await run_download(servidor, "video", use_cookies=False, on_progress=avances.append)

    assert avances, "no llego ni un aviso de progreso"
    porcentajes = [a.porcentaje for a in avances if a.porcentaje is not None]
    assert porcentajes, "ningun aviso traia porcentaje"
    assert porcentajes[0] < porcentajes[-1], "el progreso no avanza"
    assert porcentajes[-1] == pytest.approx(100.0)


@sin_ffmpeg
async def test_no_informa_de_un_archivo_ajeno(servidor: str, descargas: Path) -> None:
    """Un archivo mas reciente en la carpeta no debe pasar por la descarga.

    El codigo anterior cogia "el mas reciente del directorio", asi que este
    señuelo con fecha futura se habria reportado como lo descargado.
    """
    señuelo = descargas / "otro archivo.mp4"
    señuelo.write_bytes(b"no soy la descarga")
    futuro = time.time() + 3600
    os.utime(señuelo, (futuro, futuro))

    resultado = await run_download(servidor, "video", use_cookies=False)

    assert resultado.success is True, resultado.message
    assert resultado.file_path is not None
    assert resultado.file_path != señuelo, "informo del señuelo, no de la descarga"


@sin_ffmpeg
async def test_el_audio_descargado_lleva_etiquetas(
    servidor: str, descargas: Path
) -> None:
    """Musica de verdad: nombre utilizable y etiquetas dentro del archivo."""
    resultado = await run_download(servidor, "audio", use_cookies=False)

    assert resultado.success is True, resultado.message
    archivo = resultado.file_path
    assert archivo is not None and archivo.exists()
    assert archivo.suffix == ".m4a", f"formato inesperado: {archivo.suffix}"

    # Nombre de biblioteca de musica, no de video.
    assert " - " in archivo.stem, f"nombre poco util: {archivo.name}"
    assert archivo.stem.startswith("Desconocido - ")

    etiquetas = _etiquetas(archivo)
    assert etiquetas.get("title"), "el archivo no lleva etiqueta title"
    # yt-dlp escribe el literal "NA" en los campos ausentes y se colaba como
    # artista; eso seria basura dentro del archivo.
    assert etiquetas.get("artist") != "NA"


@sin_ffmpeg
async def test_un_fallo_se_reporta_con_su_motivo(descargas: Path) -> None:
    """Un error de yt-dlp no puede acabar en 'Error desconocido' sin mas."""
    resultado = await run_download(
        "http://127.0.0.1:1/no-existe", "video", use_cookies=False
    )

    assert resultado.success is False
    assert resultado.error is not None
    assert resultado.error.message
    assert resultado.error.message != "Error desconocido"
    assert resultado.error.suggestion


def _pistas_adjuntas(archivo: Path) -> int:
    """Cuantas pistas de imagen adjunta (caratula) tiene el archivo."""
    salida = subprocess.run(
        [
            str(FFPROBE), "-hide_banner", "-loglevel", "error",
            "-show_entries", "stream=codec_name:stream_disposition=attached_pic",
            "-of", "default=noprint_wrappers=1", str(archivo),
        ],
        capture_output=True, text=True, check=True,
    ).stdout
    return salida.count("attached_pic=1")


@sin_ffmpeg
async def test_la_caratula_acaba_dentro_del_archivo(tmp_path: Path) -> None:
    """La caratula se adjunta al audio, y se comprueba DENTRO con ffprobe.

    Es el relevo de --embed-thumbnail: ese postprocesado de yt-dlp necesita
    mutagen o AtomicParsley para m4a y, si no estan, un ffmpeg que fallaba
    tumbaba la descarga entera.
    """
    from downloader_tui.services.downloader import _adjuntar_caratula

    audio = tmp_path / "Artista - Cancion.m4a"
    portada = tmp_path / "Artista - Cancion.jpg"
    subprocess.run(
        [str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", "sine=frequency=440:duration=2", "-c:a", "aac", str(audio)],
        check=True,
    )
    subprocess.run(
        [str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", "testsrc=duration=1:size=200x200:rate=1",
         "-frames:v", "1", str(portada)],
        check=True,
    )
    assert _pistas_adjuntas(audio) == 0

    resultado = await _adjuntar_caratula(audio)

    assert resultado == audio
    assert audio.exists()
    assert _pistas_adjuntas(audio) == 1, "la caratula no quedo dentro del archivo"
    # La caratula suelta ya no hace falta y se limpia.
    assert not portada.exists()
    # Y no queda ningun temporal por medio.
    assert not list(tmp_path.glob("*__con_caratula*"))


@sin_ffmpeg
async def test_si_no_hay_caratula_el_audio_no_se_toca(tmp_path: Path) -> None:
    """Sin caratula, adjuntar no puede romper ni alterar el audio."""
    from downloader_tui.services.downloader import _adjuntar_caratula

    audio = tmp_path / "Artista - Cancion.m4a"
    subprocess.run(
        [str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-c:a", "aac", str(audio)],
        check=True,
    )
    antes = audio.stat().st_size

    assert await _adjuntar_caratula(audio) == audio
    assert audio.stat().st_size == antes
    assert _pistas_adjuntas(audio) == 0
