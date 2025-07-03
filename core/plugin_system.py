"""
Standardized plugin architecture for Atlas.

This module defines the core plugin system, including plugin discovery,
loading, lifecycle management, and integration with the application.
"""

import importlib
import inspect
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PluginMetadata:
    """Metadata describing a plugin"""

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str,
        category: str,
        dependencies: Optional[List[str]] = None,
    ):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.category = category
        self.dependencies = dependencies or []

    def to_dict(self) -> Dict[str, str]:
        """Convert metadata to dictionary

        Returns:
            Dict[str, str]: Dictionary representation of the metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "category": self.category,
            "dependencies": self.dependencies,
        }


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

    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active" if self.is_active else "inactive",
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
        plugin_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", self.plugin_dir
        )

        if not os.path.exists(plugin_path):
            logger.warning(f"Plugin directory not found: {plugin_path}")
            return plugin_names

        for entry in os.listdir(plugin_path):
            if os.path.isdir(os.path.join(plugin_path, entry)) and not entry.startswith(
                "__"
            ):
                plugin_names.append(entry)
            elif entry.endswith(".py") and not entry.startswith("__"):
                plugin_names.append(entry[:-3])

        logger.info(f"Discovered plugins: {plugin_names}")
        return plugin_names

    def load_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Load a specific plugin by name."""
        try:
            module = importlib.import_module(f"{self.plugin_dir}.{plugin_name}")

            # Look for any PluginBase subclass in the module
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    inspect.isclass(attr)
                    and issubclass(attr, PluginBase)
                    and attr != PluginBase
                ):
                    plugin_class = attr
                    break

            if plugin_class:
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


