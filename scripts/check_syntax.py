#!/usr/bin/env python3
"""Script de verificación de sintaxis."""

import sys
import subprocess
from pathlib import Path


def check_syntax() -> bool:
    """Verifica sintaxis de todos los archivos .py en src/downloader_tui."""
    src_dir = Path(__file__).parent.parent / "src" / "downloader_tui"
    py_files = list(src_dir.rglob("*.py"))

    if not py_files:
        print("No se encontraron archivos Python")
        return False

    print(f"Verificando {len(py_files)} archivos...")
    for py_file in py_files:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(py_file)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"ERROR en {py_file.relative_to(Path.cwd())}:")
            print(result.stderr)
            return False

    print("OK: Sintaxis valida en todos los archivos")
    return True


if __name__ == "__main__":
    success = check_syntax()
    sys.exit(0 if success else 1)