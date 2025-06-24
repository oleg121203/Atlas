import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable

class BaseTool:
    """
    Base class for all Atlas tools, providing async support, metadata, chaining, and logging.
    """
    name: str = "base_tool"
    description: str = "Base class for Atlas tools."
    capabilities: List[str] = []
    version: str = "1.0"

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metadata = {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "version": self.version,
        }
        self._tool_registry: Optional[Callable[[str], Any]] = None  # For chaining

    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Main async entry point for the tool. Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the async run method.")

    def set_tool_registry(self, registry: Callable[[str], Any]):
        """
        Set a registry or lookup function to enable chaining with other tools.
        """
        self._tool_registry = registry

    async def chain(self, tool_name: str, *args, **kwargs) -> Any:
        """
        Call another tool by name, passing arguments. Returns the result.
        """
        if not self._tool_registry:
            raise RuntimeError("Tool registry not set for chaining.")
        tool = self._tool_registry(tool_name)
        if hasattr(tool, "run") and asyncio.iscoroutinefunction(tool.run):
            return await tool.run(*args, **kwargs)
        elif hasattr(tool, "run"):
            return tool.run(*args, **kwargs)
        else:
            raise RuntimeError(f"Tool '{tool_name}' does not have a run method.")

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return tool metadata.
        """
        return self.metadata

    def log_usage(self, action: str, details: Optional[Dict[str, Any]] = None):
        self.logger.info(f"[TOOL USAGE] {self.name}: {action} | {details or {}}")

    # Example method
    async def example(self) -> Dict[str, Any]:
        self.log_usage("example")
        await asyncio.sleep(0.1)
        return {"status": "success", "message": "Example method executed."} 