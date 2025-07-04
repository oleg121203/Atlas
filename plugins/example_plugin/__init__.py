"""Example plugin for Atlas.

This plugin demonstrates the basic structure and functionality of an Atlas plugin.
"""

import logging

from plugins import PluginBase

logger = logging.getLogger(__name__)


class ExamplePlugin(PluginBase):
    """Example plugin implementation."""

    def __init__(self):
        """Initialize the example plugin."""
        super().__init__(name="Example Plugin", version="1.0.0")
        self.description = (
            "A simple example plugin demonstrating Atlas plugin functionality"
        )
        logger.info(f"Example plugin initialized: {self.name} v{self.version}")

    def initialize(self) -> bool:
        """Initialize plugin resources."""
        logger.info(f"Initializing {self.name}")
        # Plugin initialization code would go here
        return True

    def start(self) -> bool:
        """Start the plugin functionality."""
        logger.info(f"Starting {self.name}")
        self.enabled = True
        # Plugin startup code would go here
        return True

    def stop(self) -> bool:
        """Stop the plugin functionality."""
        logger.info(f"Stopping {self.name}")
        self.enabled = False
        # Plugin shutdown code would go here
        return True

    def get_widget(self):
        """Get the plugin's UI widget.

        In a real plugin, this would return a PySide6 QWidget.
        """
        try:
            # This is just a placeholder - in a real plugin, we would import and return an actual widget
            from PySide6.QtWidgets import QLabel

            return QLabel(f"{self.name} v{self.version}")
        except ImportError:
            logger.warning("PySide6 not available, can't create widget")
            return None


# Create plugin instance for the plugin system to discover
plugin = ExamplePlugin()
