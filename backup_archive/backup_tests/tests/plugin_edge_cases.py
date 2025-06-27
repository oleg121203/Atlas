import unittest
from unittest.mock import MagicMock

from modules.agents.agent_manager import AgentManager
from modules.agents.plugin_manager import PluginManager


class PluginEdgeCaseTests(unittest.TestCase):
    def setUp(self):
        self.agent_manager = MagicMock(spec=AgentManager)
        self.plugin_manager = PluginManager(
            self.agent_manager, plugin_dir="test_plugins"
        )

    def test_plugin_with_invalid_metadata(self):
        """Test handling of a plugin with invalid metadata."""
        invalid_metadata = {
            "name": "",
            "version": "1.0",
            "description": "Invalid Plugin",
        }
        self.plugin_manager.plugins = {"invalid_plugin": {"manifest": invalid_metadata}}
        result = self.plugin_manager.get_all_plugins()
        self.assertIn("invalid_plugin", result)
        # Check that the plugin is in the dictionary, even if it might not be enabled
        self.assertEqual(result["invalid_plugin"]["manifest"], invalid_metadata)

    def test_plugin_with_missing_files(self):
        """Test handling of a plugin directory missing required files."""
        missing_files_metadata = {
            "name": "MissingFilesPlugin",
            "version": "1.0",
            "description": "Plugin with missing files",
        }
        self.plugin_manager.plugins = {
            "missing_files_plugin": {"manifest": missing_files_metadata}
        }
        result = self.plugin_manager.get_all_plugins()
        self.assertIn("missing_files_plugin", result)
        # Check that the plugin is in the dictionary, even if it might not be enabled
        self.assertEqual(
            result["missing_files_plugin"]["manifest"], missing_files_metadata
        )

    def test_plugin_enable_with_no_tools_or_agents(self):
        """Test enabling a plugin that registers no tools or agents."""
        empty_plugin_metadata = {
            "name": "EmptyPlugin",
            "version": "1.0",
            "description": "Plugin with no tools or agents",
        }
        self.plugin_manager.plugins = {
            "empty_plugin": {
                "manifest": empty_plugin_metadata,
                "tools": [],
                "agents": [],
            }
        }
        success = self.plugin_manager.enable_plugin("empty_plugin")
        self.assertTrue(success)
        self.agent_manager.add_tool.assert_not_called()
        self.agent_manager.add_agent.assert_not_called()


if __name__ == "__main__":
    unittest.main()
