"""
Tool Management System for Atlas.

This module provides comprehensive tool management including discovery,
loading, registration, and lifecycle management of Atlas tools.
"""

import importlib
import inspect
import logging
import os
import pkgutil
from typing import Any, Dict, List, Optional, Type

from tools.base_tool import ToolBase

logger = logging.getLogger(__name__)


class ToolManager:
    """
    Comprehensive tool management system for Atlas.

    This class handles:
    - Tool discovery and loading
    - Tool registration and lifecycle management
    - Tool execution and chaining
    - Performance monitoring and statistics
    - Event system integration
    """

    def __init__(self, event_bus=None):
        """Initialize the tool manager."""
        self.event_bus = event_bus
        self.tools: Dict[str, ToolBase] = {}
        self.tool_classes: Dict[str, Type[ToolBase]] = {}
        self.categories: Dict[str, List[str]] = {}
        self._setup_event_handlers()

        logger.info("ToolManager initialized")

    def _setup_event_handlers(self):
        """Setup event handlers if event bus is available."""
        if self.event_bus:
            self.event_bus.subscribe("tool_reload_requested", self.reload_tool)
            self.event_bus.subscribe("tool_error", self.handle_tool_error)

    def discover_tools(self, package_path: str = "tools") -> List[Type[ToolBase]]:
        """
        Discover all tool classes in the specified package.

        Args:
            package_path: Path to the package containing tools

        Returns:
            List of discovered tool classes
        """
        discovered_tools = []

        # Get the actual file system path
        tools_dir = (
            os.path.join(os.path.dirname(__file__))
            if package_path == "tools"
            else package_path
        )

        if not os.path.exists(tools_dir):
            logger.warning(f"Tools directory not found: {tools_dir}")
            return discovered_tools

        # Scan for Python files in the tools directory
        for importer, modname, _ in pkgutil.iter_modules([tools_dir]):
            if modname.startswith("__") or modname == "base_tool":
                continue

            try:
                # Import the module
                if package_path == "tools":
                    module = importer.find_module(modname).load_module(modname)
                else:
                    module = importlib.import_module(f"{package_path}.{modname}")

                # Look for ToolBase subclasses
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, ToolBase)
                        and obj != ToolBase
                        and obj.__module__ == module.__name__
                    ):
                        discovered_tools.append(obj)
                        logger.debug(f"Discovered tool: {obj.__name__} in {modname}")

            except Exception as e:
                logger.error(f"Error loading tool module {modname}: {e}")

        logger.info(f"Discovered {len(discovered_tools)} tools")
        return discovered_tools

    def register_tool_class(
        self, tool_class: Type[ToolBase], name: Optional[str] = None
    ):
        """
        Register a tool class for later instantiation.

        Args:
            tool_class: The tool class to register
            name: Optional name for the tool (defaults to class-derived name)
        """
        tool_name = name or tool_class.__name__.replace("Tool", "").lower()
        self.tool_classes[tool_name] = tool_class

        logger.info(f"Registered tool class: {tool_name}")

        if self.event_bus:
            self.event_bus.publish("tool_class_registered", tool_name=tool_name)

    def load_tool(self, tool_name: str, **kwargs) -> bool:
        """
        Load and instantiate a tool.

        Args:
            tool_name: Name of the tool to load
            **kwargs: Additional arguments to pass to tool constructor

        Returns:
            True if loading was successful
        """
        if tool_name in self.tools:
            logger.warning(f"Tool {tool_name} is already loaded")
            return True

        if tool_name not in self.tool_classes:
            logger.error(f"Tool class {tool_name} not registered")
            return False

        try:
            tool_class = self.tool_classes[tool_name]
            tool_instance = tool_class(**kwargs)

            # Setup tool registry for chaining
            tool_instance.set_tool_registry(self.get_tool)

            # Setup event bus
            if self.event_bus:
                tool_instance.set_event_bus(self.event_bus)

            # Validate requirements
            if not tool_instance.validate_requirements():
                logger.warning(f"Tool {tool_name} requirements not satisfied")
                # Continue loading but log the warning

            self.tools[tool_name] = tool_instance

            # Update categories
            category = tool_instance.category
            if category not in self.categories:
                self.categories[category] = []
            if tool_name not in self.categories[category]:
                self.categories[category].append(tool_name)

            logger.info(f"Successfully loaded tool: {tool_name}")

            if self.event_bus:
                self.event_bus.publish("tool_loaded", tool_name=tool_name)

            return True

        except Exception as e:
            logger.error(f"Error loading tool {tool_name}: {e}")
            if self.event_bus:
                self.event_bus.publish("tool_error", tool_name=tool_name, error=str(e))
            return False

    def unload_tool(self, tool_name: str) -> bool:
        """
        Unload a tool.

        Args:
            tool_name: Name of the tool to unload

        Returns:
            True if unloading was successful
        """
        if tool_name not in self.tools:
            logger.warning(f"Tool {tool_name} is not loaded")
            return True

        try:
            tool = self.tools[tool_name]

            # Remove from category
            category = tool.category
            if category in self.categories and tool_name in self.categories[category]:
                self.categories[category].remove(tool_name)
                if not self.categories[category]:
                    del self.categories[category]

            # Remove from tools
            del self.tools[tool_name]

            logger.info(f"Successfully unloaded tool: {tool_name}")

            if self.event_bus:
                self.event_bus.publish("tool_unloaded", tool_name=tool_name)

            return True

        except Exception as e:
            logger.error(f"Error unloading tool {tool_name}: {e}")
            return False

    def reload_tool(self, tool_name: str, **kwargs) -> bool:
        """
        Reload a tool (unload and load again).

        Args:
            tool_name: Name of the tool to reload
            **kwargs: Additional arguments to pass to tool constructor

        Returns:
            True if reload was successful
        """
        logger.info(f"Reloading tool: {tool_name}")

        # Unload the tool
        if not self.unload_tool(tool_name):
            return False

        # Load the tool again
        return self.load_tool(tool_name, **kwargs)

    def get_tool(self, tool_name: str) -> Optional[ToolBase]:
        """
        Get a tool instance by name.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(tool_name)

    async def execute_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            *args: Arguments to pass to the tool
            **kwargs: Keyword arguments to pass to the tool

        Returns:
            Tool execution result
        """
        tool = self.get_tool(tool_name)
        if not tool:
            error_msg = f"Tool '{tool_name}' not found or not loaded"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "tool": tool_name}

        return await tool.run(*args, **kwargs)

    def list_tools(self) -> List[str]:
        """Get a list of all loaded tool names."""
        return list(self.tools.keys())

    def list_tool_classes(self) -> List[str]:
        """Get a list of all registered tool class names."""
        return list(self.tool_classes.keys())

    def list_categories(self) -> Dict[str, List[str]]:
        """Get tools organized by category."""
        return self.categories.copy()

    def get_tool_metadata(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool metadata or None if tool not found
        """
        tool = self.get_tool(tool_name)
        if tool:
            return tool.get_metadata()
        return None

    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all loaded tools."""
        metadata = {}
        for tool_name, tool in self.tools.items():
            metadata[tool_name] = tool.get_metadata()
        return metadata

    def handle_tool_error(self, tool_name: str, error: str, **kwargs):
        """Handle tool errors by attempting to reload the tool."""
        logger.warning(f"Handling error for tool {tool_name}: {error}")

        # Attempt to reload the tool
        if self.reload_tool(tool_name):
            logger.info(f"Successfully recovered tool {tool_name}")
        else:
            logger.error(f"Failed to recover tool {tool_name}")

    def initialize_all_tools(self):
        """Initialize all discovered and registered tools."""
        logger.info("Initializing all tools...")

        # Discover tools first
        discovered_tools = self.discover_tools()

        # Register discovered tools
        for tool_class in discovered_tools:
            self.register_tool_class(tool_class)

        # Load all registered tools
        success_count = 0
        for tool_name in self.tool_classes:
            if self.load_tool(tool_name):
                success_count += 1

        logger.info(f"Initialized {success_count}/{len(self.tool_classes)} tools")

        if self.event_bus:
            self.event_bus.publish(
                "tools_initialized",
                total=len(self.tool_classes),
                successful=success_count,
            )

    def shutdown(self):
        """Shutdown the tool manager and cleanup all tools."""
        logger.info("Shutting down tool manager...")

        # Unload all tools
        for tool_name in list(self.tools.keys()):
            self.unload_tool(tool_name)

        # Clear registrations
        self.tool_classes.clear()
        self.categories.clear()

        logger.info("Tool manager shutdown complete")

        if self.event_bus:
            self.event_bus.publish("tool_manager_shutdown")
