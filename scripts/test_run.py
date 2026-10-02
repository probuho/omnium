#!/usr/bin/env python3
"""Script de ejecución de tests."""

import sys
import subprocess


def run_tests() -> bool:
    """Ejecuta pytest."""
    result = subprocess.run(
        ["pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
    print("OK: Tests passed")
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)