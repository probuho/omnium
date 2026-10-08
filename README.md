<p align="center">
  <img src="assets/logo.svg" alt="Omnium Suite Logo" width="200"/>
</p>

<h1 align="center">Omnium Suite</h1>
<p align="center">
  <strong>Universal Multimedia Downloader TUI</strong> — Terminal moderna, modular y extensible para descargar video, audio e imágenes de 1000+ sitios.
</p>

<p align="center">
  <a href="https://github.com/probuho/omnium/actions/workflows/ci.yml">
    <img src="https://github.com/probuho/omnium/actions/workflows/ci.yml/badge.svg" alt="CI Status"/>
  </a>
  <a href="https://github.com/probuho/omnium/releases/latest">
    <img src="https://img.shields.io/github/v/release/probuho/omnium?label=version&color=783CBC" alt="Latest Release"/>
  </a>
  <a href="https://github.com/probuho/omnium/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/probuho/omnium?color=2DC9D1" alt="License"/>
  </a>
  <a href="https://github.com/probuho/omnium/stargazers">
    <img src="https://img.shields.io/github/stars/probuho/omnium?style=social" alt="Stars"/>
  </a>
  <a href="https://github.com/probuho/omnium/issues">
    <img src="https://img.shields.io/github/issues/probuho/omnium?color=FF585F" alt="Issues"/>
  </a>
  <br/>
  <a href="https://github.com/probuho/omnium/actions/workflows/ci.yml">
    <img src="https://img.shields.io/badge/ruff-passing-783CBC?logo=ruff&logoColor=white" alt="Ruff"/>
  </a>
  <a href="https://github.com/probuho/omnium/actions/workflows/ci.yml">
    <img src="https://img.shields.io/badge/mypy-passing-2DC9D1?logo=mypy&logoColor=white" alt="MyPy"/>
  </a>
  <a href="https://github.com/probuho/omnium/actions/workflows/ci.yml">
    <img src="https://img.shields.io/badge/pytest-19%20passed-FF585F?logo=pytest&logoColor=white" alt="Tests"/>
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11+"/>
  </a>
</p>

<p align="center">
  <!-- <img src="assets/demo.gif" alt="Omnium Suite Demo" width="800"/> -->
</p>

---

## ✨ Características

| Categoría | Detalles |
|-----------|----------|
| **Video** | YouTube, Vimeo, Twitch, TikTok, Twitter/X, Instagram, Facebook, Reddit, Pinterest, Dailymotion, Crunchyroll, Netflix*, Hulu*, HBO* y 1000+ más |
| **Audio** | SoundCloud, Bandcamp, Mixcloud, Audiomack, Spotify (podcasts), Apple Music* |
| **Imágenes** | Instagram, Pinterest, Twitter/X, Reddit, Tumblr, Imgur, etc. |
| **Calidad** | 8K → 480p, audio VBR/320/256/192/128 kbps, formatos: MP4, MP3, M4A, OPUS, FLAC, WAV, JPG, PNG, WEBP |
| **Autenticación** | `cookies.txt` para contenido privado/edad-restringido/streaming premium |

> *Requiere `cookies.txt` con sesión válida

---

## 🚀 Instalación

### Opción A: Instalación directa (recomendada)
```bash
pip install git+https://github.com/probuho/omnium.git
```

### Opción B: Desde código fuente
```bash
git clone https://github.com/probuho/omnium.git
cd omnium
pip install -e ".[dev]"
```

### Opción C: Ejecutable standalone (próximamente)
```bash
# pyinstaller --onefile --add-binary "ffmpeg.exe;." src/downloader_tui/__main__.py
```

> **Requisitos:** Python 3.11+, FFmpeg (incluido en el repo), `yt-dlp`, `textual`, `pyperclip`

---

## 🎮 Uso Rápido

```bash
# Lanzar TUI
omnium

# O directamente
python -m downloader_tui
```

### Atajos Principales

| Tecla | Acción |
|-------|--------|
| `Enter` | Descargar |
| `Ctrl+V` | Pegar URL + detectar calidades |
| `Tab` / `Shift+Tab` | Cambiar pestaña (Video/Audio/Imagen) |
| `H` | Historial |
| `S` | Configuración |
| `I` | Sitios compatibles |
| `A` | Accesibilidad (atajos) |
| `C` | Créditos |
| `ESC` | Volver / Salir |
| `Q` | Salir |

---

## ⚙️ Configuración

La configuración se guarda en `config.json` (persistente entre sesiones):

