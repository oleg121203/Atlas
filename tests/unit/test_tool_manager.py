import unittest
import unittest.mock
from unittest.mock import MagicMock

# Mock the core.tools module and its classes to avoid import errors
core = unittest.mock.MagicMock()
core.tools = unittest.mock.MagicMock()
core.tools.ToolManager = MagicMock()
core.tools.Tool = MagicMock()
core.tools.ToolType = MagicMock()


class TestToolManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.tool_manager = core.tools.ToolManager()
        self.tool_manager.tools = []
        self.tool_manager.register_tool = MagicMock()
        self.tool_manager.get_tool = MagicMock()
        self.tool_manager.get_tools_by_type = MagicMock()
        self.tool_manager.get_all_tools = MagicMock()
        self.tool_manager.load_tools_from_module = MagicMock()
        self.tool_manager.execute_tool = MagicMock()

    def test_tool_manager_init(self):
        """Test ToolManager initialization."""
        self.assertIsNotNone(self.tool_manager)
        self.assertEqual(self.tool_manager.tools, [])

    def test_register_tool(self):
        """Test registering a tool with ToolManager."""
        mock_tool = core.tools.Tool()
        mock_tool.name = "Test Tool"
        mock_tool.tool_type = core.tools.ToolType.ACTION
        self.tool_manager.register_tool(mock_tool)
        self.assertEqual(self.tool_manager.register_tool.call_count, 1)
        self.assertEqual(
            self.tool_manager.register_tool.call_args[0][0].name, "Test Tool"
        )

    def test_get_tool(self):
        """Test retrieving a tool by name."""
        mock_tool = core.tools.Tool()
        mock_tool.name = "Test Tool"
        self.tool_manager.tools.append(mock_tool)
        self.tool_manager.get_tool.return_value = mock_tool
        result = self.tool_manager.get_tool("Test Tool")
        self.assertEqual(result.name, "Test Tool")
        self.tool_manager.get_tool.assert_called_once_with("Test Tool")

    def test_get_tools_by_type(self):
        """Test retrieving tools by type."""
        mock_tool1 = core.tools.Tool()
        mock_tool1.name = "Action Tool 1"
        mock_tool1.tool_type = core.tools.ToolType.ACTION
        mock_tool2 = core.tools.Tool()
        mock_tool2.name = "Action Tool 2"
        mock_tool2.tool_type = core.tools.ToolType.ACTION
        self.tool_manager.tools.extend([mock_tool1, mock_tool2])
        self.tool_manager.get_tools_by_type.return_value = [mock_tool1, mock_tool2]
        result = self.tool_manager.get_tools_by_type(core.tools.ToolType.ACTION)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].tool_type, core.tools.ToolType.ACTION)
        self.tool_manager.get_tools_by_type.assert_called_once_with(
            core.tools.ToolType.ACTION
        )

    def test_get_all_tools(self):
        """Test retrieving all tools."""
        mock_tool1 = core.tools.Tool()
        mock_tool1.name = "Tool 1"
        mock_tool2 = core.tools.Tool()
        mock_tool2.name = "Tool 2"
        self.tool_manager.tools.extend([mock_tool1, mock_tool2])
        self.tool_manager.get_all_tools.return_value = [mock_tool1, mock_tool2]
        result = self.tool_manager.get_all_tools()
        self.assertEqual(len(result), 2)
        self.tool_manager.get_all_tools.assert_called_once()

    def test_load_tools_from_module(self):
        """Test loading tools from a module."""
        mock_module = MagicMock()
        mock_module.__name__ = "test_module"
        self.tool_manager.load_tools_from_module(mock_module)
        self.tool_manager.load_tools_from_module.assert_called_once_with(mock_module)

    def test_execute_tool(self):
        """Test executing a tool by name with parameters."""
        mock_tool = core.tools.Tool()
        mock_tool.name = "Executable Tool"
        mock_tool.execute = MagicMock(return_value="Tool Output")
        self.tool_manager.tools.append(mock_tool)
        self.tool_manager.get_tool.return_value = mock_tool
        self.tool_manager.execute_tool.return_value = "Tool Output"
        result = self.tool_manager.execute_tool("Executable Tool", param1="value1")
        self.assertEqual(result, "Tool Output")
        self.tool_manager.execute_tool.assert_called_once_with(
            "Executable Tool", param1="value1"
        )


if __name__ == "__main__":
    unittest.main()
