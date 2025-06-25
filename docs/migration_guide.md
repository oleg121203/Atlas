# Migration Guide for Atlas Plugins

This guide provides instructions for migrating existing plugins to the new architecture introduced in Phase 10 of the Atlas project. The updated architecture centralizes plugin management and introduces lifecycle hooks and a configuration system.

## Overview of Changes

- **Unified Plugin Directory**: All plugins are now consolidated under the `/plugins` directory.
- **Plugin Base Class**: A new abstract base class `PluginBase` is introduced for all plugins to inherit from.
- **Lifecycle Hooks**: Plugins now support lifecycle methods: `initialize()`, `start()`, `stop()`, and `shutdown()`.
- **Configuration System**: Plugins can now use a dedicated configuration system for settings.
- **Plugin Registry**: A central `PluginRegistry` manages plugin discovery, loading, and lifecycle.

## Migration Steps

### 1. Move Plugin to New Directory Structure

Move your plugin from the old `/tools` or other directories to the `/plugins` directory. Ensure the plugin follows the naming convention `<plugin_name>.py`.

**Example**:
```
# Old path: /tools/my_tool.py
# New path: /plugins/my_plugin.py
```

### 2. Update Plugin Class to Inherit from `PluginBase`

Update your plugin class to inherit from `PluginBase` located in `/plugins/base.py`. Implement the required abstract methods.

**Before**:
```python
class MyTool:
    def __init__(self):
        self.name = "My Tool"
    
    def run(self):
        print("Running my tool")
```

**After**:
```python
from plugins.base import PluginBase, PluginMetadata

class MyPlugin(PluginBase):
    def __init__(self, name: str, config=None):
        super().__init__(name, config)
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.name,
            description="A custom plugin for Atlas",
            version="1.0.0",
            author="Your Name"
        )
    
    def _get_settings(self) -> dict:
        return {
            "enabled": True
        }
    
    def execute(self, *args, **kwargs):
        print("Running my plugin")
```

### 3. Implement Lifecycle Hooks

Add the lifecycle methods to manage your plugin's initialization, starting, stopping, and shutdown processes.

**Example**:
```python
class MyPlugin(PluginBase):
    def initialize(self) -> bool:
        print(f"Initializing {self.name}")
        return True
    
    def start(self) -> bool:
        print(f"Starting {self.name}")
        self.activate()
        return True
    
    def stop(self) -> bool:
        print(f"Stopping {self.name}")
        self.deactivate()
        return True
    
    def shutdown(self) -> bool:
        print(f"Shutting down {self.name}")
        return True
```

### 4. Update Configuration Handling

Use the provided configuration system to manage plugin settings. Configurations are loaded from `/config/plugins/<plugin_name>.json` if available.

**Example**:
```python
class MyPlugin(PluginBase):
    def initialize(self) -> bool:
        # Access configuration
        setting_value = self.config.get("setting_key", "default_value")
        print(f"Using setting: {setting_value}")
        return True
```

### 5. Test Plugin Integration

Ensure your plugin integrates with the `PluginRegistry`. The registry will automatically discover and load plugins from the `/plugins` directory. Test the plugin lifecycle by starting and stopping the application to verify that hooks are called correctly.

## Additional Notes

- **Backward Compatibility**: If your plugin needs to support older versions of Atlas, maintain compatibility checks within your code until full migration is complete.
- **Dependencies**: Ensure any dependencies required by your plugin are documented and compatible with the Atlas environment (Python 3.9+, PySide6).
- **UI Integration**: If your plugin provides UI elements, implement `get_widget()` and `settings_widget()` methods to integrate with the Atlas UI.

## Need Help?

If you encounter issues during migration, refer to the updated documentation in `/docs` or reach out to the development team for assistance.

**Note**: This guide will be expanded with more detailed examples and troubleshooting tips as part of the ongoing documentation updates in Phase 10.
