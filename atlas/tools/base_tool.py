import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class ToolMetadata:
    """Metadata describing a tool's capabilities and properties."""

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        author: str = "Atlas",
        category: str = "general",
        capabilities: Optional[List[str]] = None,
        requirements: Optional[List[str]] = None,
        async_supported: bool = True,
    ):
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.category = category
        self.capabilities = capabilities or []
        self.requirements = requirements or []
        self.async_supported = async_supported

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "category": self.category,
            "capabilities": self.capabilities,
            "requirements": self.requirements,
            "async_supported": self.async_supported,
        }


class ToolBase(ABC):
    """
    Enhanced base class for all Atlas tools with comprehensive functionality.

    This class provides:
    - Async/sync execution support
    - Tool chaining capabilities
    - Performance monitoring
    - Error handling and recovery
    - Metadata management
    - Event system integration
    """

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "1.0.0",
        category: str = "general",
        **kwargs,
    ):
        """Initialize the tool with metadata and configuration."""
        self.name = name or self.__class__.__name__.replace("Tool", "").lower()
        self.description = description or f"{self.name} tool"
        self.version = version
        self.category = category

        # Initialize metadata
        self.metadata = ToolMetadata(
            name=self.name,
            description=self.description,
            version=self.version,
            category=self.category,
            capabilities=self.get_capabilities(),
            requirements=self.get_requirements(),
            async_supported=True,
        )

        # Setup logging
        self.logger = logging.getLogger(f"tools.{self.name}")

        # Tool registry for chaining
        self._tool_registry: Optional[Callable[[str], "ToolBase"]] = None

        # Event bus for system integration
        self._event_bus = None

        # Performance tracking
        self._execution_stats = {
            "total_calls": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "last_execution": None,
            "errors": 0,
        }

        self.logger.info(f"Initialized {self.name} tool v{self.version}")

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities this tool provides."""
        return []

    def get_requirements(self) -> List[str]:
        """Return a list of requirements/dependencies for this tool."""
        return []

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Main execution method for the tool. Must be implemented by subclasses.

        Returns:
            Dict containing the execution result and metadata
        """
        pass

    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Enhanced run method with error handling and performance tracking.
        """
        start_time = time.time()
        self._execution_stats["total_calls"] += 1

        try:
            self.logger.debug(
                f"Executing {self.name} with args: {args}, kwargs: {kwargs}"
            )

            # Publish tool execution start event
            if self._event_bus:
                self._event_bus.publish(
                    "tool_execution_start",
                    tool_name=self.name,
                    args=args,
                    kwargs=kwargs,
                )

            # Execute the tool
            result = await self.execute(*args, **kwargs)

            # Ensure result is properly formatted
            if not isinstance(result, dict):
                result = {"result": result, "success": True}
            elif "success" not in result:
                result["success"] = True

            # Add metadata to result
            result["tool"] = self.name
            result["execution_time"] = time.time() - start_time

            # Update stats
            execution_time = result["execution_time"]
            self._execution_stats["total_time"] += execution_time
            self._execution_stats["average_time"] = (
                self._execution_stats["total_time"]
                / self._execution_stats["total_calls"]
            )
            self._execution_stats["last_execution"] = time.time()

            self.logger.debug(
                f"Successfully executed {self.name} in {execution_time:.3f}s"
            )

            # Publish success event
            if self._event_bus:
                self._event_bus.publish(
                    "tool_execution_success",
                    tool_name=self.name,
                    result=result,
                    execution_time=execution_time,
                )

            return result

        except Exception as e:
            # Update error stats
            self._execution_stats["errors"] += 1
            execution_time = time.time() - start_time

            self.logger.error(f"Error executing {self.name}: {e}", exc_info=True)

            # Publish error event
            if self._event_bus:
                self._event_bus.publish(
                    "tool_execution_error",
                    tool_name=self.name,
                    error=str(e),
                    execution_time=execution_time,
                )

            # Return error result
            return {
                "success": False,
                "error": str(e),
                "tool": self.name,
                "execution_time": execution_time,
            }

    def set_tool_registry(self, registry: Callable[[str], "ToolBase"]):
        """Set the tool registry for enabling tool chaining."""
        self._tool_registry = registry
        self.logger.debug(f"Tool registry set for {self.name}")

    def set_event_bus(self, event_bus):
        """Set the event bus for system integration."""
        self._event_bus = event_bus
        self.logger.debug(f"Event bus set for {self.name}")

    async def chain(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute another tool by name and return its result.

        Args:
            tool_name: Name of the tool to execute
            *args: Arguments to pass to the tool
            **kwargs: Keyword arguments to pass to the tool

        Returns:
            The result from the chained tool execution
        """
        if not self._tool_registry:
            raise RuntimeError(
                f"Tool registry not set for {self.name}, cannot chain to {tool_name}"
            )

        try:
            tool = self._tool_registry(tool_name)
            if not tool:
                raise RuntimeError(f"Tool '{tool_name}' not found in registry")

            self.logger.debug(f"Chaining from {self.name} to {tool_name}")
            result = await tool.run(*args, **kwargs)

            self.logger.debug(f"Chain to {tool_name} completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Error chaining to {tool_name}: {e}")
            raise

    def get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata including performance statistics."""
        metadata = self.metadata.to_dict()
        metadata["statistics"] = self._execution_stats.copy()
        return metadata

    def validate_requirements(self) -> bool:
        """
        Validate that all tool requirements are met.

        Returns:
            True if all requirements are satisfied, False otherwise
        """
        # Basic validation - can be overridden by subclasses
        requirements = self.get_requirements()

        for requirement in requirements:
            try:
                # Try to import required modules
                if requirement.startswith("module:"):
                    module_name = requirement.replace("module:", "")
                    __import__(module_name)
                # Add other requirement types as needed
                elif requirement.startswith("command:"):
                    # Check for system commands
                    import shutil

                    command = requirement.replace("command:", "")
                    if not shutil.which(command):
                        self.logger.warning(f"Required command '{command}' not found")
                        return False

            except ImportError:
                self.logger.warning(f"Required module '{requirement}' not available")
                return False
            except Exception as e:
                self.logger.warning(
                    f"Error validating requirement '{requirement}': {e}"
                )
                return False

        return True

    def reset_statistics(self):
        """Reset performance statistics."""
        self._execution_stats = {
            "total_calls": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "last_execution": None,
            "errors": 0,
        }
        self.logger.info(f"Statistics reset for {self.name}")


# Legacy compatibility
class BaseTool(ToolBase):
    """Legacy BaseTool class for backward compatibility."""

    def __init__(self, **kwargs):
        # Convert legacy attributes to new format
        name = kwargs.get("name") or getattr(self, "name", None)
        description = kwargs.get("description") or getattr(self, "description", None)
        version = kwargs.get("version") or getattr(self, "version", "1.0.0")

        super().__init__(name=name, description=description, version=version, **kwargs)

        # Legacy attribute mapping
        self.capabilities = self.get_capabilities()

    def get_capabilities(self) -> List[str]:
        """Get capabilities from legacy capabilities attribute."""
        return getattr(self, "capabilities", [])

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute using legacy run method if available."""
        # Try to call the legacy run method if it exists
        if hasattr(self, "_legacy_run"):
            result = await self._legacy_run(*args, **kwargs)
        else:
            raise NotImplementedError(
                "Tool must implement execute method or provide _legacy_run"
            )

        return result if isinstance(result, dict) else {"result": result}

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
