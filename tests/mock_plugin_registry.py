from typing import Dict, Any
from plugins.base import PluginBase

class MockPluginRegistry:
    """Mock PluginRegistry class for testing."""
    
    def __init__(self):
        """Initialize mock plugin registry."""
        self.plugins: Dict[str, PluginBase] = {}
        self.active_plugins: Dict[str, PluginBase] = {}
        
    def register_plugin(self, plugin: PluginBase) -> None:
        """Register a plugin."""
        self.plugins[plugin.get_metadata().name] = plugin
        
    def activate_plugin(self, plugin_name: str) -> None:
        """Activate a plugin."""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.activate()
            self.active_plugins[plugin_name] = plugin
        
    def deactivate_plugin(self, plugin_name: str) -> None:
        """Deactivate a plugin."""
        if plugin_name in self.active_plugins:
            plugin = self.active_plugins[plugin_name]
            plugin.deactivate()
            del self.active_plugins[plugin_name]
        
    def get_plugin_info(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin information."""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            return {
                'name': plugin.get_metadata().name,
                'version': plugin.get_metadata().version,
                'description': plugin.get_metadata().description,
                'author': plugin.get_metadata().author,
                'active': plugin_name in self.active_plugins
            }
        return {}
        
    def get_all_plugins(self) -> Dict[str, PluginBase]:
        """Get all registered plugins."""
        return self.plugins
        
    def get_active_plugins(self) -> Dict[str, PluginBase]:
        """Get all active plugins."""
        return self.active_plugins
