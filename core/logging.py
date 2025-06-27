"""
Logging Module for Atlas

This module provides a centralized logging utility for the Atlas application.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name):
    """
    Get a logger instance with the specified name.

    Args:
        name (str): Name of the logger, usually the module name.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:  # Only configure if not already configured
        logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "logs"
        )
        os.makedirs(logs_dir, exist_ok=True)

        # Configure file handler with rotation
        log_file = os.path.join(logs_dir, "atlas.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5
        )  # 10MB per file, 5 backups
        file_handler.setLevel(logging.INFO)

        # Configure stream handler for console output
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)

        # Define log format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger


def setup_logging(log_file: str = "atlas.log", log_level: int = logging.INFO) -> None:
    """
    Set up logging configuration for the Atlas application.

    Args:
        log_file (str): Path to the log file.
        log_level (int): Logging level (default: INFO).
    """
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear any existing handlers
    logger.handlers = []

    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1024 * 1024 * 5, backupCount=3
    )
    file_handler.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logging initialized for Atlas")


# Configure root logger
root_logger = get_logger("Atlas")
