# How to Create a Tool for Atlas

This guide will walk you through creating a custom tool for the Atlas system.

## Overview

Atlas tools are executable components that provide specific functionality to the system. Unlike plugins, tools are designed to perform discrete actions and can be called from various parts of the application, including the chat system, workflows, and other plugins.

## Tool Structure

Every tool must inherit from the `BaseTool` class and implement the required interface.

### Basic Tool Template

```python
"""
My Custom Tool for Atlas
"""

import logging
from typing import Dict, Any

from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class MyCustomTool(BaseTool):
    """
    A custom tool that demonstrates the Atlas tool system.
    
    This tool should inherit from BaseTool and implement the required methods.
    """

    def __init__(self):
        super().__init__()
        self.category = "general"  # Tool category

    def get_name(self) -> str:
        """Return the tool name."""
        return "my_custom_tool"

    def get_description(self) -> str:
        """Return a description of what this tool does."""
        return "A custom tool for demonstrating Atlas tool system capabilities"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Return the parameters this tool accepts.
        
        Returns:
            Dict describing the tool's parameters using JSON Schema format
        """
        return {
            "action": {
                "type": "string",
                "description": "The action to perform",
                "required": True,
                "enum": ["greet", "calculate", "status"]
            },
            "name": {
                "type": "string",
                "description": "Name for greeting (required for 'greet' action)",
                "required": False
            },
            "numbers": {
                "type": "array",
                "description": "Numbers to calculate (required for 'calculate' action)",
                "items": {"type": "number"},
                "required": False
            }
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Parameters for the tool execution
            
        Returns:
            Dict containing the execution result
        """
        try:
            action = kwargs.get("action")
            
            if not action:
                return {
                    "success": False,
                    "error": "Action parameter is required",
                    "available_actions": ["greet", "calculate", "status"]
                }

            if action == "greet":
                return await self._handle_greet(kwargs)
            elif action == "calculate":
                return await self._handle_calculate(kwargs)
            elif action == "status":
                return await self._handle_status(kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": ["greet", "calculate", "status"]
                }
                
        except Exception as e:
            logger.error(f"Error in {self.get_name()}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _handle_greet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greeting action."""
        name = params.get("name", "World")
        return {
            "success": True,
            "message": f"Hello, {name}! Greetings from {self.get_name()}",
            "action": "greet"
        }

    async def _handle_calculate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calculation action."""
        numbers = params.get("numbers", [])
        
        if not numbers:
            return {
                "success": False,
                "error": "Numbers array is required for calculate action"
            }
        
        if not all(isinstance(n, (int, float)) for n in numbers):
            return {
                "success": False,
                "error": "All numbers must be numeric"
            }
        
        result = {
            "success": True,
            "action": "calculate",
            "input": numbers,
            "sum": sum(numbers),
            "average": sum(numbers) / len(numbers),
            "min": min(numbers),
            "max": max(numbers),
            "count": len(numbers)
        }
        
        return result

    async def _handle_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status action."""
        return {
            "success": True,
            "action": "status",
            "tool_name": self.get_name(),
            "status": "operational",
            "version": "1.0.0",
            "category": self.category
        }
```

## Tool File Structure

Tools should be placed in the `tools/` directory as individual Python files:

```
tools/
├── my_custom_tool.py    # Your tool implementation
├── base_tool.py         # Base class (already exists)
├── tool_manager.py      # Tool manager (already exists)
└── other_tools.py       # Other existing tools
```

## Example Tools

### 1. File Operations Tool

```python
from tools.base_tool import BaseTool
import os
import json

class FileOperationsTool(BaseTool):
    """Tool for basic file operations."""
    
    def get_name(self) -> str:
        return "file_operations"
    
    def get_description(self) -> str:
        return "Perform basic file operations like read, write, list directory"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "enum": ["read", "write", "list", "exists"],
                "required": True
            },
            "path": {
                "type": "string",
                "description": "File or directory path",
                "required": True
            },
            "content": {
                "type": "string",
                "description": "Content to write (for write operation)",
                "required": False
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        operation = kwargs.get("operation")
        path = kwargs.get("path")
        
        if operation == "read":
            try:
                with open(path, 'r') as f:
                    content = f.read()
                return {"success": True, "content": content}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif operation == "write":
            content = kwargs.get("content", "")
            try:
                with open(path, 'w') as f:
                    f.write(content)
                return {"success": True, "message": f"Written to {path}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif operation == "list":
            try:
                files = os.listdir(path)
                return {"success": True, "files": files}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif operation == "exists":
            exists = os.path.exists(path)
            return {"success": True, "exists": exists}
```

