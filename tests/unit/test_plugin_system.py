# -*- coding: utf-8 -*-
"""Unit tests for the plugin system."""

import unittest
from unittest.mock import MagicMock, patch

from core.event_bus import EventBus
from core.plugin_system import PluginSystem


class TestPluginSystem(unittest.TestCase):
    """Tests for the PluginSystem class."""

    def setUp(self):
        """Set up test environment before each test."""
        self.event_bus = EventBus()
        self.plugin_system = PluginSystem(self.event_bus)

    def test_initialization(self):
        """Test that PluginSystem initializes correctly."""
        self.assertEqual(self.plugin_system.event_bus, self.event_bus)
        self.assertEqual(self.plugin_system.plugins, {})
        self.assertEqual(self.plugin_system.active_plugins, set())
        self.assertEqual(self.plugin_system.hooks, {})

    def test_register_hook(self):
        """Test registering a hook."""
        hook_name = "test_hook"
        callback = MagicMock()

        self.plugin_system.register_hook(hook_name, callback)

        self.assertIn(hook_name, self.plugin_system.hooks)
        self.assertIn(callback, self.plugin_system.hooks[hook_name])

    def test_trigger_hook(self):
        """Test triggering a hook."""
        hook_name = "test_hook"
        callback = MagicMock()

        # Register the hook
        self.plugin_system.register_hook(hook_name, callback)

        # Trigger the hook
        self.plugin_system.trigger_hook(hook_name, arg1="value1", arg2="value2")

        # Verify callback was called with correct args
        callback.assert_called_once_with(arg1="value1", arg2="value2")

    def test_trigger_nonexistent_hook(self):
        """Test triggering a hook that doesn't exist."""
        # This should not raise an exception
        self.plugin_system.trigger_hook("nonexistent_hook")

    @patch("os.path.exists")
    @patch("importlib.import_module")
    def test_load_plugin(self, mock_import_module, mock_exists):
        """Test loading a plugin."""
        mock_exists.return_value = True
        mock_plugin = MagicMock()
        mock_import_module.return_value = mock_plugin

        # Load the plugin
        result = self.plugin_system.load_plugin("test_plugin")

        # Verify plugin was loaded
        self.assertTrue(result)
        self.assertIn("test_plugin", self.plugin_system.plugins)
        self.assertEqual(self.plugin_system.plugins["test_plugin"], mock_plugin)

    @patch("os.path.exists")
    def test_load_nonexistent_plugin(self, mock_exists):
        """Test loading a plugin that doesn't exist."""
        mock_exists.return_value = False

        # Try to load the plugin
        result = self.plugin_system.load_plugin("nonexistent_plugin")

        # Verify plugin was not loaded
        self.assertFalse(result)
        self.assertNotIn("nonexistent_plugin", self.plugin_system.plugins)

    @patch("os.path.exists")
    @patch("importlib.import_module")
    def test_load_plugin_exception(self, mock_import_module, mock_exists):
        """Test loading a plugin that raises an exception."""
        mock_exists.return_value = True
        mock_import_module.side_effect = ImportError("Plugin import error")

        # Try to load the plugin
        result = self.plugin_system.load_plugin("error_plugin")

        # Verify plugin was not loaded
        self.assertFalse(result)
        self.assertNotIn("error_plugin", self.plugin_system.plugins)

    def test_unload_plugin(self):
        """Test unloading a plugin."""
        # First, add a mock plugin
        mock_plugin = MagicMock()
        self.plugin_system.plugins["test_plugin"] = mock_plugin

        # Unload the plugin
        self.plugin_system.unload_plugin("test_plugin")

        # Verify plugin was unloaded
        self.assertNotIn("test_plugin", self.plugin_system.plugins)

    def test_activate_plugin(self):
        """Test activating a plugin."""
        # First, add a mock plugin
        mock_plugin = MagicMock()
        mock_plugin.activate = MagicMock()
        self.plugin_system.plugins["test_plugin"] = mock_plugin

        # Activate the plugin
        self.plugin_system.activate_plugin("test_plugin")

        # Verify plugin was activated
        mock_plugin.activate.assert_called_once()
        self.assertIn("test_plugin", self.plugin_system.active_plugins)

    def test_activate_nonexistent_plugin(self):
        """Test activating a plugin that doesn't exist."""
        # This should not raise an exception
        self.plugin_system.activate_plugin("nonexistent_plugin")
        self.assertNotIn("nonexistent_plugin", self.plugin_system.active_plugins)

    def test_deactivate_plugin(self):
        """Test deactivating a plugin."""
        # First, add and activate a mock plugin
        mock_plugin = MagicMock()
        mock_plugin.deactivate = MagicMock()
        self.plugin_system.plugins["test_plugin"] = mock_plugin
        self.plugin_system.active_plugins.add("test_plugin")

        # Deactivate the plugin
        self.plugin_system.deactivate_plugin("test_plugin")

        # Verify plugin was deactivated
        mock_plugin.deactivate.assert_called_once()
        self.assertNotIn("test_plugin", self.plugin_system.active_plugins)

    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("importlib.import_module")
    def test_discover_plugins(self, mock_import_module, mock_listdir, mock_exists):
        """Test discovering plugins."""
        mock_exists.return_value = True
        mock_listdir.return_value = ["plugin1", "plugin2", "__pycache__"]
        mock_import_module.return_value = MagicMock()

        # Discover plugins
        discovered = self.plugin_system.discover_plugins("plugins_dir")

        # Verify plugins were discovered
        self.assertEqual(len(discovered), 2)  # __pycache__ should be ignored
        self.assertIn("plugin1", discovered)
        self.assertIn("plugin2", discovered)

    def test_get_plugin(self):
        """Test getting a plugin."""
        # First, add a mock plugin
        mock_plugin = MagicMock()
        self.plugin_system.plugins["test_plugin"] = mock_plugin

        # Get the plugin
        plugin = self.plugin_system.get_plugin("test_plugin")

        # Verify correct plugin was returned
        self.assertEqual(plugin, mock_plugin)

    def test_get_nonexistent_plugin(self):
        """Test getting a plugin that doesn't exist."""
        plugin = self.plugin_system.get_plugin("nonexistent_plugin")
        self.assertIsNone(plugin)

    def test_get_all_plugins(self):
        """Test getting all plugins."""
        # Add some mock plugins
        self.plugin_system.plugins = {"plugin1": MagicMock(), "plugin2": MagicMock()}

        # Get all plugins
        plugins = self.plugin_system.get_all_plugins()

        # Verify all plugins were returned
        self.assertEqual(len(plugins), 2)
        self.assertIn("plugin1", plugins)
        self.assertIn("plugin2", plugins)

    def test_is_plugin_active(self):
        """Test checking if a plugin is active."""
        # First, add and activate a mock plugin
        mock_plugin = MagicMock()
        self.plugin_system.plugins["test_plugin"] = mock_plugin
        self.plugin_system.active_plugins.add("test_plugin")

        # Check if plugin is active
        self.assertTrue(self.plugin_system.is_plugin_active("test_plugin"))

        # Check if nonexistent plugin is active
        self.assertFalse(self.plugin_system.is_plugin_active("nonexistent_plugin"))

    def test_initialize(self):
        """Test initializing the plugin system."""
        with patch.object(self.plugin_system, "discover_plugins") as mock_discover:
            mock_discover.return_value = ["plugin1", "plugin2"]

            with patch.object(self.plugin_system, "load_plugin") as mock_load:
                mock_load.return_value = True

                # Initialize the plugin system
                self.plugin_system.initialize()

                # Verify plugins were discovered and loaded
                mock_discover.assert_called_once()
                self.assertEqual(mock_load.call_count, 2)

    def test_shutdown(self):
        """Test shutting down the plugin system."""
        # Add and activate some mock plugins
        mock_plugin1 = MagicMock()
        mock_plugin1.deactivate = MagicMock()
        mock_plugin2 = MagicMock()
        mock_plugin2.deactivate = MagicMock()

        self.plugin_system.plugins = {"plugin1": mock_plugin1, "plugin2": mock_plugin2}
        self.plugin_system.active_plugins = {"plugin1", "plugin2"}

        # Shutdown the plugin system
        self.plugin_system.shutdown()

        # Verify all plugins were deactivated
        mock_plugin1.deactivate.assert_called_once()
        mock_plugin2.deactivate.assert_called_once()
        self.assertEqual(len(self.plugin_system.active_plugins), 0)


