import time
import unittest
from unittest.mock import MagicMock

from modules.agents.agent_manager import AgentManager
from modules.agents.plugin_manager import PluginManager


class PluginLoadTest(unittest.TestCase):
    def setUp(self):
        self.agent_manager = MagicMock(spec=AgentManager)
        self.plugin_manager = PluginManager(
            self.agent_manager, plugin_dir="test_plugins"
        )

    def test_load_multiple_plugins(self):
        """Test loading a large number of plugins to simulate load."""
        num_plugins = 100
        plugins_dict = {}
        for i in range(num_plugins):
            plugin_name = f"plugin_{i}"
            plugins_dict[plugin_name] = {
                "manifest": {
                    "name": f"Plugin {i}",
                    "version": "1.0",
                    "description": f"Test Plugin {i}",
                },
                "tools": [],
                "agents": [],
            }
        self.plugin_manager.plugins = plugins_dict

        start_time = time.time()
        result = self.plugin_manager.get_all_plugins()
        end_time = time.time()

        self.assertEqual(len(result), num_plugins)
        self.assertLess(end_time - start_time, 1.0, "Loading 100 plugins took too long")

    def test_enable_multiple_plugins(self):
        """Test enabling a large number of plugins under load."""
        num_plugins = 100
        plugins_dict = {}
        for i in range(num_plugins):
            plugin_name = f"plugin_{i}"
            plugins_dict[plugin_name] = {
                "manifest": {
                    "name": f"Plugin {i}",
                    "version": "1.0",
                    "description": f"Test Plugin {i}",
                },
                "tools": [],
                "agents": [],
            }
        self.plugin_manager.plugins = plugins_dict

        start_time = time.time()
        for i in range(num_plugins):
            plugin_name = f"plugin_{i}"
            self.plugin_manager.enable_plugin(plugin_name)
        end_time = time.time()

        self.assertLess(
            end_time - start_time, 2.0, "Enabling 100 plugins took too long"
        )

    def test_plugin_status_check_under_load(self):
        """Test checking status of multiple plugins under load."""
        num_plugins = 100
        plugins_dict = {}
        for i in range(num_plugins):
            plugin_name = f"plugin_{i}"
            plugins_dict[plugin_name] = {
                "manifest": {
                    "name": f"Plugin {i}",
                    "version": "1.0",
                    "description": f"Test Plugin {i}",
                },
                "tools": [],
                "agents": [],
            }
        self.plugin_manager.plugins = plugins_dict

        start_time = time.time()
        for i in range(num_plugins):
            plugin_name = f"plugin_{i}"
            self.plugin_manager.get_plugin_status(plugin_name)
        end_time = time.time()

        self.assertLess(
            end_time - start_time, 1.0, "Checking status of 100 plugins took too long"
        )


if __name__ == "__main__":
    unittest.main()