class PluginSystem:
    """
    Main plugin system that orchestrates plugin management.

    This class provides a high-level interface for managing plugins,
    including discovery, loading, activation, and lifecycle management.
    """

    def __init__(self, event_bus=None):
        """Initialize the plugin system."""
        self.event_bus = event_bus
        self.registry = PluginRegistry()
        self.plugins: Dict[str, PluginBase] = {}
        self.active_plugins: Dict[str, PluginBase] = {}
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Setup event handlers if event bus is available."""
        if self.event_bus:
            self.event_bus.subscribe("plugin_reload_requested", self.reload_plugin)
            self.event_bus.subscribe("plugin_error", self.handle_plugin_error)

    def initialize(self):
        """Initialize the plugin system and discover available plugins."""
        logger.info("Initializing plugin system")

        # Discover available plugins
        plugin_names = self.registry.discover_plugins()

        # Load all discovered plugins
        for plugin_name in plugin_names:
            self.load_plugin(plugin_name)

        logger.info(f"Plugin system initialized with {len(self.plugins)} plugins")

        if self.event_bus:
            self.event_bus.publish(
                "plugin_system_initialized", plugin_count=len(self.plugins)
            )

    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a plugin.

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            bool: True if loading was successful
        """
        try:
            plugin = self.registry.load_plugin(plugin_name)
            if plugin:
                self.plugins[plugin_name] = plugin
                logger.info(f"Plugin loaded: {plugin_name}")

                if self.event_bus:
                    self.event_bus.publish("plugin_loaded", plugin_name=plugin_name)

                return True
            else:
                logger.error(f"Failed to load plugin: {plugin_name}")
                return False

        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e}")
            if self.event_bus:
                self.event_bus.publish(
                    "plugin_error", plugin_name=plugin_name, error=str(e)
                )
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            bool: True if unloading was successful
        """
        try:
            # Deactivate first if active
            if plugin_name in self.active_plugins:
                self.deactivate_plugin(plugin_name)

            # Remove from loaded plugins
            if plugin_name in self.plugins:
                del self.plugins[plugin_name]
                logger.info(f"Plugin unloaded: {plugin_name}")

                if self.event_bus:
                    self.event_bus.publish("plugin_unloaded", plugin_name=plugin_name)

                return True
            else:
                logger.warning(f"Plugin not loaded: {plugin_name}")
                return False

        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            if self.event_bus:
                self.event_bus.publish(
                    "plugin_error", plugin_name=plugin_name, error=str(e)
                )
            return False

    def activate_plugin(self, plugin_name: str) -> bool:
        """
        Activate a loaded plugin.

        Args:
            plugin_name: Name of the plugin to activate

        Returns:
            bool: True if activation was successful
        """
        if plugin_name not in self.plugins:
            logger.error(f"Plugin not loaded: {plugin_name}")
            return False

        try:
            plugin = self.plugins[plugin_name]
            plugin.initialize()
            self.active_plugins[plugin_name] = plugin

            logger.info(f"Plugin activated: {plugin_name}")

            if self.event_bus:
                self.event_bus.publish("plugin_activated", plugin_name=plugin_name)

            return True

        except Exception as e:
            logger.error(f"Error activating plugin {plugin_name}: {e}")
            if self.event_bus:
                self.event_bus.publish(
                    "plugin_error", plugin_name=plugin_name, error=str(e)
                )
            return False

    def deactivate_plugin(self, plugin_name: str) -> bool:
        """
        Deactivate an active plugin.

        Args:
            plugin_name: Name of the plugin to deactivate

        Returns:
            bool: True if deactivation was successful
        """
        if plugin_name not in self.active_plugins:
            logger.warning(f"Plugin not active: {plugin_name}")
            return True

        try:
            plugin = self.active_plugins[plugin_name]
            plugin.shutdown()
            del self.active_plugins[plugin_name]

            logger.info(f"Plugin deactivated: {plugin_name}")

            if self.event_bus:
                self.event_bus.publish("plugin_deactivated", plugin_name=plugin_name)

            return True

        except Exception as e:
            logger.error(f"Error deactivating plugin {plugin_name}: {e}")
            if self.event_bus:
                self.event_bus.publish(
                    "plugin_error", plugin_name=plugin_name, error=str(e)
                )
            return False

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin (unload and load again).

        Args:
            plugin_name: Name of the plugin to reload

        Returns:
            bool: True if reload was successful
        """
        logger.info(f"Reloading plugin: {plugin_name}")

        was_active = plugin_name in self.active_plugins

        # Unload the plugin
        if not self.unload_plugin(plugin_name):
            return False

        # Load the plugin again
        if not self.load_plugin(plugin_name):
            return False

        # Reactivate if it was active before
        if was_active:
            return self.activate_plugin(plugin_name)

        return True

    def handle_plugin_error(self, plugin_name: str, error: str, **kwargs):
        """Handle plugin errors by attempting to reload the plugin."""
        logger.warning(f"Handling error for plugin {plugin_name}: {error}")

        # Attempt to reload the plugin
        if self.reload_plugin(plugin_name):
            logger.info(f"Successfully recovered plugin {plugin_name}")
        else:
            logger.error(f"Failed to recover plugin {plugin_name}")

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get a plugin instance by name."""
        return self.plugins.get(plugin_name)

    def list_plugins(self) -> List[str]:
        """Get a list of all loaded plugin names."""
        return list(self.plugins.keys())

    def list_active_plugins(self) -> List[str]:
        """Get a list of all active plugin names."""
        return list(self.active_plugins.keys())

    def get_plugin_status(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get the status of a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Dict containing plugin status information
        """
        if plugin_name not in self.plugins:
            return {"status": "not_loaded", "active": False}

        plugin = self.plugins[plugin_name]
        return {
            "status": "loaded",
            "active": plugin_name in self.active_plugins,
            "metadata": plugin.get_metadata(),
        }

    def shutdown(self):
        """Shutdown the plugin system and all active plugins."""
        logger.info("Shutting down plugin system")

        # Deactivate all active plugins
        for plugin_name in list(self.active_plugins.keys()):
            self.deactivate_plugin(plugin_name)

        # Clear all plugins
        self.plugins.clear()
        self.active_plugins.clear()

        logger.info("Plugin system shutdown complete")

        if self.event_bus:
            self.event_bus.publish("plugin_system_shutdown")
