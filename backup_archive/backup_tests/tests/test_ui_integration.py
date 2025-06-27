import logging

import pytest
from plugins.base import PluginBase, PluginMetadata
from plugins.plugin_registry import PluginRegistry
from PySide6.QtWidgets import QApplication, QWidget

from ui.plugins_module import PluginsModule

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def qapp():
    """Qt application fixture."""
    return QApplication([])


class TestPluginUIIntegration:
    """Test cases for plugin UI integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = PluginRegistry()
        self.plugins_module = PluginsModule()
        self.plugins_module.set_plugin_manager(self.registry)

        # Create test plugin
        metadata = PluginMetadata(
            name="TestPlugin",
            description="A test plugin",
            version="1.0.0",
            author="Test Author",
            dependencies=[],
            min_app_version="1.0.0",
        )
        self.test_plugin = PluginBase()
        self.test_plugin.metadata = metadata
        self.registry.plugins["TestPlugin"] = self.test_plugin

    def test_plugin_ui_update(self, qapp):
        """Test UI updates when plugins change."""
        # Initial state
        assert self.plugins_module.list.count() == 0

        # Add plugin
        self.registry.activate_plugin("TestPlugin")
        self.plugins_module.update_plugins()
        assert self.plugins_module.list.count() == 1

        # Check plugin status
        item_text = self.plugins_module.list.item(0).text()
        assert "TestPlugin" in item_text
        assert "(active)" in item_text

    def test_plugin_activation_ui(self, qapp):
        """Test plugin activation through UI."""
        # Add plugin
        self.registry.activate_plugin("TestPlugin")
        self.plugins_module.update_plugins()

        # Deactivate through UI
        self.plugins_module.list.setCurrentRow(0)
        self.plugins_module.deactivate_plugin()
        assert not self.test_plugin.active

        # Reactivate through UI
        self.plugins_module.activate_plugin()
        assert self.test_plugin.active

    def test_plugin_settings_ui(self, qapp):
        """Test plugin settings UI integration."""
        # Add plugin with settings
        metadata = PluginMetadata(
            name="TestSettingsPlugin",
            description="A test plugin with settings",
            version="1.0.0",
            author="Test Author",
            dependencies=[],
            min_app_version="1.0.0",
        )
        settings_plugin = PluginBase()
        settings_plugin.metadata = metadata
        settings_plugin.settings = {"test_setting": "value"}
        self.registry.plugins["TestSettingsPlugin"] = settings_plugin

        # Activate plugin
        self.registry.activate_plugin("TestSettingsPlugin")
        self.plugins_module.update_plugins()

        # Check settings widget
        self.plugins_module.list.setCurrentRow(0)
        settings_widget = self.plugins_module.plugins_frame.findChild(
            QWidget, "settings_widget"
        )
        assert settings_widget is not None

    def test_plugin_tools_ui(self, qapp):
        """Test plugin tools UI integration."""
        # Add plugin with tool
        metadata = PluginMetadata(
            name="TestToolPlugin",
            description="A test plugin with tools",
            version="1.0.0",
            author="Test Author",
            dependencies=[],
            min_app_version="1.0.0",
        )
        tool_plugin = PluginBase()
        tool_plugin.metadata = metadata
        tool_plugin.settings = {"test_tool": "enabled"}
        self.registry.plugins["TestToolPlugin"] = tool_plugin

        # Activate plugin
        self.registry.activate_plugin("TestToolPlugin")
        self.plugins_module.update_plugins()

        # Check tools widget
        self.plugins_module.list.setCurrentRow(0)
        tools_widget = self.plugins_module.plugins_frame.findChild(
            QWidget, "tools_widget"
        )
        assert tools_widget is not None

    def test_plugin_reload_ui(self, qapp):
        """Test plugin reload through UI."""
        # Add plugin
        self.registry.activate_plugin("TestPlugin")
        self.plugins_module.update_plugins()

        # Reload through UI
        self.plugins_module.reload_plugins()
        assert self.test_plugin.active  # Should remain active after reload

    def test_plugin_search_ui(self, qapp):
        """Test plugin search functionality."""
        # Add multiple plugins
        for i in range(3):
            metadata = PluginMetadata(
                name=f"TestPlugin{i}",
                description=f"A test plugin {i}",
                version="1.0.0",
                author="Test Author",
                dependencies=[],
                min_app_version="1.0.0",
            )
            plugin = PluginBase()
            plugin.metadata = metadata
            self.registry.plugins[f"TestPlugin{i}"] = plugin
            self.registry.activate_plugin(f"TestPlugin{i}")

        self.plugins_module.update_plugins()

        # Search for plugins
        results = self.plugins_module.search("TestPlugin1")
        assert len(results) == 1
        assert results[0]["label"] == "TestPlugin1"

    def test_plugin_selection_ui(self, qapp):
        """Test plugin selection functionality."""
        # Add multiple plugins
        for i in range(3):
            metadata = PluginMetadata(
                name=f"TestPlugin{i}",
                description=f"A test plugin {i}",
                version="1.0.0",
                author="Test Author",
                dependencies=[],
                min_app_version="1.0.0",
            )
            plugin = PluginBase()
            plugin.metadata = metadata
            self.registry.plugins[f"TestPlugin{i}"] = plugin
            self.registry.activate_plugin(f"TestPlugin{i}")

        self.plugins_module.update_plugins()

        # Select plugin
        self.plugins_module.select_by_key("TestPlugin1")
        assert self.plugins_module.list.currentRow() == 1

    def test_plugin_error_handling_ui(self, qapp):
        """Test error handling in UI."""
        # Create plugin that raises error
        metadata = PluginMetadata(
            name="ErrorPlugin",
            description="A plugin that raises error",
            version="1.0.0",
            author="Test Author",
            dependencies=[],
            min_app_version="1.0.0",
        )
        error_plugin = PluginBase()
        error_plugin.metadata = metadata

        def raise_error():
            raise Exception("Test error")

        error_plugin.activate = raise_error
        self.registry.plugins["ErrorPlugin"] = error_plugin

        # Try to activate plugin
        self.registry.activate_plugin("ErrorPlugin")
        self.plugins_module.update_plugins()

        # Check error handling
        assert not error_plugin.active
        assert self.plugins_module.list.count() == 0  # Should not show errored plugin
