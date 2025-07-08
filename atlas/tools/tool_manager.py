"""
Tool Manager for Atlas

This module manages the registration, discovery and execution of tools.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ToolManager:
    """
    Manages tool registration and execution.

    This class is responsible for:
    - Registering tools and their handlers
    - Executing tools with provided arguments
    - Managing tool metadata and capabilities
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        logger.info("ToolManager initialized")

    def register_tool(
        self,
        name: str,
        handler: Callable,
        description: str,
        required_args: Optional[List[str]] = None,
        optional_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a new tool with the manager.

        Args:
            name: Unique name of the tool
            handler: Function that implements the tool
            description: Human-readable description of what the tool does
            required_args: List of required argument names
            optional_args: Dictionary of optional arguments and their default values
        """
        self.tools[name] = {
            "handler": handler,
            "description": description,
            "required_args": required_args or [],
            "optional_args": optional_args or {},
        }
        logger.info(f"Registered tool: {name}")

    def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """
        Execute a tool with the provided arguments.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool

        Returns:
            Result from the tool execution

        Raises:
            KeyError: If tool_name is not registered
            ValueError: If required arguments are missing
        """
        if tool_name not in self.tools:
            raise KeyError(f"Tool not found: {tool_name}")

        tool = self.tools[tool_name]

        # Validate required arguments
        missing_args = set(tool["required_args"]) - set(kwargs.keys())
        if missing_args:
            raise ValueError(
                f"Missing required arguments for {tool_name}: {missing_args}"
            )

        # Add default values for optional arguments
        for arg, default in tool["optional_args"].items():
            kwargs.setdefault(arg, default)

        try:
            result = tool["handler"](**kwargs)
            logger.debug(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise

    def initialize(self):
        """
        Initialize the tool manager and discover tools.
        """
        # Placeholder for tool discovery logic
        logger.info("ToolManager initialized and tools discovered.")

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a registered tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with tool metadata or None if tool not found
        """
        return self.tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self.tools.keys())

    def get_tool_description(self, tool_name: str) -> Optional[str]:
        """Get human-readable description of a tool."""
        tool = self.tools.get(tool_name)
        return tool["description"] if tool else None
