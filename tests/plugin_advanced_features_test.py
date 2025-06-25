import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Ensure the parent directory is in the path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.plugin_manager import PluginManager

class PluginAdvancedFeaturesTest(unittest.TestCase):
    def setUp(self):
        self.mock_agent_manager = MagicMock()
        self.mock_llm_manager = MagicMock()
        self.plugin_manager = PluginManager(agent_manager=self.mock_agent_manager, plugin_dir="test_plugins")
        self.plugin_manager.logger = MagicMock()

    def test_plugin_dependency_management(self):
        """Test that plugin dependencies are checked and resolved during discovery."""
        # Mock plugin metadata with dependencies
        plugin_metadata = {
            "name": "TestPluginWithDeps",
            "version": "1.0.0",
            "dependencies": {"OtherPlugin": ">=0.9.0"}
        }
        self.plugin_manager.plugins = {
            "OtherPlugin": {"metadata": {"name": "OtherPlugin", "version": "1.0.0"}, "enabled": True}
        }

        with patch.object(self.plugin_manager, '_load_plugin_metadata', return_value=plugin_metadata):
            with patch.object(self.plugin_manager, '_check_dependency', return_value=True):
                result = self.plugin_manager._check_dependencies(plugin_metadata)
                self.assertTrue(result, "Dependencies should be resolved successfully")

    def test_plugin_version_control(self):
        """Test that plugin versions are correctly compared and managed."""
        self.plugin_manager.plugins = {
            "TestPlugin": {"metadata": {"name": "TestPlugin", "version": "1.0.0"}, "enabled": True}
        }

        # Test version compatibility
        result = self.plugin_manager._compare_version("1.0.0", ">=0.9.0")
        self.assertTrue(result, "Version 1.0.0 should be >= 0.9.0")

        result = self.plugin_manager._compare_version("0.8.0", ">=0.9.0")
        self.assertFalse(result, "Version 0.8.0 should not be >= 0.9.0")

    def test_plugin_conflict_resolution(self):
        """Test conflict resolution when plugins have incompatible dependencies."""
        self.plugin_manager.plugins = {
            "PluginA": {"metadata": {"name": "PluginA", "version": "1.0.0", "dependencies": {"SharedDep": ">=2.0.0"}}, "enabled": True},
            "PluginB": {"metadata": {"name": "PluginB", "version": "1.0.0", "dependencies": {"SharedDep": "<=1.0.0"}}, "enabled": True},
            "SharedDep": {"metadata": {"name": "SharedDep", "version": "1.0.0"}, "enabled": True}
        }

        conflict_report = self.plugin_manager._detect_conflicts()
        self.assertIn("SharedDep", conflict_report, "Conflict should be detected for SharedDep")
        self.assertEqual(len(conflict_report["SharedDep"]), 1, "One conflict should be reported for SharedDep")
        self.assertEqual(conflict_report["SharedDep"][0]["plugin"], "PluginA", "Conflict should be reported for PluginA")

    def test_enable_plugin_with_dependencies(self):
        """Test enabling a plugin with dependencies checks and resolves them."""
        plugin_name = "TestPluginWithDeps"
        self.plugin_manager.plugins = {
            plugin_name: {
                "metadata": {"name": plugin_name, "version": "1.0.0", "dependencies": {"OtherPlugin": ">=0.9.0"}},
                "enabled": False,
                "modules": []
            },
            "OtherPlugin": {"metadata": {"name": "OtherPlugin", "version": "1.0.0"}, "enabled": True}
        }

        with patch.object(self.plugin_manager, '_check_dependencies', return_value=True):
            result = self.plugin_manager.enable_plugin(plugin_name)
            self.assertTrue(result, "Plugin should be enabled when dependencies are met")
            self.assertTrue(self.plugin_manager.plugins[plugin_name]["enabled"], "Plugin status should be updated to enabled")

    def test_disable_plugin_with_dependents(self):
        """Test disabling a plugin checks for dependent plugins and prevents disabling if dependents are active."""
        plugin_name = "BasePlugin"
        dependent_plugin = "DependentPlugin"
        self.plugin_manager.plugins = {
            plugin_name: {
                "metadata": {"name": plugin_name, "version": "1.0.0"},
                "enabled": True,
                "modules": []
            },
            dependent_plugin: {
                "metadata": {"name": dependent_plugin, "version": "1.0.0", "dependencies": {plugin_name: ">=1.0.0"}},
                "enabled": True,
                "modules": []
            }
        }

        result = self.plugin_manager.disable_plugin(plugin_name)
        self.assertFalse(result, "Plugin should not be disabled if there are active dependents")
        self.assertTrue(self.plugin_manager.plugins[plugin_name]["enabled"], "Plugin status should remain enabled")

if __name__ == '__main__':
    unittest.main()
