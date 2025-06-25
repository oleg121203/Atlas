"""
Standardized plugin architecture for Atlas.

This module defines the core plugin system, including plugin discovery,
loading, lifecycle management, and integration with the application.
"""
import os
import importlib
import logging
from typing import Dict, List, Type, Optional

logger = logging.getLogger(__name__)

class PluginBase:
    """Base class for all Atlas plugins."""

    def __init__(self, name: str, version: str):
        """Initialize the plugin with basic metadata."""
        self.name = name
        self.version = version
        self.is_active = False

    def initialize(self) -> None:
        """Initialize the plugin. Override in subclasses."""
        logger.info(f"Initializing plugin: {self.name} v{self.version}")
        self.is_active = True

    def shutdown(self) -> None:
        """Shut down the plugin. Override in subclasses."""
        logger.info(f"Shutting down plugin: {self.name}")
        self.is_active = False

    def get_metadata(self) -> Dict[str, str]:
        """Return plugin metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active" if self.is_active else "inactive"
        }

class PluginRegistry:
    """Manages plugin discovery, loading, and lifecycle."""

    def __init__(self, plugin_dir: str = "plugins"):
        """Initialize the plugin registry."""
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_dir = plugin_dir

    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugin directory."""
        plugin_names = []
        plugin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', self.plugin_dir)
        
        if not os.path.exists(plugin_path):
            logger.warning(f"Plugin directory not found: {plugin_path}")
            return plugin_names

        for entry in os.listdir(plugin_path):
            if os.path.isdir(os.path.join(plugin_path, entry)) and not entry.startswith('__'):
                plugin_names.append(entry)
            elif entry.endswith('.py') and not entry.startswith('__'):
                plugin_names.append(entry[:-3])

        logger.info(f"Discovered plugins: {plugin_names}")
        return plugin_names

    def load_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Load a specific plugin by name."""
        try:
            module = importlib.import_module(f"{self.plugin_dir}.{plugin_name}")
            plugin_class = getattr(module, f"{plugin_name.capitalize()}Plugin", None)
            if plugin_class and issubclass(plugin_class, PluginBase):
                plugin_instance = plugin_class(plugin_name, "1.0.0")
                self.plugins[plugin_name] = plugin_instance
                logger.info(f"Loaded plugin: {plugin_name}")
                return plugin_instance
            else:
                logger.warning(f"No valid plugin class found for: {plugin_name}")
                return None
        except ImportError as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return None

    def activate_plugin(self, plugin_name: str) -> bool:
        """Activate a loaded plugin."""
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].initialize()
                logger.info(f"Activated plugin: {plugin_name}")
                return True
            except Exception as e:
                logger.error(f"Error activating plugin {plugin_name}: {e}")
                return False
        return False

    def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate a loaded plugin."""
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].shutdown()
                logger.info(f"Deactivated plugin: {plugin_name}")
                return True
            except Exception as e:
                logger.error(f"Error deactivating plugin {plugin_name}: {e}")
                return False
        return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get a plugin instance by name."""
        return self.plugins.get(plugin_name)

    def get_all_plugins(self) -> Dict[str, PluginBase]:
        """Get all loaded plugins."""
        return self.plugins

# Global plugin registry instance
PLUGIN_REGISTRY = PluginRegistry()
