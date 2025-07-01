"""Test module for ToolManagerUI."""

import unittest
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication

from ui.tools.tool_manager_ui import ToolManagerUI


class TestToolManagerUI(unittest.TestCase):
    """Test class for ToolManagerUI."""

    @classmethod
    def setUpClass(cls):
        """Set up the QApplication before all tests."""
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        """Clean up the QApplication after all tests."""
        cls.app.quit()

    def setUp(self):
        """Set up the test environment before each test."""
        self.tool_manager = ToolManagerUI()

    def test_initialization(self):
        """Test that ToolManagerUI initializes correctly."""
        self.assertIsNotNone(self.tool_manager)
        self.assertEqual(self.tool_manager.windowTitle(), "Atlas Tool Manager")
        self.assertEqual(self.tool_manager.tools, [])

    def test_update_tool_list(self):
        """Test updating the tool list."""
        tools = ["Tool1", "Tool2", "Tool3"]
        self.tool_manager.update_tool_list(tools)
        self.assertEqual(self.tool_manager.tools, tools)
        self.assertEqual(self.tool_manager.tool_list.count(), len(tools))
        for i, tool in enumerate(tools):
            self.assertEqual(self.tool_manager.tool_list.item(i).text(), tool)

    def test_tool_selection(self):
        """Test tool selection functionality."""
        tools = ["Tool1", "Tool2", "Tool3"]
        self.tool_manager.update_tool_list(tools)

        # Connect a mock to the tool_selected signal
        mock_selected = MagicMock()
        self.tool_manager.tool_selected.connect(mock_selected)

        # Select the second tool
        self.tool_manager.tool_list.setCurrentRow(1)
        mock_selected.assert_called_with("Tool2")

    def test_tool_activation(self):
        """Test tool activation functionality."""
        tools = ["Tool1", "Tool2", "Tool3"]
        self.tool_manager.update_tool_list(tools)

        # Connect a mock to the tool_activated signal
        mock_activated = MagicMock()
        self.tool_manager.tool_activated.connect(mock_activated)

        # Select the first tool and activate it
        self.tool_manager.tool_list.setCurrentRow(0)
        self.tool_manager.on_activate_tool()
        mock_activated.assert_called_with("Tool1")

    def test_refresh_tools(self):
        """Test refreshing the tool list."""
        tools = ["Tool1", "Tool2", "Tool3"]
        self.tool_manager.update_tool_list(tools)
        self.tool_manager.tool_list.setCurrentRow(1)

        # Refresh should clear selection
        self.tool_manager.refresh_tools()
        self.assertIsNone(self.tool_manager.tool_list.currentItem())


if __name__ == "__main__":
    unittest.main()
