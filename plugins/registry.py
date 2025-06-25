"""
Plugin Registry for Atlas

This module manages the registration and lifecycle of plugins in the Atlas system.
"""

import importlib.util
import inspect
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Type, Any

from plugins.base import PluginBase

logger = logging.getLogger(__name__)

class PluginRegistry:
    """Manages the registration and lifecycle of plugins in Atlas."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        """Initialize the plugin registry.
        
        Args:
            plugins_dir: Directory where plugins are located.
        """
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_classes: Dict[str, Type[PluginBase]] = {}
        self.app_context: Dict[str, Any] = {}
        logger.info("Plugin registry initialized")

    def set_application_context(self, context: Dict[str, Any]) -> None:
        """Set the application context to be passed to plugins during activation.
        
        Args:
            context: Application context dictionary.
        """
        self.app_context = context
        logger.info("Application context set for plugin registry")

    def discover_plugins(self) -> List[str]:
        """Discover all available plugins in the plugins directory.
        
        Returns:
            List of plugin module names discovered.
        """
        discovered = []
        plugins_path = Path(self.plugins_dir)
        if not plugins_path.exists():
            logger.warning(f"Plugins directory {self.plugins_dir} does not exist")
            return discovered

        for item in plugins_path.iterdir():
            if item.is_dir() and not item.name.startswith("__") and (item / "__init__.py").exists():
                discovered.append(item.name)
                logger.info(f"Discovered plugin: {item.name}")
        return discovered

    def register_plugin(self, plugin_name: str, plugin_class: Type[PluginBase] = None) -> bool:
        """Register a plugin by name or class.
        
        Args:
            plugin_name: Name of the plugin module to register.
            plugin_class: Optional plugin class to register directly.
        
        Returns:
            True if registration is successful, False otherwise.
        """
        if plugin_class:
            self.plugin_classes[plugin_name] = plugin_class
            logger.info(f"Registered plugin class: {plugin_name}")
            return True
        
        try:
            module_path = os.path.join(self.plugins_dir, plugin_name)
            spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}", f"{module_path}/__init__.py")
            if spec is None:
                logger.error(f"Failed to find plugin module: {plugin_name}")
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                    plugin_class = obj
                    break

            if plugin_class:
                self.plugin_classes[plugin_name] = plugin_class
                logger.info(f"Registered plugin: {plugin_name}")
                return True
            else:
                logger.error(f"No PluginBase subclass found in {plugin_name}")
                return False
        except Exception as e:
            logger.error(f"Error registering plugin {plugin_name}: {e}")
            return False

    def load_plugin(self, plugin_name: str, config: Optional[dict] = None) -> Optional[PluginBase]:
        """Load and instantiate a plugin.
        
        Args:
            plugin_name: Name of the plugin to load.
            config: Optional configuration dictionary for the plugin.
        
        Returns:
            Plugin instance if successful, None otherwise.
        """
        if plugin_name not in self.plugin_classes:
            if not self.register_plugin(plugin_name):
                return None

        if plugin_name in self.plugins:
            logger.info(f"Plugin already loaded: {plugin_name}")
            return self.plugins[plugin_name]

        try:
            plugin_instance = self.plugin_classes[plugin_name](plugin_name, config)
            if plugin_instance.initialize():
                self.plugins[plugin_name] = plugin_instance
                logger.info(f"Loaded plugin: {plugin_name}")
                if self.app_context:
                    plugin_instance.activate(self.app_context)
                return plugin_instance
            else:
                logger.error(f"Failed to initialize plugin: {plugin_name}")
                return None
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e}")
            return None

    def start_plugin(self, plugin_name: str) -> bool:
        """Start a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to start.
        
        Returns:
            True if start is successful, False otherwise.
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.start()
        return False

    def stop_plugin(self, plugin_name: str) -> bool:
        """Stop a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to stop.
        
        Returns:
            True if stop is successful, False otherwise.
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.stop()
        return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin and clean up resources.
        
        Args:
            plugin_name: Name of the plugin to unload.
        
        Returns:
            True if unloading is successful, False otherwise.
        """
        if plugin_name in self.plugins:
            try:
                if self.plugins[plugin_name].shutdown():
                    del self.plugins[plugin_name]
                    logger.info(f"Unloaded plugin: {plugin_name}")
                    return True
                else:
                    logger.error(f"Failed to shutdown plugin: {plugin_name}")
                    return False
            except Exception as e:
                logger.error(f"Error unloading plugin {plugin_name}: {e}")
                return False
        return True

    def start_all_plugins(self) -> List[str]:
        """Start all loaded plugins.
        
        Returns:
            List of plugin names that were successfully started.
        """
        started = []
        for plugin_name, plugin in self.plugins.items():
            if plugin.start():
                started.append(plugin_name)
                logger.info(f"Started plugin: {plugin_name}")
            else:
                logger.error(f"Failed to start plugin: {plugin_name}")
        return started

    def stop_all_plugins(self) -> List[str]:
        """Stop all loaded plugins.
        
        Returns:
            List of plugin names that were successfully stopped.
        """
        stopped = []
        for plugin_name, plugin in self.plugins.items():
            if plugin.stop():
                stopped.append(plugin_name)
                logger.info(f"Stopped plugin: {plugin_name}")
            else:
                logger.error(f"Failed to stop plugin: {plugin_name}")
        return stopped

    def unload_all_plugins(self) -> List[str]:
        """Unload all loaded plugins.
        
        Returns:
            List of plugin names that were successfully unloaded.
        """
        unloaded = []
        plugin_names = list(self.plugins.keys())
        for plugin_name in plugin_names:
            if self.unload_plugin(plugin_name):
                unloaded.append(plugin_name)
        return unloaded

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get a loaded plugin instance.
        
        Args:
            plugin_name: Name of the plugin to retrieve.
        
        Returns:
            Plugin instance if loaded, None otherwise.
        """
        return self.plugins.get(plugin_name)

    def get_all_plugins(self) -> Dict[str, PluginBase]:
        """Get all loaded plugins.
        
        Returns:
            Dictionary of all loaded plugin instances.
        """
        return self.plugins

    def load_all_plugins(self, config: Optional[Dict[str, dict]] = None) -> List[str]:
        """Load all discovered plugins.
        
        Args:
            config: Optional dictionary of plugin-specific configurations.
        
        Returns:
            List of successfully loaded plugin names.
        """
        config = config or {}
        loaded = []
        for plugin_name in self.discover_plugins():
            plugin_config = config.get(plugin_name, {})
            if self.load_plugin(plugin_name, plugin_config):
                loaded.append(plugin_name)
        return loaded
