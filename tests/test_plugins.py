import pytest
from unittest.mock import MagicMock, patch
from plugins.base import PluginMetadata, PluginBase
from plugins.plugin_registry import PluginRegistry
from typing import Dict, Any, Optional
from PySide6.QtWidgets import QWidget
import logging

# Test plugin implementation
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
            min_app_version="1.0.0"
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
            'name': self.metadata.name,
            'version': self.metadata.version,
            'author': self.metadata.author,
            'description': self.metadata.description,
            'active': self.active
        }

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestPluginBase:
    """Test cases for PluginBase class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.plugin = TestPlugin()

    def test_plugin_metadata(self):
        """Test plugin metadata."""
        assert self.plugin.metadata.name == "TestPlugin"
        assert self.plugin.metadata.version == "1.0.0"
        assert self.plugin.metadata.author == "Test Author"

    def test_plugin_activation(self):
        """Test plugin activation."""
        app_context = {"test": "context"}
        self.plugin.activate(app_context)
        assert self.plugin.active is True

    def test_plugin_deactivation(self):
        """Test plugin deactivation."""
        self.plugin.activate()
        self.plugin.deactivate()
        assert self.plugin.active is False

class TestPluginRegistry:
    """Test cases for PluginRegistry class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = PluginRegistry()

    def test_plugin_registration(self):
        """Test plugin registration."""
        test_plugin = TestPlugin()
        self.registry.plugins[test_plugin.metadata.name] = test_plugin
        assert test_plugin.metadata.name in self.registry.plugins
        assert self.registry.plugins[test_plugin.metadata.name] == test_plugin

    def test_plugin_activation(self):
        """Test plugin activation."""
        test_plugin = TestPlugin()
        self.registry.plugins[test_plugin.metadata.name] = test_plugin
        assert self.registry.activate_plugin(test_plugin.metadata.name) is True
        assert test_plugin.active is True

    def test_plugin_deactivation(self):
        """Test plugin deactivation."""
        test_plugin = TestPlugin()
        self.registry.plugins[test_plugin.metadata.name] = test_plugin
        assert self.registry.activate_plugin(test_plugin.metadata.name) is True
        assert self.registry.deactivate_plugin(test_plugin.metadata.name) is True
        assert test_plugin.active is False

    def test_plugin_info(self):
        """Test plugin information retrieval."""
        test_plugin = TestPlugin()
        self.registry.plugins[test_plugin.metadata.name] = test_plugin
        info = self.registry.get_plugin_info(test_plugin.metadata.name)
        assert info["name"] == test_plugin.metadata.name
        assert info["version"] == test_plugin.metadata.version
        assert info["author"] == test_plugin.metadata.author
        assert info["description"] == test_plugin.metadata.description
        assert info["active"] == test_plugin.active
