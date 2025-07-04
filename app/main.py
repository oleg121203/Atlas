"""Main entry point for the Atlas application."""

import logging
import os
import sys

from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)


def run_application():
    """Run the Atlas application with error handling."""
    logger.info("Starting Atlas application...")

    # Ensure the application is running from the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Initialize QApplication as early as possible
    QApplication(sys.argv)
    logger.info("QApplication initialized at application start")

    from core.application import AtlasApplication

    app = AtlasApplication()
    app.initialize_ui()
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    run_application()
