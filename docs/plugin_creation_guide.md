# How to Create a Plugin for Atlas

This guide will walk you through creating a custom plugin for the Atlas system.

## Overview

Atlas plugins extend the functionality of the application by providing modular, reusable components. Each plugin is a self-contained module that can be loaded, activated, and deactivated at runtime.

## Plugin Structure

Every plugin must inherit from the `PluginBase` class and implement the required interface.

### Basic Plugin Template

```python
"""
My Custom Plugin for Atlas
"""

import logging
from typing import Dict, Any

from core.plugin_system import PluginBase

logger = logging.getLogger(__name__)


class MyCustomPlugin(PluginBase):
    """
    A custom plugin that demonstrates the Atlas plugin system.
    
    This plugin should inherit from PluginBase and implement the required methods.
    """

    def __init__(self):
        super().__init__("my_custom_plugin", "1.0.0")
        self.is_running = False

    def initialize(self) -> None:
        """
        Initialize the plugin.
        
        This method is called when the plugin is activated.
        Set up any resources, connections, or initial state here.
        """
        logger.info(f"Initializing {self.name}")
        
        # Your initialization code here
        self.is_running = True
        
        logger.info(f"Plugin {self.name} initialized successfully")

    def shutdown(self) -> None:
        """
        Shutdown the plugin.
        
        This method is called when the plugin is deactivated.
        Clean up any resources, close connections, etc.
        """
        logger.info(f"Shutting down {self.name}")
        
        # Your cleanup code here
        self.is_running = False
        
        logger.info(f"Plugin {self.name} shutdown complete")

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return plugin metadata.
        
        This method should return a dictionary containing information
        about the plugin.
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": "A custom plugin for demonstrating Atlas plugin system",
            "author": "Your Name",
            "category": "demo",
            "dependencies": [],
            "status": "running" if self.is_running else "stopped"
        }

    def execute_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a plugin command.
        
        Args:
            command: The command to execute
            **kwargs: Additional parameters
            
        Returns:
            Dict containing the result of the command
        """
        if not self.is_running:
            return {"error": "Plugin not initialized", "success": False}
            
        if command == "status":
            return {
                "success": True,
                "status": "running",
                "message": f"Plugin {self.name} is active"
            }
        elif command == "hello":
            name = kwargs.get("name", "World")
            return {
                "success": True,
                "message": f"Hello, {name}! From {self.name} plugin"
            }
        else:
            return {
                "error": f"Unknown command: {command}",
                "success": False,
                "available_commands": ["status", "hello"]
            }
```

## Plugin Directory Structure

Create your plugin in the `plugins/` directory:

```
plugins/
├── my_custom_plugin/
│   ├── __init__.py      # Plugin entry point
│   ├── plugin.py        # Main plugin class (optional)
│   ├── config.py        # Plugin configuration (optional)
│   └── resources/       # Plugin resources (optional)
│       ├── data.json
│       └── templates/
```

### Plugin Entry Point (`__init__.py`)

```python
"""
My Custom Plugin Entry Point
"""

from .my_custom_plugin import MyCustomPlugin

# The plugin system will look for a class that inherits from PluginBase
# Make sure to export your main plugin class
__all__ = ["MyCustomPlugin"]
```

## Example Plugins

### 1. Simple Status Plugin

```python
from core.plugin_system import PluginBase
import psutil

class SystemStatusPlugin(PluginBase):
    def __init__(self):
        super().__init__("system_status", "1.0.0")
    
    def initialize(self):
        # No initialization needed for this simple plugin
        pass
    
    def get_metadata(self):
        return {
            "name": self.name,
            "version": self.version,
            "description": "Provides system status information",
            "author": "Atlas Team",
            "category": "system"
        }
    
    def get_cpu_usage(self):
        return {"cpu_percent": psutil.cpu_percent()}
    
    def get_memory_usage(self):
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        }
```

### 2. Plugin with Configuration

```python
from core.plugin_system import PluginBase
import os
import json

class ConfigurablePlugin(PluginBase):
    def __init__(self):
        super().__init__("configurable_plugin", "1.0.0")
        self.config = {}
    
    def initialize(self):
        self.load_config()
    
    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"enabled": True, "interval": 60}
    
    def get_metadata(self):
        return {
            "name": self.name,
            "version": self.version,
            "description": "A plugin with configuration support",
            "config": self.config
        }
```

## Plugin Lifecycle

1. **Discovery**: The plugin system scans the `plugins/` directory
2. **Loading**: The plugin class is imported and instantiated
3. **Activation**: `initialize()` method is called
4. **Runtime**: Plugin provides functionality to the system
5. **Deactivation**: `shutdown()` method is called

## Best Practices

### 1. Error Handling

Always use try-catch blocks in your plugin methods:

```python
def initialize(self):
    try:
        # Your initialization code
        self.setup_resources()
        logger.info(f"Plugin {self.name} initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize plugin {self.name}: {e}")
        raise
```

### 2. Logging

Use the standard Python logging module:

```python
import logging
logger = logging.getLogger(__name__)

def my_method(self):
    logger.info("Starting operation")
    logger.debug("Debug information")
    logger.warning("Warning message")
    logger.error("Error occurred")
```

### 3. Configuration

Store configuration in a separate file:

```python
def load_config(self):
    config_file = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_file, 'r') as f:
        self.config = json.load(f)
```

### 4. Dependencies

If your plugin has external dependencies, list them in metadata:

```python
def get_metadata(self):
    return {
        "name": self.name,
        "dependencies": ["requests", "beautifulsoup4"],
        # ... other metadata
    }
```

## Testing Your Plugin

Create tests for your plugin:

```python
import unittest
from unittest.mock import Mock, patch
from plugins.my_custom_plugin import MyCustomPlugin

class TestMyCustomPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyCustomPlugin()
    
    def test_initialization(self):
        self.plugin.initialize()
        self.assertTrue(self.plugin.is_running)
    
    def test_shutdown(self):
        self.plugin.initialize()
        self.plugin.shutdown()
        self.assertFalse(self.plugin.is_running)
    
    def test_metadata(self):
        metadata = self.plugin.get_metadata()
        self.assertEqual(metadata["name"], "my_custom_plugin")
        self.assertEqual(metadata["version"], "1.0.0")
```

## Loading and Managing Plugins

### Using the Plugin System

```python
from core.application import AtlasApplication

app = AtlasApplication()
plugin_system = app.plugin_system

# Load a plugin
success = plugin_system.load_plugin("my_custom_plugin")

# Activate a plugin
if success:
    plugin_system.activate_plugin("my_custom_plugin")

# Get plugin instance
plugin = plugin_system.get_plugin("my_custom_plugin")

# Execute plugin command
if plugin:
    result = plugin.execute_command("hello", name="Atlas")
    print(result)  # {"success": True, "message": "Hello, Atlas! From my_custom_plugin plugin"}
```

## Debugging

### Common Issues

1. **Plugin not found**: Check that the plugin directory is in `plugins/` and has an `__init__.py`
2. **Import errors**: Ensure all dependencies are installed
3. **Plugin won't activate**: Check the `initialize()` method for exceptions

### Debug Mode

Enable debug logging to see detailed plugin loading information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

- Look at the existing demo plugins in `plugins/git_integration/`, `plugins/system_monitor/`, and `plugins/spotify_control/`
- Read the [Tool Creation Guide](tool_creation_guide.md) for creating tools
- Check the [Architecture Overview](architecture_overview.md) for system design

## Resources

- [Plugin System API Reference](../api/plugins.md)
- [Core System Documentation](../api/core.md)
- [Example Plugins Repository](../examples/plugins/)
