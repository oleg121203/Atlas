"""Main entry point for the Sample Plugin in Atlas."""

import logging
from typing import Any, Optional

from PySide6.QtCore import QObject

from plugins.plugin_interface import PluginInterface


class AtlasPlugin(PluginInterface):
    """Sample plugin implementation for Atlas."""

    def __init__(self, plugin_id: str, parent: Optional[QObject] = None):
        super().__init__(plugin_id, parent)
        self.logger = logging.getLogger(__name__)
        self.metadata = {
            "name": "Sample Plugin",
            "version": "1.0.0",
            "description": "A sample plugin demonstrating Atlas plugin functionality.",
            "author": "Atlas Team",
        }
        self.logger.info(f"Sample Plugin {plugin_id} instantiated")

    def on_initialize(self) -> bool:
        """Initialize the sample plugin.

        Returns:
            bool: True if initialization successful, False otherwise.
        """
        self.logger.info("Sample Plugin initializing")
        # Perform any initialization logic here
        return True

    def on_shutdown(self) -> None:
        """Shut down the sample plugin."""
        self.logger.info("Sample Plugin shutting down")
        # Perform any cleanup logic here

    def handle_event(self, event_type: str, data: Any) -> None:
        """Handle events passed to the plugin.

        Args:
            event_type (str): Type of event.
            data (Any): Event data.
        """
        self.logger.info(f"Sample Plugin received event: {event_type}")
        # Handle different event types as needed
        if event_type == "sample_event":
            self.logger.info(f"Sample Plugin processing sample_event with data: {data}")
