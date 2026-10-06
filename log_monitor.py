"""Monitor de logs en tiempo real para Omnium Suite.

Ejecuta: python log_monitor.py
Muestra los logs en tiempo real con colores por nivel.
"""

import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR / "logs"

COLORS = {
    "DEBUG": "\033[36m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[35m",
}
RESET = "\033[0m"


def get_latest_log() -> Path | None:
    if not LOG_DIR.exists():
        return None
    logs = sorted(LOG_DIR.glob("omnium_*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def tail_log(log_file: Path):
    with open(log_file, encoding="utf-8") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            for level, color in COLORS.items():
                if f" {level} " in line or f" | {level} " in line:
                    print(f"{color}{line.rstrip()}{RESET}")
                    break
            else:
                print(line.rstrip())


def main():
    print(f"Omnium Log Monitor - Watching {LOG_DIR}")
    print("Press Ctrl+C to exit\n")

    log_file = get_latest_log()
    if not log_file:
        print("No log file found. Start the app first.")
        sys.exit(1)

    print(f"Watching: {log_file.name}\n")

    try:
        tail_log(log_file)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()