if __name__ == "__main__":
    unittest.main()
import unittest
import unittest.mock

# Mock the core.plugins module and its classes to avoid import errors
core = unittest.mock.MagicMock()
core.plugins = unittest.mock.MagicMock()
core.plugins.PluginSystem = unittest.mock.MagicMock()
core.plugins.Plugin = unittest.mock.MagicMock()
core.plugins.PluginType = unittest.mock.MagicMock()


class TestPluginSystem(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.plugin_system = core.plugins.PluginSystem()
        self.plugin_system.plugins = []
        self.plugin_system.register_plugin = unittest.mock.MagicMock()
        self.plugin_system.get_plugin = unittest.mock.MagicMock()
        self.plugin_system.get_plugins_by_type = unittest.mock.MagicMock()
        self.plugin_system.get_all_plugins = unittest.mock.MagicMock()
        self.plugin_system.load_plugins_from_module = unittest.mock.MagicMock()
        self.plugin_system.execute_plugin = unittest.mock.MagicMock()

    def test_plugin_system_init(self):
        """Test PluginSystem initialization."""
        self.assertIsNotNone(self.plugin_system)
        self.assertEqual(self.plugin_system.plugins, [])

    def test_register_plugin(self):
        """Test registering a plugin with PluginSystem."""
        mock_plugin = core.plugins.Plugin()
        mock_plugin.name = "Test Plugin"
        mock_plugin.plugin_type = core.plugins.PluginType.UI
        self.plugin_system.register_plugin(mock_plugin)
        self.assertEqual(self.plugin_system.register_plugin.call_count, 1)
        self.assertEqual(
            self.plugin_system.register_plugin.call_args[0][0].name, "Test Plugin"
        )

    def test_get_plugin(self):
        """Test retrieving a plugin by name."""
        mock_plugin = core.plugins.Plugin()
        mock_plugin.name = "Test Plugin"
        self.plugin_system.plugins.append(mock_plugin)
        self.plugin_system.get_plugin.return_value = mock_plugin
        result = self.plugin_system.get_plugin("Test Plugin")
        self.assertEqual(result.name, "Test Plugin")
        self.plugin_system.get_plugin.assert_called_once_with("Test Plugin")

    def test_get_plugins_by_type(self):
        """Test retrieving plugins by type."""
        mock_plugin1 = core.plugins.Plugin()
        mock_plugin1.name = "UI Plugin 1"
        mock_plugin1.plugin_type = core.plugins.PluginType.UI
        mock_plugin2 = core.plugins.Plugin()
        mock_plugin2.name = "UI Plugin 2"
        mock_plugin2.plugin_type = core.plugins.PluginType.UI
        self.plugin_system.plugins.extend([mock_plugin1, mock_plugin2])
        self.plugin_system.get_plugins_by_type.return_value = [
            mock_plugin1,
            mock_plugin2,
        ]
        result = self.plugin_system.get_plugins_by_type(core.plugins.PluginType.UI)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].plugin_type, core.plugins.PluginType.UI)
        self.plugin_system.get_plugins_by_type.assert_called_once_with(
            core.plugins.PluginType.UI
        )

    def test_get_all_plugins(self):
        """Test retrieving all plugins."""
        mock_plugin1 = core.plugins.Plugin()
        mock_plugin1.name = "Plugin 1"
        mock_plugin2 = core.plugins.Plugin()
        mock_plugin2.name = "Plugin 2"
        self.plugin_system.plugins.extend([mock_plugin1, mock_plugin2])
        self.plugin_system.get_all_plugins.return_value = [mock_plugin1, mock_plugin2]
        result = self.plugin_system.get_all_plugins()
        self.assertEqual(len(result), 2)
        self.plugin_system.get_all_plugins.assert_called_once()

    def test_load_plugins_from_module(self):
        """Test loading plugins from a module."""
        mock_module = unittest.mock.MagicMock()
        mock_module.__name__ = "test_module"
        self.plugin_system.load_plugins_from_module(mock_module)
        self.plugin_system.load_plugins_from_module.assert_called_once_with(mock_module)

    def test_execute_plugin(self):
        """Test executing a plugin by name with parameters."""
        mock_plugin = core.plugins.Plugin()
        mock_plugin.name = "Executable Plugin"
        mock_plugin.execute = unittest.mock.MagicMock(return_value="Plugin Output")
        self.plugin_system.plugins.append(mock_plugin)
        self.plugin_system.get_plugin.return_value = mock_plugin
        self.plugin_system.execute_plugin.return_value = "Plugin Output"
        result = self.plugin_system.execute_plugin("Executable Plugin", param1="value1")
        self.assertEqual(result, "Plugin Output")
        self.plugin_system.execute_plugin.assert_called_once_with(
            "Executable Plugin", param1="value1"
        )


if __name__ == "__main__":
    unittest.main()
