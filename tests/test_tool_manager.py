#!/usr/bin/env python3
"""
Tests for the Atlas Tool Manager.
"""

from unittest.mock import Mock, patch

from tools.base_tool import BaseTool
from tools.tool_manager import ToolManager


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(self, name="mock_tool"):
        super().__init__()
        self._name = name
        self.executed = False
        self.execute_result = {"success": True, "message": "Mock execution"}

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return f"Mock tool: {self._name}"

    def get_parameters(self) -> dict:
        return {
            "param1": {
                "type": "string",
                "description": "Test parameter",
                "required": False,
            }
        }

    async def execute(self, **kwargs):
        self.executed = True
        return self.execute_result


class TestToolManager:
    """Test cases for ToolManager."""

    def test_init(self):
        """Test ToolManager initialization."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        assert tool_manager.event_bus == event_bus
        assert tool_manager.tools == {}
        assert tool_manager.tool_classes == {}

    def test_register_tool_class(self):
        """Test registering a tool class."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        tool_manager.register_tool_class("mock", MockTool)

        assert "mock" in tool_manager.tool_classes
        assert tool_manager.tool_classes["mock"] == MockTool

    def test_register_tool_instance_success(self):
        """Test successful tool instance registration."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        mock_tool = MockTool("test_tool")
        result = tool_manager.register_tool(mock_tool)

        assert result is True
        assert "test_tool" in tool_manager.tools
        assert tool_manager.tools["test_tool"] == mock_tool

    def test_register_tool_instance_duplicate(self):
        """Test registering duplicate tool instance."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        mock_tool1 = MockTool("test_tool")
        mock_tool2 = MockTool("test_tool")

        result1 = tool_manager.register_tool(mock_tool1)
        result2 = tool_manager.register_tool(mock_tool2)

        assert result1 is True
        assert result2 is False  # Should fail due to duplicate name

    def test_get_tool(self):
        """Test getting a tool by name."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        mock_tool = MockTool("test_tool")
        tool_manager.register_tool(mock_tool)

        result = tool_manager.get_tool("test_tool")

        assert result == mock_tool

    def test_get_tool_nonexistent(self):
        """Test getting a nonexistent tool."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        result = tool_manager.get_tool("nonexistent_tool")

        assert result is None

    def test_list_tools(self):
        """Test listing all tools."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        mock_tool1 = MockTool("tool1")
        mock_tool2 = MockTool("tool2")
        tool_manager.register_tool(mock_tool1)
        tool_manager.register_tool(mock_tool2)

        tools = tool_manager.list_tools()

        assert set(tools) == {"tool1", "tool2"}

    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        mock_tool1 = MockTool("tool1")
        mock_tool1.category = "category1"
        mock_tool2 = MockTool("tool2")
        mock_tool2.category = "category2"
        mock_tool3 = MockTool("tool3")
        mock_tool3.category = "category1"

        tool_manager.register_tool(mock_tool1)
        tool_manager.register_tool(mock_tool2)
        tool_manager.register_tool(mock_tool3)

        category1_tools = tool_manager.get_tools_by_category("category1")

        assert len(category1_tools) == 2
        assert mock_tool1 in category1_tools
        assert mock_tool3 in category1_tools

    async def test_execute_tool_success(self):
        """Test successful tool execution."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        mock_tool = MockTool("test_tool")
        tool_manager.register_tool(mock_tool)

        result = await tool_manager.execute_tool("test_tool", param1="test")

        assert result == mock_tool.execute_result
        assert mock_tool.executed is True

    async def test_execute_tool_nonexistent(self):
        """Test executing a nonexistent tool."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        result = await tool_manager.execute_tool("nonexistent_tool")

        assert "error" in result
        assert result["success"] is False

    async def test_execute_tool_exception(self):
        """Test tool execution with exception."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        mock_tool = MockTool("test_tool")
        mock_tool.execute = Mock(side_effect=Exception("Test error"))
        tool_manager.register_tool(mock_tool)

        result = await tool_manager.execute_tool("test_tool")

        assert "error" in result
        assert result["success"] is False

    def test_load_tools_from_directory(self):
        """Test loading tools from directory."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        # Mock the directory scanning and module loading
        with (
            patch("tools.tool_manager.os.listdir") as mock_listdir,
            patch("tools.tool_manager.importlib.import_module") as mock_import,
        ):
            mock_listdir.return_value = [
                "test_tool.py",
                "__init__.py",
                "not_a_tool.txt",
            ]

            # Mock module with tool class
            mock_module = Mock()
            mock_module.TestTool = MockTool
            mock_import.return_value = mock_module

            # Mock inspect to find tool classes
            with patch("tools.tool_manager.inspect.getmembers") as mock_getmembers:
                mock_getmembers.return_value = [("TestTool", MockTool)]

                tool_manager._load_tools_from_directory()

                # Should have registered the tool class
                assert len(tool_manager.tool_classes) > 0

    def test_initialize_all_tools(self):
        """Test initializing all registered tool classes."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        # Register a tool class
        tool_manager.register_tool_class("mock", MockTool)

        tool_manager.initialize_all_tools()

        # Should have created and registered an instance
        assert "mock_tool" in tool_manager.tools
        assert isinstance(tool_manager.tools["mock_tool"], MockTool)

    def test_get_tool_info(self):
        """Test getting tool information."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        mock_tool = MockTool("test_tool")
        tool_manager.register_tool(mock_tool)

        info = tool_manager.get_tool_info("test_tool")

        assert info["name"] == "test_tool"
        assert info["description"] == "Mock tool: test_tool"
        assert "parameters" in info

    def test_get_tool_info_nonexistent(self):
        """Test getting info for nonexistent tool."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        info = tool_manager.get_tool_info("nonexistent_tool")

        assert info is None

    def test_unregister_tool(self):
        """Test unregistering a tool."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        mock_tool = MockTool("test_tool")
        tool_manager.register_tool(mock_tool)

        # Verify tool is registered
        assert "test_tool" in tool_manager.tools

        result = tool_manager.unregister_tool("test_tool")

        assert result is True
        assert "test_tool" not in tool_manager.tools

    def test_unregister_tool_nonexistent(self):
        """Test unregistering a nonexistent tool."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        result = tool_manager.unregister_tool("nonexistent_tool")

        assert result is False

    def test_event_publishing(self):
        """Test that events are published correctly."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus)

        mock_tool = MockTool("test_tool")
        tool_manager.register_tool(mock_tool)

        # Should publish tool_registered event
        event_bus.publish.assert_called_with(
            "tool_registered", tool_name="test_tool", tool=mock_tool
        )
