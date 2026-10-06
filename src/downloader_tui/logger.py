"""Logging centralizado para Omnium Suite."""

import logging
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent.parent
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"omnium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

_FORMAT = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"

_fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATEFMT))

_ch = logging.StreamHandler(sys.stdout)
_ch.setLevel(logging.INFO)
_ch.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATEFMT))

_root = logging.getLogger("omnium")
_root.setLevel(logging.DEBUG)
_root.addHandler(_fh)
_root.addHandler(_ch)

logger = logging.getLogger("omnium")

logger.info(f"Logging initialized. Log file: {LOG_FILE}")
