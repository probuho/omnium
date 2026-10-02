#!/usr/bin/env python3
"""Script de type checking con mypy."""

import sys
import subprocess


def run_typecheck() -> bool:
    """Ejecuta mypy."""
    result = subprocess.run(
        ["mypy", "src/downloader_tui"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return False
    print("OK: Type check passed")
    return True


if __name__ == "__main__":
    success = run_typecheck()
    sys.exit(0 if success else 1)