#!/usr/bin/env python3
"""
Tests for the Atlas Tool Manager.
"""

import asyncio
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from tools.base_tool import BaseTool
from tools.tool_manager import ToolManager


class MockTool(BaseTool):
    """Mock tool for testing."""

    def __init__(self):
        super().__init__()
        self._name = "test_tool"
        self._category = "general"
        self._description = "Mock tool for testing"
        self.executed = False
        self.execute_result = {"success": True, "message": "Mock execution"}

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._description

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "First parameter"},
                "param2": {"type": "string", "description": "Second parameter"},
            },
        }

    async def execute(self, *args, **kwargs):
        self.executed = True
        return self.execute_result

    async def run(self, *args, **kwargs):
        return {"success": True, "result": f"Mock tool executed with {args} {kwargs}"}

    def get_metadata(self):
        return {
            "name": "test_tool",
            "category": "general",
            "description": "Mock tool for testing",
        }


class TestToolManager(TestCase):
    """Test cases for ToolManager."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.event_bus_mock = Mock()
        self.tool_manager = ToolManager(self.event_bus_mock)

    def test_initialization(self):
        """Test that ToolManager initializes correctly."""
        self.assertIsNotNone(self.tool_manager.event_bus)
        self.assertEqual(self.tool_manager.tools, {})
        self.assertEqual(self.tool_manager.tool_classes, {})
        self.assertEqual(self.tool_manager.categories, {})

    def test_register_tool_class(self):
        """Test registering a tool class."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.assertIn("test_tool", self.tool_manager.tool_classes)
        self.assertEqual(self.tool_manager.tool_classes["test_tool"], tool_class)

    def test_load_tool(self):
        """Test loading a tool."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        result = self.tool_manager.load_tool("test_tool")
        self.assertTrue(result)
        self.assertIn("test_tool", self.tool_manager.tools)

    def test_load_tool_already_loaded(self):
        """Test loading a tool that is already loaded."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        result = self.tool_manager.load_tool("test_tool")
        self.assertTrue(result)
        self.assertIn("test_tool", self.tool_manager.tools)

    def test_load_tool_not_registered(self):
        """Test loading a tool that is not registered."""
        result = self.tool_manager.load_tool("nonexistent_tool")
        self.assertFalse(result)
        self.assertNotIn("nonexistent_tool", self.tool_manager.tools)

    def test_unload_tool(self):
        """Test unloading a tool."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        result = self.tool_manager.unload_tool("test_tool")
        self.assertTrue(result)
        self.assertNotIn("test_tool", self.tool_manager.tools)

    def test_unload_tool_not_loaded(self):
        """Test unloading a tool that is not loaded."""
        result = self.tool_manager.unload_tool("nonexistent_tool")
        self.assertTrue(result)

    def test_get_tool(self):
        """Test getting a tool instance."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        tool = self.tool_manager.get_tool("test_tool")
        self.assertIsNotNone(tool)
        self.assertIsInstance(tool, BaseTool)

    def test_get_tool_nonexistent(self):
        """Test getting a non-existent tool."""
        tool = self.tool_manager.get_tool("nonexistent_tool")
        self.assertIsNone(tool)

    def test_execute_tool_success(self):
        """Test executing a tool successfully."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        tool_instance = self.tool_manager.get_tool("test_tool")
        if tool_instance is not None:
            # Set up the mock for async run method
            tool_instance.run = AsyncMock(
                return_value={
                    "success": True,
                    "result": "Mock tool executed with arg1=value1",
                }
            )
        result = asyncio.run(self.tool_manager.execute_tool("test_tool", arg1="value1"))
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "Mock tool executed with arg1=value1")

    def test_execute_tool_not_found(self):
        """Test executing a non-existent tool."""
        result = asyncio.run(self.tool_manager.execute_tool("nonexistent_tool"))
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_execute_tool_exception(self):
        """Test executing a tool that raises an exception."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        tool_instance = self.tool_manager.get_tool("test_tool")
        if tool_instance is not None:
            # Set up the mock to raise an exception when run is called
            tool_instance.run = AsyncMock(side_effect=ValueError("Test error"))
        with self.assertRaises(ValueError):
            asyncio.run(self.tool_manager.execute_tool("test_tool"))

    def test_list_tools(self):
        """Test listing loaded tools."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        tools = self.tool_manager.list_tools()
        self.assertIn("test_tool", tools)

    def test_list_tool_classes(self):
        """Test listing registered tool classes."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        tool_classes = self.tool_manager.list_tool_classes()
        self.assertIn("test_tool", tool_classes)

    def test_list_categories(self):
        """Test listing tool categories."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        categories = self.tool_manager.list_categories()
        self.assertIn("general", categories)
        self.assertIn("test_tool", categories["general"])

    def test_get_tool_metadata(self):
        """Test getting tool metadata."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        metadata = self.tool_manager.get_tool_metadata("test_tool")
        self.assertIsNotNone(metadata)
        if isinstance(metadata, dict):
            self.assertEqual(metadata.get("name", ""), "test_tool")
        else:
            self.assertEqual(getattr(metadata, "name", ""), "test_tool")

    def test_get_tool_metadata_nonexistent(self):
        """Test getting metadata for non-existent tool."""
        metadata = self.tool_manager.get_tool_metadata("nonexistent_tool")
        self.assertIsNone(metadata)

    def test_get_all_metadata(self):
        """Test getting metadata for all tools."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        all_metadata = self.tool_manager.get_all_metadata()
        self.assertIn("test_tool", all_metadata)
        metadata = all_metadata["test_tool"]
        if isinstance(metadata, dict):
            self.assertEqual(metadata.get("name", ""), "test_tool")
        else:
            self.assertEqual(getattr(metadata, "name", ""), "test_tool")

    @patch("tools.tool_manager.ToolManager.discover_tools")
    def test_discover_tools(self, mock_discover):
        """Test discovering tools."""
        mock_discover.return_value = True
        result = self.tool_manager.discover_tools()
        self.assertTrue(result)
        mock_discover.assert_called_once()

    def test_initialize_all_tools(self):
        """Test initializing all tools."""
        mock_tool_class = MockTool
        with patch.object(
            self.tool_manager, "discover_tools", return_value=[mock_tool_class]
        ):
            self.tool_manager.initialize_all_tools()
            self.assertIn("mock", self.tool_manager.tool_classes)
            self.assertIn("mock", self.tool_manager.tools)

    def test_shutdown(self):
        """Test shutting down the tool manager."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        self.tool_manager.shutdown()
        self.assertEqual(len(self.tool_manager.tools), 0)
        self.assertEqual(len(self.tool_manager.tool_classes), 0)
        self.assertEqual(len(self.tool_manager.categories), 0)

    def test_reload_tool(self):
        """Test reloading a tool."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        result = self.tool_manager.reload_tool("test_tool")
        self.assertTrue(result)
        self.assertIn("test_tool", self.tool_manager.tools)

    def test_handle_tool_error(self):
        """Test handling tool errors."""
        tool_class = MockTool
        self.tool_manager.register_tool_class(tool_class, name="test_tool")
        self.tool_manager.load_tool("test_tool")
        with patch.object(self.tool_manager, "reload_tool", return_value=True):
            self.tool_manager.handle_tool_error("test_tool", "Test error")
            # Just ensure no exceptions are raised
            self.assertTrue(True)

    def test_event_publishing(self):
        """Test that events are published correctly."""
        event_bus = Mock()
        tool_manager = ToolManager(event_bus=event_bus)
        tool_class = MockTool
        tool_manager.register_tool_class(tool_class, name="test_tool")
        tool_manager.load_tool("test_tool")
        event_bus.publish.assert_called()
