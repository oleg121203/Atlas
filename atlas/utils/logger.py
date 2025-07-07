"""Simple structured logger for Atlas."""

from __future__ import annotations

import json
import logging
import os
from logging import Handler, Logger
from pathlib import Path
from typing import Any, Dict

LOG_DIR = Path.home() / ".atlas" / "logs"
LOG_FILE_PATH = LOG_DIR / "atlas.log.jsonl"

_logger_initialized = False


class JsonLFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
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
        return logger  # Already configured

    logger.setLevel(logging.INFO)

    # If running in a test environment, return a logger with only a NullHandler
    # to prevent file I/O side effects during test collection.
    if os.environ.get("ATLAS_TESTING"):
        logger.addHandler(logging.NullHandler())
        return logger

    # Proceed with file and stream handlers for normal execution
    global _logger_initialized
    if not _logger_initialized:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        _logger_initialized = True

    fh = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    fh.setFormatter(JsonLFormatter())
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(sh)

    return logger


def add_handler(handler: Handler, name: str = "atlas") -> None:
    """Add a new handler to the specified logger."""
    logger = logging.getLogger(name)
    logger.addHandler(handler)
