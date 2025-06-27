from typing import Any, Dict, Optional

from plugins.base import PluginBase, PluginMetadata
from PySide6.QtWidgets import QWidget


class TestPlugin(PluginBase):
    """Test plugin implementation."""

    def _get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="TestPlugin",
            description="A test plugin",
            version="1.0.0",
            author="Test Author",
            dependencies=[],
            min_app_version="1.0.0",
        )

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings."""
        return {}

    def activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        """Activate the plugin."""
        self.active = True

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        self.active = False

    def on_activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        """Called when plugin is activated."""
        pass

    def on_deactivate(self) -> None:
        """Called when plugin is deactivated."""
        pass

    def get_widget(self, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """Get the main widget for UI integration."""
        return None

    def get_settings(self) -> Dict[str, Any]:
        """Get current plugin settings."""
        return self.settings

    def set_settings(self, settings: Dict[str, Any]) -> None:
        """Set plugin settings."""
        self.settings = settings

    def on_settings_changed(self, settings: Dict[str, Any]) -> None:
        """Called when settings are changed."""
        pass

    def settings_widget(self, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """Get settings widget for editing."""
        return None

    def info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "author": self.metadata.author,
            "description": self.metadata.description,
            "active": self.active,
        }
