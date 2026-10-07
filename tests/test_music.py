"""Tests del modo musica: etiquetas, caratula y nombre de archivo utilizable.

Antes el camino de Audio extraia el audio correctamente pero el archivo salia
sin title/artist/album y sin portada (comprobado con ffprobe), asi que no servia
para una biblioteca de musica.
"""

import sys
from pathlib import Path

from yt_dlp import YoutubeDL

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from downloader_tui.services.downloader import (
    add_common_args,
    build_yt_dlp_cmd,
    plantilla_de_salida,
)

URL = "https://www.youtube.com/watch?v=NQo91kZ7amM"


def _cmd(media_type: str, url: str = URL) -> list[str]:
    return add_common_args(
        build_yt_dlp_cmd(url, media_type), url, use_cookies=False, media_type=media_type
    )


def _valor(cmd: list[str], opcion: str) -> str:
    return cmd[cmd.index(opcion) + 1]


def test_la_plantilla_de_audio_es_valida_para_yt_dlp() -> None:
    error = YoutubeDL.validate_outtmpl(plantilla_de_salida("audio"))
    assert error is None, f"yt-dlp rechaza la plantilla de audio: {error}"


def test_la_plantilla_de_video_sigue_siendo_valida() -> None:
    error = YoutubeDL.validate_outtmpl(plantilla_de_salida("video"))
    assert error is None, f"yt-dlp rechaza la plantilla de video: {error}"


def test_el_audio_se_nombra_con_artista_y_titulo() -> None:
    plantilla = _valor(_cmd("audio"), "--output")
    ydl = YoutubeDL({"outtmpl": {"default": plantilla}, "quiet": True, "no_warnings": True})

    con_artista = ydl.prepare_filename(
        {"title": "Cancion", "ext": "m4a", "artist": "La Banda", "id": "x"}
    )
    assert Path(con_artista).name == "La Banda - Cancion.m4a"

    # Sin campo artist: cae al canal que subio la cancion.
    por_canal = ydl.prepare_filename(
        {"title": "Cancion", "ext": "m4a", "uploader": "Canal Musical", "id": "x"}
    )
    assert Path(por_canal).name == "Canal Musical - Cancion.m4a"

    # Sin nada: literal honesto, nunca un nombre vacio ni "NA".
    sin_datos = ydl.prepare_filename({"title": "Cancion", "ext": "m4a", "id": "x"})
    assert Path(sin_datos).name == "Desconocido - Cancion.m4a"


def test_el_modo_audio_pide_etiquetas_y_caractula() -> None:
    cmd = _cmd("audio")
    assert "--embed-metadata" in cmd
    # La caratula se DESCARGA con el audio y se adjunta despues en
    # _adjuntar_caratula(). Con --embed-thumbnail, yt-dlp necesita mutagen o
    # AtomicParsley para m4a y, si no estan, cae a un ffmpeg que en la practica
    # fallaba ("Unable to embed using ffprobe & ffmpeg; Conversion failed!"),
    # tumbando una descarga de audio que ya estaba perfecta.
    assert "--write-thumbnail" in cmd
    assert "--embed-thumbnail" not in cmd
    # La caratula en jpg para que la lea cualquier reproductor.
    assert _valor(cmd, "--convert-thumbnails") == "jpg"
    # El artista sale del canal cuando el sitio no da uno propio. La regex
    # descarta el "NA" literal de yt-dlp para no etiquetar con basura.
    assert "uploader:(?P<meta_artist>^(?!NA$).+)" in cmd


def test_adjuntar_caratula_por_contenedor() -> None:
    """ffmpeg solo puede adjuntar en algunos contenedores; en el resto se deja."""
    from downloader_tui.services.downloader import _argumentos_caratula

    for contenedor in (".m4a", ".mp4", ".m4v", ".mov"):
        argumentos = _argumentos_caratula(contenedor)
        assert argumentos is not None, contenedor
        assert "attached_pic" in argumentos
    assert _argumentos_caratula(".mp3") is not None
    # opus/flac/ogg necesitan mutagen: mejor caratula al lado que fallo.
    for contenedor in (".opus", ".flac", ".ogg", ".wav"):
        assert _argumentos_caratula(contenedor) is None, contenedor


