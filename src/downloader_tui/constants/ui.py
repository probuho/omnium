"""Constantes de UI: textos, logo ASCII, accesibilidad, créditos."""

ASCII_LOGO = r"""
  +-------------------------------------------------------------+
  |  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  _  |
  | / \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \|
  | \_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/|
  |                                                             |
  |   O M N I U M   S U I T E   -   V i d e o   D o w n l o a d |
  |                                                             |
  +-------------------------------------------------------------+
"""

ACCESSIBILITY_TEXT = """
Atajos Globales (disponibles en todas las pantallas):
  ESC           - Volver / Salir
  Q             - Salir de la aplicacion
  Enter         - Descargar (en pantalla principal)
  Ctrl+V        - Pegar URL del portapapeles
  Ctrl+C        - Copiar URL actual
  Ctrl+L        - Limpiar campo URL
  Tab / Shift+Tab - Cambiar pestana (Video/Audio/Imagen)
  Flechas       - Navegar entre botones y opciones
  H             - Abrir Historial
  S             - Abrir Configuracion
  I             - Abrir Sitios Compatibles
  A             - Abrir Accesibilidad (desde Configuracion)
  C             - Abrir Creditos (desde Configuracion)

Pantalla Principal:
  Flechas Izq/Der - Navegar entre botones de accion
  Flechas Arr/Ab - Cambiar foco entre input y botones
  Enter en boton  - Ejecutar accion del boton

Pantalla de Historial:
  R             - Actualizar lista
  Delete        - Eliminar archivo seleccionado
  Flechas Arr/Ab - Navegar filas de la tabla

Pantalla de Configuracion:
  Flechas Arr/Ab - Navegar entre campos y botones
  Enter en Input  - Editar valor
  Enter en Boton  - Ejecutar accion
  A             - Abrir Accesibilidad
  C             - Abrir Creditos

Pantalla de Sitios Compatibles:
  Flechas Arr/Ab - Scroll en la lista
  Page Up/Down  - Scroll rapido

Pantalla de Accesibilidad / Creditos:
  Flechas Arr/Ab - Scroll en el texto
  Page Up/Down  - Scroll rapido
"""

CREDITS_TEXT = """
Omnium Suite - Universal Video Downloader
Version 1.0

Desarrollado con:
  - Python 3
  - Textual (TUI framework) - https://github.com/Textualize/textual
  - yt-dlp (descarga de video/audio) - https://github.com/yt-dlp/yt-dlp
  - FFmpeg (procesamiento multimedia) - https://ffmpeg.org/

Agradecimientos especiales:
  - Equipo de Textualize por Textual, un framework TUI excelente
  - Equipo de yt-dlp por el mejor descargador de video/audio
  - Comunidad de FFmpeg por el procesamiento multimedia estandar

Licencia: MIT
Este software se ejecuta 100% localmente en tu equipo.
No se recopilan, envian ni almacenan datos personales.
"""