### 2. Web Request Tool

```python
from tools.base_tool import BaseTool
import aiohttp
import json

class WebRequestTool(BaseTool):
    """Tool for making HTTP requests."""
    
    def get_name(self) -> str:
        return "web_request"
    
    def get_description(self) -> str:
        return "Make HTTP requests to web services"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "url": {
                "type": "string",
                "description": "URL to request",
                "required": True
            },
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE"],
                "default": "GET",
                "required": False
            },
            "headers": {
                "type": "object",
                "description": "HTTP headers",
                "required": False
            },
            "data": {
                "type": "object",
                "description": "Request body data",
                "required": False
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        url = kwargs.get("url")
        method = kwargs.get("method", "GET")
        headers = kwargs.get("headers", {})
        data = kwargs.get("data")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, headers=headers, json=data
                ) as response:
                    content = await response.text()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "content": content,
                        "headers": dict(response.headers)
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### 3. System Information Tool

```python
from tools.base_tool import BaseTool
import platform
import psutil
import datetime

class SystemInfoTool(BaseTool):
    """Tool for getting system information."""
    
    def get_name(self) -> str:
        return "system_info"
    
    def get_description(self) -> str:
        return "Get system information including OS, CPU, memory, and disk usage"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "info_type": {
                "type": "string",
                "enum": ["all", "os", "cpu", "memory", "disk"],
                "default": "all",
                "required": False
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        info_type = kwargs.get("info_type", "all")
        result = {"success": True}
        
        if info_type in ["all", "os"]:
            result["os"] = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        
        if info_type in ["all", "cpu"]:
            result["cpu"] = {
                "count": psutil.cpu_count(),
                "percent": psutil.cpu_percent(interval=1),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            }
        
        if info_type in ["all", "memory"]:
            memory = psutil.virtual_memory()
            result["memory"] = {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            }
        
        if info_type in ["all", "disk"]:
            disk = psutil.disk_usage('/')
            result["disk"] = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        
        return result
```

## Tool Lifecycle

1. **Discovery**: The tool manager scans the `tools/` directory for tool classes
2. **Registration**: Tool classes are registered with the tool manager
3. **Loading**: Tool instances are created when needed
4. **Execution**: Tools are executed with specific parameters
5. **Cleanup**: Tools can be unloaded if needed

## Using Tools

### From Code

```python
from core.application import AtlasApplication

app = AtlasApplication()
tool_manager = app.tool_manager

# Execute a tool
result = await tool_manager.execute_tool(
    "my_custom_tool",
    action="greet",
    name="Atlas User"
)

print(result)  # {"success": True, "message": "Hello, Atlas User! ..."}
```

### From Chat System

Tools can be called from the chat system using natural language:

```
User: "Calculate the sum of 1, 2, 3, 4, 5"
System: [Uses my_custom_tool with action="calculate", numbers=[1,2,3,4,5]]
Result: {"success": True, "sum": 15, "average": 3.0, ...}
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
async def execute(self, **kwargs) -> Dict[str, Any]:
    try:
        # Tool logic here
        return {"success": True, "result": result}
    except ValueError as e:
        return {"success": False, "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Unexpected error in {self.get_name()}: {e}")
        return {"success": False, "error": "Internal tool error"}
```

### 2. Input Validation

Validate parameters before processing:

```python
def validate_parameters(self, **kwargs) -> Dict[str, Any]:
    required_params = ["action"]
    missing = [p for p in required_params if p not in kwargs]
    
    if missing:
        return {
            "success": False,
            "error": f"Missing required parameters: {missing}"
        }
    
    return {"success": True}
```

### 3. Async Operations

Use async/await for I/O operations:

```python
async def execute(self, **kwargs) -> Dict[str, Any]:
    # For file operations
    async with aiofiles.open(file_path, 'r') as f:
        content = await f.read()
    
    # For HTTP requests
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    
    return {"success": True, "data": data}
```

### 4. Logging

Use proper logging levels:

```python
import logging
logger = logging.getLogger(__name__)

async def execute(self, **kwargs) -> Dict[str, Any]:
    logger.info(f"Executing {self.get_name()} with params: {kwargs}")
    logger.debug(f"Processing data: {data}")
    logger.warning(f"Deprecated parameter used: {param}")
    logger.error(f"Operation failed: {error}")
```

### 5. Configuration

Support configuration for your tools:

```python
class ConfigurableTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
    
    def load_config(self):
        # Load from environment variables
        return {
            "api_key": os.getenv("API_KEY"),
            "timeout": int(os.getenv("TIMEOUT", "30")),
            "retry_count": int(os.getenv("RETRY_COUNT", "3"))
        }
```

## Testing Tools

Create comprehensive tests for your tools:

```python
import unittest
from unittest.mock import patch, AsyncMock
import asyncio
from tools.my_custom_tool import MyCustomTool

class TestMyCustomTool(unittest.TestCase):
    def setUp(self):
        self.tool = MyCustomTool()
    
    def test_get_name(self):
        self.assertEqual(self.tool.get_name(), "my_custom_tool")
    
    def test_get_description(self):
        description = self.tool.get_description()
        self.assertIsInstance(description, str)
        self.assertTrue(len(description) > 0)
    
    def test_get_parameters(self):
        params = self.tool.get_parameters()
        self.assertIn("action", params)
        self.assertTrue(params["action"]["required"])
    
    async def test_execute_greet(self):
        result = await self.tool.execute(action="greet", name="Test")
        self.assertTrue(result["success"])
        self.assertIn("Hello, Test", result["message"])
    
    async def test_execute_invalid_action(self):
        result = await self.tool.execute(action="invalid")
        self.assertFalse(result["success"])
        self.assertIn("Unknown action", result["error"])
    
    def test_async_execution(self):
        # Helper to run async tests
        async def run_test():
            result = await self.tool.execute(action="status")
            self.assertTrue(result["success"])
        
        asyncio.run(run_test())
```

## Integration with Other Systems

### Plugin Integration

Tools can be used by plugins:

```python
class MyPlugin(PluginBase):
    def __init__(self):
        super().__init__("my_plugin", "1.0.0")
        self.tool_manager = None  # Will be injected
    
    async def process_data(self, data):
        # Use a tool from the plugin
        result = await self.tool_manager.execute_tool(
            "file_operations",
            operation="write",
            path="/tmp/data.json",
            content=json.dumps(data)
        )
        return result
```

### Event System Integration

Tools can publish events:

```python
class EventTool(BaseTool):
    def __init__(self, event_bus=None):
        super().__init__()
        self.event_bus = event_bus
    
    async def execute(self, **kwargs):
        result = await self.process_data(kwargs)
        
        # Publish event when done
        if self.event_bus:
            self.event_bus.publish("tool_completed", {
                "tool": self.get_name(),
                "result": result
            })
        
        return result
```

## Debugging

### Common Issues

1. **Tool not discovered**: Ensure the tool file is in `tools/` directory and the class inherits from `BaseTool`
2. **Import errors**: Check that all dependencies are installed
3. **Async errors**: Make sure to use `await` for async operations
4. **Parameter validation**: Verify that parameter schemas match the expected format

### Debug Mode

Enable debug logging to see detailed tool execution:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# You'll see detailed logs about tool discovery, loading, and execution
```

## Next Steps

- Look at existing tools in the `tools/` directory for more examples
- Read the [Plugin Creation Guide](plugin_creation_guide.md) for creating plugins
- Check the [Architecture Overview](architecture_overview.md) for system design
- Review the [API Documentation](../api/tools.md) for technical details

## Resources

- [Tool Manager API Reference](../api/tools.md)
- [Base Tool Class Documentation](../api/tools.md#basetool)
- [Example Tools Repository](../examples/tools/)
- [Testing Guidelines](testing_guidelines.md)