def test_encuentra_la_caratula_dejada_junto_al_audio(tmp_path) -> None:
    from downloader_tui.services.downloader import _buscar_portada

    audio = tmp_path / "Artista - Cancion.m4a"
    audio.write_bytes(b"audio")
    assert _buscar_portada(audio) is None
    portada = tmp_path / "Artista - Cancion.jpg"
    portada.write_bytes(b"jpg")
    assert _buscar_portada(audio) == portada


def test_el_modo_video_no_lleva_las_opciones_de_musica() -> None:
    cmd = _cmd("video")
    assert "--embed-metadata" not in cmd
    assert "--extract-audio" not in cmd


def test_el_modo_audio_no_mezcla_video() -> None:
    cmd = _cmd("audio")
    # --extract-audio es un flag sin valor: se comprueba su presencia, no el
    # argumento siguiente (que es --audio-format).
    assert "--extract-audio" in cmd
    assert "--merge-output-format" not in cmd


def test_un_video_dentro_de_una_lista_no_arrastra_la_lista() -> None:
    """Pegar una cancion de una radio automatica bajaba la lista entera."""
    from downloader_tui.services.downloader import es_video_suelto_en_lista

    assert es_video_suelto_en_lista(
        "https://www.youtube.com/watch?v=C-u5WLJ9Yk4&list=RDMMrMqayO-"
    )
    assert es_video_suelto_en_lista("https://youtube.com/watch?v=abc&list=PL1")
    # Una lista pura si se descarga como lista.
    assert not es_video_suelto_en_lista("https://www.youtube.com/playlist?list=PL1")
    # Un video suelto no necesita el flag.
    assert not es_video_suelto_en_lista("https://www.youtube.com/watch?v=C-u5WLJ9Yk4")

    cmd = _cmd("audio", "https://www.youtube.com/watch?v=C-u5WLJ9Yk4&list=RDMMrMqayO-")
    assert "--no-playlist" in cmd
    cmd_lista = _cmd("audio", "https://www.youtube.com/playlist?list=PL1")
    assert "--no-playlist" not in cmd_lista


def test_las_cookies_del_navegador_mandan_sobre_el_archivo(tmp_path, monkeypatch) -> None:
    """YouTube corta la sesion en cuanto el cookies.txt se queda viejo."""
    from downloader_tui import config
    from downloader_tui.services.downloader import add_common_args, build_yt_dlp_cmd

    archivo = tmp_path / "cookies.txt"
    archivo.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")

    base = dict(config.DEFAULT_CONFIG, cookies_file=str(archivo))

    monkeypatch.setattr(config, "_config", dict(base, cookies_from_browser=""))
    cmd = add_common_args(build_yt_dlp_cmd(URL, "video"), URL, True)
    assert "--cookies" in cmd
    assert "--cookies-from-browser" not in cmd

    monkeypatch.setattr(config, "_config", dict(base, cookies_from_browser="firefox"))
    cmd = add_common_args(build_yt_dlp_cmd(URL, "video"), URL, True)
    assert cmd[cmd.index("--cookies-from-browser") + 1] == "firefox"
    # Si se leen del navegador, no se pasa ademas el archivo.
    assert "--cookies" not in cmd

    # Con las cookies desactivadas no se pasa ninguna de las dos cosas.
    monkeypatch.setattr(config, "_config", dict(base, cookies_from_browser="firefox"))
    cmd = add_common_args(build_yt_dlp_cmd(URL, "video"), URL, False)
    assert "--cookies" not in cmd
    assert "--cookies-from-browser" not in cmd
