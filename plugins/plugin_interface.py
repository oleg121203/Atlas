"""Plugin Interface definition for Atlas."""

import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, Signal

# Імпортуємо PluginBase для сумісності
try:
    from core.plugin_system import PluginBase
except ImportError:
    # Fallback якщо PluginBase недоступний
    class PluginBase:
        def __init__(self, name: str, version: str):
            self.name = name
            self.version = version
            self.is_active = False

        def initialize(self) -> None:
            self.is_active = True

        def shutdown(self) -> None:
            self.is_active = False

        def get_metadata(self) -> Dict[str, Any]:
            return {
                "name": self.name,
                "version": self.version,
                "status": "active" if self.is_active else "inactive",
            }


class PluginInterface(PluginBase, QObject):
    """Base interface for all plugins in Atlas."""

    status_changed = Signal(str)

    def __init__(self, name: str, version: str, parent: Optional[QObject] = None):
        PluginBase.__init__(self, name, version)
        QObject.__init__(self, parent)
        self.logger = logging.getLogger(__name__)
        self.plugin_id = name  # Використовуємо name як plugin_id для сумісності
        self.metadata = {
            "name": "Unnamed Plugin",
            "version": version,
            "description": "No description provided.",
            "author": "Unknown",
        }
        self.logger.info(f"Plugin interface initialized for {name}")

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