```json
{
  "download_dir": "D:\\Vídeo",
  "cookies_file": "cookies.txt",
  "ffmpeg_dir": ".",
  "theme": "textual-dark",
  "video_quality": "bestvideo+bestaudio/best",
  "audio_format": "m4a",
  "audio_quality": "0",
  "image_format": "jpg"
}
```

### En la TUI (`S` → Configuración):
- ✏️ Editar rutas de descargas, cookies, FFmpeg
- 🎨 Cambiar tema (Oscuro/Claro/Sistema)
- 💾 Guardar / 🔄 Restablecer defaults
- 🔍 Verificar cookies / 📁 Abrir carpeta / 🧪 Probar FFmpeg
- ♿ Accesibilidad (A) / 📜 Créditos (C)

---

## 📸 Capturas

### Pantalla Principal
```
  ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ██████╗  ██████╗ ████████╗███████╗
 ██╔════╝██═══██╗████╗ ████║██══██╗██║     ██═══██╗██═══██╗╚══██══╝██════╝
 ██║     ██║   ██║██╔████╔██║██████╔╝ ██║     ██║  ██║██║   ██║   ██║   ███████╗
 ██║     ██═══██══╝██══════╝╚══════╝╚══════╝╚══════╝╚══════╝    ╚══════╝╚══════╝

═══════════════════════════════════════════════════════════════════════════════

URL:
> https://youtube.com/watch?v=...  •  pegar con Ctrl+V
✓ URL válida

Video  Audio  Imagen

Calidad y formato se configuran en Config (S)

Descargar (Enter)  Limpiar (Ctrl+L)  Pegar (Ctrl+V)  Sitios (I)  Historial (H)  Config (S)

🔒 Privacidad: Esta herramienta se ejecuta 100% en tu equipo...
```

### Modal de Calidades (Ctrl+V en URL válida)
```
┌──────────────────── Calidades Disponibles ────────────────────┐
│ URL: https://youtube.com/watch?v=...                          │
│ ✅ Se detectaron 12 formatos                                   │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ 1. ID: 137  Ext: mp4  Res: 1920x1080  (video only)        │ │
│ │ 2. ID: 248  Ext: webm  Res: 1920x1080  (video only)       │ │
│ │ 3. ID: 140  Ext: m4a  Res: audio only  (audio only)       │ │
│ └────────────────────────────────────────────────────────────┘ │
│ [Descargar] [Cancelar]                                         │
└────────────────────────────────────────────────────────────────┘
```

### Configuración
```
┌─────────────────── Configuración ────────────────────┐
│ Carpeta de descargas:                                 │
│ [ D:\Vídeo                                    ]       │
│ Archivo de cookies:                                   │
│ [ cookies.txt                               ]        │
│ Directorio FFmpeg:                                    │
│ [ .                                               ]    │
│ Tema:                                                 │
│ ▸ Oscuro (textual-dark)                               │
│   Claro (textual-light)                               │
│   Sistema (textual-ansi)                              │
│                                                       │
│ [ Guardar ] [ Restablecer ]                           │
│                                                       │
│ [ Verificar cookies ] [ Abrir carpeta ] [ Probar FFmpeg ]│
│ [ Accesibilidad (A) ] [ Creditos (C) ]               │
│                                                       │
│ ESC: Volver  |  A: Accesibilidad  |  C: Creditos      │
└────────────────────────────────────────────────────────┘
```

---

## 🔧 Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Verificación completa
make check        # lint + typecheck + test

# Formateo
make fmt

# Tests
make test

# Type checking
make typecheck

# Linting
make lint
```

### Arquitectura

```mermaid
graph TD
    A[__main__.py] --> B[OmniumSuiteApp]
    B --> C[MainScreen]
    B --> D[Theme Manager]
    B --> E[Logger]

    C --> F[SitesScreen]
    C --> G[HistoryScreen]
    C --> H[SettingsScreen]
    C --> I[QualityDetectionModal]

    H --> J[AccessibilityScreen]
    H --> K[CreditsScreen]

    C --> L[DownloaderService]
    I --> L
    L --> M[yt-dlp subprocess]
    L --> N[FFmpegService]
    L --> O[QualityService]
    L --> P[CookiesService]

    H --> Q[ConfigManager]
    Q --> R[config.json]

    D --> S[Monokai Theme]
    D --> T[textual-dark]
    D --> U[textual-light]
    D --> V[textual-ansi]
