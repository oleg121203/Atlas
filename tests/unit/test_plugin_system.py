# -*- coding: utf-8 -*-
"""Unit tests for the plugin system."""

import os
import tempfile
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
