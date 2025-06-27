import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import Qt

# Adjust the system path to include the project root directory for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Project root added to sys.path: {project_root}")
print(f"Current sys.path: {sys.path}")

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

try:
    from ui.main_window import AtlasMainWindow
    from ui.plugin_marketplace_module import PluginMarketplace
except ImportError as e:
    print(f"Import error: {e}")
    raise


class PluginMarketplaceTest(unittest.TestCase):
    def setUp(self):
        # Ensure a QApplication instance exists for Qt operations
        if QCoreApplication.instance() is None:
            self.app = QApplication([])
        else:
            self.app = QCoreApplication.instance()
        # Mock dependencies
        self.mock_meta_agent = MagicMock()
        self.mock_meta_agent.agent_manager = MagicMock()
        self.mock_meta_agent.plugin_manager = MagicMock()

    def test_plugin_marketplace_initialization(self):
        """Test that PluginMarketplace module initializes correctly."""
        marketplace = PluginMarketplace(
            plugin_manager=self.mock_meta_agent.plugin_manager
        )
        self.assertIsNotNone(marketplace, "PluginMarketplace should initialize")
        self.assertIsNotNone(
            marketplace.plugin_list, "Plugin list should be initialized"
        )
        self.assertIsNotNone(
            marketplace.search_input, "Search input should be initialized"
        )
        self.assertIsNotNone(
            marketplace.install_button, "Install button should be initialized"
        )
        self.assertIsNotNone(
            marketplace.update_button, "Update button should be initialized"
        )

    def test_plugin_marketplace_integration(self):
        """Test integration of PluginMarketplace with AtlasMainWindow."""
        main_window = AtlasMainWindow(meta_agent=self.mock_meta_agent)
        self.assertIn(
            "marketplace",
            main_window.modules,
            "PluginMarketplace should be initialized in main window",
        )
        self.assertIsInstance(
            main_window.modules["marketplace"],
            PluginMarketplace,
            "Module should be of type PluginMarketplace",
        )

    def test_search_plugins(self):
        """Test searching for plugins in the marketplace."""
        marketplace = PluginMarketplace(
            plugin_manager=self.mock_meta_agent.plugin_manager
        )
        marketplace.search_input.setText("test")
        self.assertGreater(
            marketplace.plugin_list.count(),
            0,
            "Plugin list should populate after search",
        )

    def test_install_plugin_button_enable(self):
        """Test that install button enables when a plugin is selected."""
        marketplace = PluginMarketplace(
            plugin_manager=self.mock_meta_agent.plugin_manager
        )
        marketplace.search_input.setText("test")
        # Ensure the plugin data is set correctly
        item = marketplace.plugin_list.item(0)
        if item:
            plugin_data = {
                "name": "Example Plugin",
                "version": "1.0.0",
                "description": "A sample plugin for testing.",
            }
            item.setData(Qt.UserRole, plugin_data)
            marketplace.plugin_list.setCurrentItem(item)
            marketplace.on_plugin_selected(item)
            self.assertTrue(
                marketplace.install_button.isEnabled(),
                "Install button should be enabled after selecting a plugin",
            )
        else:
            self.fail("No plugin item found in the list after search")

    def test_update_plugin_button_enable(self):
        """Test that update button enables when a newer version is available."""
        marketplace = PluginMarketplace(
            plugin_manager=self.mock_meta_agent.plugin_manager
        )
        marketplace.search_input.setText("test")
        # Mock installed plugins with older version
        self.mock_meta_agent.plugin_manager.get_all_plugins.return_value = {
            "Example Plugin": {
                "metadata": {"name": "Example Plugin", "version": "0.9.0"},
                "enabled": True,
            }
        }
        # Ensure the plugin data is set correctly
        item = marketplace.plugin_list.item(0)
        if item:
            plugin_data = {
                "name": "Example Plugin",
                "version": "1.0.0",
                "description": "A sample plugin for testing.",
            }
            item.setData(Qt.UserRole, plugin_data)
            marketplace.plugin_list.setCurrentItem(item)
            marketplace.on_plugin_selected(item)
            self.assertTrue(
                marketplace.update_button.isEnabled(),
                "Update button should be enabled when a newer version is available",
            )
        else:
            self.fail("No plugin item found in the list after search")

    @patch("PySide6.QtWidgets.QMessageBox.information")
    def test_install_plugin_action(self, mock_msg_box):
        """Test installing a plugin emits the correct signal and shows confirmation."""
        marketplace = PluginMarketplace(
            plugin_manager=self.mock_meta_agent.plugin_manager
        )
        marketplace.search_input.setText("test")
        marketplace.plugin_list.setCurrentRow(0)
        mock_signal = MagicMock()
        marketplace.plugin_installed.connect(mock_signal)
        marketplace.install_plugin()
        mock_signal.assert_called_once_with("Example Plugin")
        mock_msg_box.assert_called_once()

    @patch("PySide6.QtWidgets.QMessageBox.information")
    def test_update_plugin_action(self, mock_msg_box):
        """Test updating a plugin emits the correct signal and shows confirmation."""
        marketplace = PluginMarketplace(
            plugin_manager=self.mock_meta_agent.plugin_manager
        )
        marketplace.search_input.setText("test")
        self.mock_meta_agent.plugin_manager.get_all_plugins.return_value = {
            "Example Plugin": {
                "metadata": {"name": "Example Plugin", "version": "0.9.0"},
                "enabled": True,
            }
        }
        marketplace.plugin_list.setCurrentRow(0)
        mock_signal = MagicMock()
        marketplace.plugin_updated.connect(mock_signal)
        marketplace.update_plugin()
        mock_signal.assert_called_once_with("Example Plugin")
        mock_msg_box.assert_called_once()


if __name__ == "__main__":
    unittest.main()
