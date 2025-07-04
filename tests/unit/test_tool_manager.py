import asyncio
import unittest
import unittest.mock
from unittest.mock import MagicMock, patch

from core.event_bus import EventBus


class TestToolManager(unittest.TestCase):
    """Tests for the ToolManager class."""

    def setUp(self):
        """Set up test environment before each test."""
        self.event_bus = EventBus()
        # Import here to avoid circular import issues
        from tools.tool_manager import ToolManager

        self.tool_manager = ToolManager(self.event_bus)

    def test_initialization(self):
        """Test that ToolManager initializes correctly."""
        self.assertEqual(self.tool_manager.event_bus, self.event_bus)
        self.assertIsInstance(self.tool_manager.tools, dict)
        self.assertIsInstance(self.tool_manager.tool_classes, dict)

    def test_register_tool_class(self):
        """Test registering a tool class."""
        # Create a mock tool class
        mock_tool_class = MagicMock()
        mock_tool_class.TOOL_NAME = "test_tool"

        # Register the tool class
        self.tool_manager.register_tool_class(mock_tool_class)

        # Verify tool class was registered
        self.assertIn("test_tool", self.tool_manager.tool_classes)
        self.assertEqual(self.tool_manager.tool_classes["test_tool"], mock_tool_class)

    def test_register_duplicate_tool_class(self):
        """Test registering a duplicate tool class."""
        # Create mock tool classes with the same name
        mock_tool_class1 = MagicMock()
        mock_tool_class1.TOOL_NAME = "test_tool"
        mock_tool_class2 = MagicMock()
        mock_tool_class2.TOOL_NAME = "test_tool"

        # Register the first tool class
        self.tool_manager.register_tool_class(mock_tool_class1)

        # Register the second tool class (should override the first)
        self.tool_manager.register_tool_class(mock_tool_class2)

        # Verify the second tool class was registered
        self.assertEqual(self.tool_manager.tool_classes["test_tool"], mock_tool_class2)

    def test_load_tool(self):
        """Test loading a tool."""
        # Create a mock tool class and instance
        mock_tool_class = MagicMock()
        mock_tool_class.TOOL_NAME = "test_tool"
        mock_tool_instance = MagicMock()
        mock_tool_class.return_value = mock_tool_instance

        # Register the tool class
        self.tool_manager.register_tool_class(mock_tool_class)

        # Load the tool
        result = self.tool_manager.load_tool("test_tool")

        # Verify tool was loaded
        self.assertTrue(result)
        self.assertIn("test_tool", self.tool_manager.tools)
        self.assertEqual(self.tool_manager.tools["test_tool"], mock_tool_instance)

        # Verify tool instance was initialized
        mock_tool_instance.initialize.assert_called_once()

    def test_load_nonexistent_tool(self):
        """Test loading a tool that doesn't exist."""
        # Try to load a nonexistent tool
        result = self.tool_manager.load_tool("nonexistent_tool")

        # Verify tool was not loaded
        self.assertFalse(result)
        self.assertNotIn("nonexistent_tool", self.tool_manager.tools)

    def test_unload_tool(self):
        """Test unloading a tool."""
        # Create a mock tool instance
        mock_tool = MagicMock()
        self.tool_manager.tools["test_tool"] = mock_tool

        # Unload the tool
        self.tool_manager.unload_tool("test_tool")

        # Verify tool was unloaded
        self.assertNotIn("test_tool", self.tool_manager.tools)
        mock_tool.shutdown.assert_called_once()

    def test_unload_nonexistent_tool(self):
        """Test unloading a tool that doesn't exist."""
        # Should not raise an exception
        self.tool_manager.unload_tool("nonexistent_tool")

    def test_get_tool(self):
        """Test getting a tool."""
        # Create a mock tool instance
        mock_tool = MagicMock()
        self.tool_manager.tools["test_tool"] = mock_tool

        # Get the tool
        tool = self.tool_manager.get_tool("test_tool")

        # Verify correct tool was returned
        self.assertEqual(tool, mock_tool)

    def test_get_nonexistent_tool(self):
        """Test getting a tool that doesn't exist."""
        tool = self.tool_manager.get_tool("nonexistent_tool")
        self.assertIsNone(tool)

    def test_get_all_tools(self):
        """Test getting all tools."""
        # Add some mock tools
        self.tool_manager.tools = {"tool1": MagicMock(), "tool2": MagicMock()}

        # Get all tools
        tools = self.tool_manager.get_all_tools()

        # Verify all tools were returned
        self.assertEqual(len(tools), 2)
        self.assertIn("tool1", tools)
        self.assertIn("tool2", tools)

    def test_execute_tool(self):
        """Test executing a tool."""
        # Create a mock tool instance with a synchronous execute method
        mock_tool = MagicMock()
        mock_tool.execute = MagicMock(return_value="result")
        self.tool_manager.tools["test_tool"] = mock_tool

        # Execute the tool synchronously
        result = asyncio.run(self.tool_manager.execute_tool("test_tool", arg1="value1"))

        # Verify tool was executed with correct args
        mock_tool.execute.assert_called_once_with(arg1="value1")
        self.assertEqual(result, "result")

    def test_execute_async_tool(self):
        """Test executing a tool with an async execute method."""
        # Create a mock tool instance with an asynchronous execute method
        mock_tool = MagicMock()

        async def mock_execute(**kwargs):
            return "async_result"

        mock_tool.execute = mock_execute
        self.tool_manager.tools["test_tool"] = mock_tool

        # Execute the tool asynchronously
        result = asyncio.run(self.tool_manager.execute_tool("test_tool", arg1="value1"))

        # Verify result
        self.assertEqual(result, "async_result")

    def test_execute_nonexistent_tool(self):
        """Test executing a tool that doesn't exist."""
        with self.assertRaises(ValueError):
            asyncio.run(self.tool_manager.execute_tool("nonexistent_tool"))

    def test_initialize_all_tools(self):
        """Test initializing all tools."""
        # Create mock tool classes
        mock_tool_class1 = MagicMock()
        mock_tool_class1.TOOL_NAME = "tool1"
        mock_tool_instance1 = MagicMock()
        mock_tool_class1.return_value = mock_tool_instance1

        mock_tool_class2 = MagicMock()
        mock_tool_class2.TOOL_NAME = "tool2"
        mock_tool_instance2 = MagicMock()
        mock_tool_class2.return_value = mock_tool_instance2

        # Register the tool classes
        self.tool_manager.tool_classes = {
            "tool1": mock_tool_class1,
            "tool2": mock_tool_class2,
        }

        # Initialize all tools
        with patch.object(self.tool_manager, "load_tool") as mock_load:
            mock_load.return_value = True
            self.tool_manager.initialize_all_tools()

            # Verify load_tool was called for each tool class
            self.assertEqual(mock_load.call_count, 2)
            mock_load.assert_any_call("tool1")
            mock_load.assert_any_call("tool2")

    def test_shutdown_all_tools(self):
        """Test shutting down all tools."""
        # Add some mock tools
        mock_tool1 = MagicMock()
        mock_tool2 = MagicMock()
        self.tool_manager.tools = {"tool1": mock_tool1, "tool2": mock_tool2}

        # Shutdown all tools
        self.tool_manager.shutdown_all_tools()

        # Verify all tools were shut down
        mock_tool1.shutdown.assert_called_once()
        mock_tool2.shutdown.assert_called_once()
        self.assertEqual(len(self.tool_manager.tools), 0)


