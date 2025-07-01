"""Plugin Interface definition for Atlas."""

import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, Signal


class PluginInterface(QObject):
    """Base interface for all plugins in Atlas."""

    status_changed = Signal(str)

    def __init__(self, plugin_id: str, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.plugin_id = plugin_id
        self.is_active = False
        self.metadata = {
            "name": "Unnamed Plugin",
            "version": "0.1.0",
            "description": "No description provided.",
            "author": "Unknown",
        }
        self.logger.info(f"Plugin interface initialized for {plugin_id}")

    def initialize(self) -> bool:
        """Initialize the plugin.

        Returns:
            bool: True if initialization successful, False otherwise.
        """
        self.logger.debug(f"Initializing plugin: {self.plugin_id}")
        try:
            # Perform plugin-specific initialization
            success = self.on_initialize()
            if success:
                self.is_active = True
                self.status_changed.emit("Initialized")
                self.logger.info(f"Plugin {self.plugin_id} initialized successfully")
            else:
                self.logger.error(f"Plugin {self.plugin_id} initialization failed")
            return success
        except Exception as e:
            self.logger.error(f"Error initializing plugin {self.plugin_id}: {str(e)}")
            return False

    def shutdown(self) -> None:
        """Shut down the plugin."""
        self.logger.debug(f"Shutting down plugin: {self.plugin_id}")
        try:
            self.on_shutdown()
            self.is_active = False
            self.status_changed.emit("Shut down")
            self.logger.info(f"Plugin {self.plugin_id} shut down")
        except Exception as e:
            self.logger.error(f"Error shutting down plugin {self.plugin_id}: {str(e)}")

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the plugin.

        Returns:
            Dict[str, Any]: Dictionary containing plugin metadata.
        """
        return self.metadata

    def on_initialize(self) -> bool:
        """Plugin-specific initialization logic.

        Returns:
            bool: True if initialization successful, False otherwise.
        """
        # To be implemented by subclasses
        return True

    def on_shutdown(self) -> None:
        """Plugin-specific shutdown logic."""
        # To be implemented by subclasses
        pass

    def get_ui_component(self) -> Optional[Any]:
        """Get the UI component for this plugin, if any.

        Returns:
            Optional[Any]: UI component or None if not applicable.
        """
        # To be implemented by subclasses if they provide UI
        return None

    def handle_event(self, event_type: str, data: Any) -> None:
        """Handle events passed to the plugin.

        Args:
            event_type (str): Type of event.
            data (Any): Event data.
        """
        # To be implemented by subclasses if they handle events
        self.logger.debug(f"Plugin {self.plugin_id} received event {event_type}")
