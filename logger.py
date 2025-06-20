"""Simple structured logger for Atlas."""
from __future__ import annotations

import json
import logging
from logging import Handler, Logger
from pathlib import Path
from typing import Any, Dict

LOG_DIR = Path.home() / ".atlas" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE_PATH = LOG_DIR / "atlas.log.jsonl"


class JsonLFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  #noqa: D401
        payload: Dict[str, Any] = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
            "name": record.name,
        }
        return json.dumps(payload)


def get_logger(name: str = "atlas") -> Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  #already configured

    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    fh.setFormatter(JsonLFormatter())
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(sh)

    return logger


def add_handler(handler: Handler, name: str = "atlas"):
    """Add a new handler to the specified logger."""
    logger = logging.getLogger(name)
    logger.addHandler(handler)
