## 4. Plugin System Enhancement

### 4.1. Plugin API

```python
class PluginBase:
    """Base class for all Atlas plugins."""

    def __init__(self, app):
        self.app = app  # Access to core API
        self.config = {}
        self.version = "1.0.0"

    @property
    def name(self):
        """Unique plugin name."""
        raise NotImplementedError

    @property
    def description(self):
        """Plugin description."""
        return ""

    def initialize(self):
        """Plugin initialization."""
        pass

    def cleanup(self):
        """Resource release."""
        pass

    def get_widget(self, parent=None):
        """Returns a widget for UI if the plugin has a visual interface."""
        return None

    def get_settings_widget(self, parent=None):
        """Returns the plugin settings widget."""
        return None

    def on_event(self, event_type, data):
        """Event handler from the core system."""
        pass
```

### 4.2. Plugin Registration System

```python
class PluginRegistry:
    """Plugin registry with dependency and versioning support."""

    def __init__(self, app):
        self.app = app
        self.plugins = {}
        self.active_plugins = {}

    def discover_plugins(self):
        """Search and register available plugins."""
        # Code to search for plugins in the plugins/ directory

    def activate_plugin(self, plugin_name):
        """Activate a plugin and its dependencies."""
        # Code to activate the plugin
        # 1. Check if plugin exists in registry
        # 2. Resolve and activate dependencies first
        # 3. Initialize plugin
        # 4. Register event listeners
        # 5. Add to active_plugins dictionary

    def deactivate_plugin(self, plugin_name):
        """Deactivate a plugin."""
        # Code to deactivate the plugin
        # 1. Check if plugin is active
        # 2. Unregister event listeners
        # 3. Call cleanup method
        # 4. Remove from active_plugins dictionary

    def get_plugin_by_name(self, plugin_name):
        """Get plugin instance by name."""
        return self.active_plugins.get(plugin_name)
```