if __name__ == "__main__":
    unittest.main()
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

    def test_get_tool_not_found(self):
        """Test retrieving a tool that does not exist."""
        self.tool_manager.get_tool.return_value = None
        result = self.tool_manager.get_tool("Nonexistent Tool")
        self.assertIsNone(result)
        self.tool_manager.get_tool.assert_called_once_with("Nonexistent Tool")

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

    def test_get_tools_by_type_empty(self):
        """Test retrieving tools by type when no tools of that type exist."""
        self.tool_manager.get_tools_by_type.return_value = []
        result = self.tool_manager.get_tools_by_type(core.tools.ToolType.ACTION)
        self.assertEqual(len(result), 0)
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

    def test_execute_tool_not_found(self):
        """Test executing a tool that does not exist."""
        self.tool_manager.get_tool.return_value = None
        self.tool_manager.execute_tool.return_value = None
        result = self.tool_manager.execute_tool("Nonexistent Tool")
        self.assertIsNone(result)
        self.tool_manager.execute_tool.assert_called_once_with("Nonexistent Tool")

    def test_execute_tool_with_error(self):
        """Test executing a tool that raises an exception."""
        mock_tool = core.tools.Tool()
        mock_tool.name = "Error Tool"
        mock_tool.execute = MagicMock(side_effect=Exception("Tool execution failed"))
        self.tool_manager.tools.append(mock_tool)
        self.tool_manager.get_tool.return_value = mock_tool
        self.tool_manager.execute_tool.return_value = None
        result = self.tool_manager.execute_tool("Error Tool")
        self.assertIsNone(result)
        self.tool_manager.execute_tool.assert_called_once_with("Error Tool")


if __name__ == "__main__":
    unittest.main()