```

### Estructura del Proyecto
```
src/downloader_tui/
├── __init__.py
├── __main__.py            # Entry point (omnium)
├── app.py                 # App principal + Theme registration
├── config.py              # Config JSON persistente
├── logger.py              # Logging centralizado (file + console)
├── constants/             # ASCII_LOGO, SITES_LIST, textos
├── models/errors.py       # ErrorCategory, DownloadError
├── services/
│   ├── downloader.py      # run_download, build_yt_dlp_cmd
│   ├── quality.py         # detect_available_formats
│   ├── cookies.py         # validate_cookies_file
│   └── ffmpeg.py          # test_ffmpeg
├── screens/
│   ├── main.py            # MainScreen (URL, tabs, botones)
│   ├── sites.py           # SitesScreen
│   ├── history.py         # HistoryScreen
│   ├── settings.py        # SettingsScreen
│   ├── accessibility.py   # AccessibilityScreen
│   ├── credits.py         # CreditsScreen
│   ├── base.py            # BaseScreen + nav-hint
│   └── modals/
│       ├── confirm.py     # ConfirmDialog
│       └── quality.py     # QualityDetectionModal
├── styles/css.py          # MONOKAI_CSS
└── utils/                 # Utilidades
```

### Flujo de Usuario

```mermaid
flowchart TD
    A[Inicio] --> B[MainScreen]
    B --> C{URL válida?}
    C -->|Sí| D[QualityDetectionModal]
    C -->|No| E[Mostrar error]
    D --> F{Seleccionar calidad?}
    F -->|Sí| G[DownloaderService]
    F -->|No| B
    G --> H{Descarga exitosa?}
    H -->|Sí| I[Mostrar éxito + archivo]
    H -->|No| J[Mostrar error + sugerencia]
    I --> B
    J --> B

    B --> K[SettingsScreen]
    K --> L[Guardar/Restablecer config]
    K --> M[AccessibilityScreen]
    K --> N[CreditsScreen]

    B --> O[HistoryScreen]
    O --> P[Ver/Eliminar archivos]

    B --> Q[SitesScreen]
```

### Flujo de Datos

```mermaid
sequenceDiagram
    participant U as Usuario
    participant MS as MainScreen
    participant Q as QualityModal
    participant D as DownloaderService
    participant Y as yt-dlp
    participant F as FileSystem

    U->>MS: Ingresa URL
    MS->>MS: Valida URL
    U->>MS: Ctrl+V (pegar)
    MS->>Q: push_screen(QualityDetectionModal)
    Q->>D: detect_available_formats()
    D->>Y: --list-formats
    Y-->>D: Lista de formatos
    D-->>Q: Formatos disponibles
    Q->>U: Selecciona calidad
    Q->>D: dismiss({format_id, url})
    D->>Y: download --format ...
    Y->>F: Escribe archivo
    F-->>D: Archivo creado
    D-->>MS: DownloadResult
    MS->>U: Muestra resultado
```

---

## 📋 Requisitos de `cookies.txt`

Para contenido privado/edad-restringido/streaming premium:

1. Instala extensión **Get cookies.txt LOCALLY** (Chrome/Firefox)
2. Exporta cookies del sitio (YouTube, Instagram, etc.)
3. Guarda como `cookies.txt` en la carpeta del proyecto
4. Verifica en Config → **Verificar cookies**

> ⚠️ **Privacidad:** El archivo `cookies.txt` NUNCA sale de tu equipo. Solo yt-dlp lo usa localmente.

---

## 🛡️ Privacidad

> **Esta herramienta se ejecuta 100% en tu equipo.**  
> No se envían datos, URLs, ni credenciales a servidores externos.  
> Solo `yt-dlp` (local) contacta directamente al sitio de origen para descargar el contenido que tú solicitas.

---

## 📄 Licencia

MIT License — Ver [LICENSE](LICENSE) para detalles.

---

## 🙏 Créditos

Desarrollado con:
- [Textual](https://github.com/Textualize/textual) — TUI framework excelente
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — El mejor descargador de video/audio
- [FFmpeg](https://ffmpeg.org/) — Procesamiento multimedia estándar

---

## 🤝 Contribuir

1. Fork el repo
2. Crea branch (`git checkout -b feature/nueva-funcion`)
3. Commit (`git commit -m 'feat: nueva función'`)
4. Push (`git push origin feature/nueva-funcion`)
5. Abre Pull Request

---

## 📞 Soporte

- 🐛 [Issues](https://github.com/probuho/omnium/issues) — Bugs y feature requests
- 💬 [Discussions](https://github.com/probuho/omnium/discussions) — Preguntas y ayuda
- 📖 [Wiki](https://github.com/probuho/omnium/wiki) — Documentación extendida

---

<p align="center">
  <sub>Hecho con ❤️ para la comunidad — <a href="https://github.com/probuho">@probuho</a></sub>
</p>