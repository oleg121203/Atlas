# Atlas Plugins

This directory contains plugins for the Atlas platform. Plugins extend the functionality of Atlas by providing additional tools, agents, UI components, or integrations.

## Structure

- Each plugin should be in its own directory or as a single `.py` file.
- Directory-based plugins must have an `__init__.py` file.
- Plugins can define a main `Plugin` class or a class named after the plugin (e.g., `MyFeaturePlugin` for a plugin named `my_feature`).

## Creating a Plugin

1. Create a new directory or file in this `plugins/` folder.
2. Implement your plugin functionality.
3. Ensure your plugin is discoverable by the `PluginManager`.

## Example Plugin

```python
# plugins/example_plugin.py

__version__ = "1.0.0"
__description__ = "An example plugin for Atlas"

class ExamplePlugin:
    def __init__(self):
        self.name = "Example Plugin"

    def say_hello(self):
        return f"Hello from {self.name}!"
```

Plugins are automatically discovered and can be loaded by the `PluginManager` in Atlas.
