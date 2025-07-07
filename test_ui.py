#!/usr/bin/env python3
"""
Simple test script for the Atlas main window UI.
"""

import logging
import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import AtlasMainWindow


def test_ui():
    """Test the main window UI functionality."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Create QApplication
    app = QApplication(sys.argv)

    try:
        # Create main window
        logger.info("Creating main window...")
        main_window = AtlasMainWindow(app=app)

        # Show the window
        logger.info("Showing main window...")
        main_window.show()

        # Test basic functionality
        logger.info("Testing module switching...")
        main_window.show_module("Chat")
        main_window.show_module("Plugins")

        logger.info("UI test completed successfully!")
        logger.info("Window is now displayed. Close it to exit.")

        # Run the event loop
        return app.exec()

    except Exception as e:
        logger.error(f"Error during UI test: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(test_ui())
