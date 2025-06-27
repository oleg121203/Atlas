"""
Centralized logging system for the Atlas application.

This module provides a unified logging mechanism with configurable log levels,
multiple output handlers (console, file), and performance monitoring capabilities.
"""

import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from core.config import get_config

# Default log directory and file
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
DEFAULT_LOG_FILE = os.path.join(LOG_DIR, "atlas.log")

# Sensitive data patterns to redact
SENSITIVE_PATTERNS = [
    re.compile(
        r"(password|secret|key|token|api_key|access_token)=[^&\s]+", re.IGNORECASE
    ),
    re.compile(r"\b\d{16}\b"),  # Credit card numbers
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
]


def redact_sensitive_data(message: str) -> str:
    """
    Redact sensitive information from log messages.

    Args:
        message (str): The original log message

    Returns:
        str: The message with sensitive data redacted
    """
    redacted = message
    for pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


class RedactingFormatter(logging.Formatter):
    """Formatter that redacts sensitive information from log messages."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record and redact sensitive data."""
        original_message = super().format(record)
        return redact_sensitive_data(original_message)


# Log level mapping
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Global logger instance
_logger: Optional[logging.Logger] = None


def setup_logging() -> logging.Logger:
    """
    Configure and return the global logger instance for Atlas.

    Returns:
        logging.Logger: Configured logger instance
    """
    global _logger
    if _logger is not None:
        return _logger

    config = get_config()
    log_level_str = config.get("log_level", "INFO").upper()
    log_level = LOG_LEVELS.get(log_level_str, logging.INFO)

    # Create log directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create formatters
    console_formatter = RedactingFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_formatter = RedactingFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        DEFAULT_LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Log initialization
    root_logger.info("Logging system initialized with level: %s", log_level_str)

    return root_logger


def get_logger(name: str = "Atlas") -> logging.Logger:
    """
    Get a logger instance with the specified name.
    If no name is provided, returns the root Atlas logger.

    Args:
        name (str): Name of the logger instance

    Returns:
        logging.Logger: Logger instance
    """
    global _logger
    if _logger is None:
        return setup_logging().getChild(name) if name != "Atlas" else setup_logging()
    return _logger.getChild(name) if name != "Atlas" else _logger


def set_log_level(level: str) -> bool:
    """
    Dynamically update the log level for all handlers.

    Args:
        level (str): New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        bool: True if level was updated successfully
    """
    global _logger
    if _logger is None:
        return False

    level = level.upper()
    if level not in LOG_LEVELS:
        return False

    log_level = LOG_LEVELS[level]
    _logger.setLevel(log_level)
    for handler in _logger.handlers:
        handler.setLevel(log_level)

    _logger.info("Log level updated to: %s", level)
    return True


def log_performance(
    component: str, operation: str, duration_ms: float, details: Optional[str] = None
) -> None:
    """
    Log performance metrics for operations.

    Args:
        component (str): Name of component being measured
        operation (str): Operation being measured
        duration_ms (float): Duration in milliseconds
        details (str, optional): Additional details about the operation
    """
    logger = get_logger("Performance")
    msg = f"{component} - {operation}: {duration_ms:.2f}ms"
    if details:
        msg += f" - {details}"
    if duration_ms > 100:  # Warn on slow operations (>100ms)
        logger.warning(msg)
    else:
        logger.debug(msg)
