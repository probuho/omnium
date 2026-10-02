from setuptools import setup

setup(
    name="universal-video-downloader",
    version="1.0.0",
    description="TUI para descargar videos con yt-dlp",
    py_modules=["downloader_tui"],
    install_requires=[
        "yt-dlp",
        "textual>=0.50.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "downloader = downloader_tui:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["ffmpeg.exe", "ffprobe.exe", "ffplay.exe", "cookies.txt"],
    },
    python_requires=">=3.8",
)