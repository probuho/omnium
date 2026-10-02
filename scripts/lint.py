#!/usr/bin/env python3
"""Script de linting con ruff."""

import sys
import subprocess


def run_lint() -> bool:
    """Ejecuta ruff check."""
    result = subprocess.run(
        ["ruff", "check", "src/", "tests/"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return False
    print("OK: Ruff check passed")
    return True


def run_format_check() -> bool:
    """Ejecuta ruff format --check."""
    result = subprocess.run(
        ["ruff", "format", "--check", "src/", "tests/"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return False
    print("OK: Ruff format check passed")
    return True


if __name__ == "__main__":
    success = run_lint() and run_format_check()
    sys.exit(0 if success else 1)