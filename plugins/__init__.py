"""Plugin system for Atlas application.

This module handles plugin discovery, loading, and management for Atlas, allowing for extensible
functionality through a plugin architecture.
"""

import importlib
import logging
import os
import pkgutil
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Plugin discovery paths
DEFAULT_PLUGIN_PATHS = [
    os.path.join(os.path.dirname(__file__), "builtin"),  # Built-in plugins
    os.path.join(os.path.expanduser("~"), ".atlas", "plugins"),  # User plugins
]

# Registry for loaded plugins
_loaded_plugins: Dict[str, Any] = {}


class PluginBase:
    """Base class for all Atlas plugins.

    All plugins must inherit from this class and implement
    the required methods.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        """Initialize plugin with name and version.

        Args:
            name: The name of the plugin
            version: The version of the plugin
        """
        self.name = name
        self.version = version
        self.enabled = False

    def initialize(self) -> bool:
        """Initialize the plugin.

        Returns:
            True if initialization was successful, False otherwise
        """
        raise NotImplementedError("Plugins must implement initialize()")

    def start(self) -> bool:
        """Start the plugin.

        Returns:
            True if startup was successful, False otherwise
        """
        raise NotImplementedError("Plugins must implement start()")

    def stop(self) -> None:
        """Stop the plugin."""
        raise NotImplementedError("Plugins must implement stop()")

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information.

        Returns:
            Dictionary containing plugin metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
        }


def discover_plugins(search_paths: Optional[List[str]] = None) -> List[str]:
    """Discover available plugins in the specified search paths.

    Args:
        search_paths: List of paths to search for plugins. Uses DEFAULT_PLUGIN_PATHS if None.

    Returns:
        List of discovered plugin module names
    """
    if search_paths is None:
        search_paths = DEFAULT_PLUGIN_PATHS

    discovered = []

    for path in search_paths:
        if not os.path.exists(path):
            continue

        try:
            # Add path to sys.path if not already there
            if path not in sys.path:
                sys.path.insert(0, path)

            # Discover modules in the path
            for _, name, _ in pkgutil.iter_modules([path]):
                if name not in discovered:
                    discovered.append(name)
                    logger.debug(f"Discovered plugin: {name}")
        except Exception as e:
            logger.error(f"Error discovering plugins in {path}: {e}")

    return discovered


def load_plugin(
    plugin_name: str, search_paths: Optional[List[str]] = None
) -> Optional[PluginBase]:
    """Load a specific plugin by name.

    Args:
        plugin_name: Name of the plugin to load
        search_paths: List of paths to search for the plugin

    Returns:
        Loaded plugin instance or None if loading failed
    """
    if plugin_name in _loaded_plugins:
        return _loaded_plugins[plugin_name]

    try:
        # Try to import the plugin module
        module = importlib.import_module(plugin_name)

        # Look for a plugin class that inherits from PluginBase
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, PluginBase)
                and attr != PluginBase
            ):
                plugin_class = attr
                break

        if plugin_class is None:
            logger.error(f"No valid plugin class found in module {plugin_name}")
            return None

        # Create plugin instance
        plugin_instance = plugin_class(plugin_name)
        _loaded_plugins[plugin_name] = plugin_instance

        logger.info(f"Successfully loaded plugin: {plugin_name}")
        return plugin_instance

    except Exception as e:
        logger.error(f"Failed to load plugin {plugin_name}: {e}")
        return None


def get_loaded_plugins() -> Dict[str, PluginBase]:
    """Get all currently loaded plugins.

    Returns:
        Dictionary of plugin name to plugin instance
    """
    return _loaded_plugins.copy()


def unload_plugin(plugin_name: str) -> bool:
    """Unload a specific plugin.

    Args:
        plugin_name: Name of the plugin to unload

    Returns:
        True if plugin was successfully unloaded, False otherwise
    """
    if plugin_name not in _loaded_plugins:
        logger.warning(f"Plugin {plugin_name} is not loaded")
        return False

    try:
        plugin = _loaded_plugins[plugin_name]
        plugin.stop()
        del _loaded_plugins[plugin_name]
        logger.info(f"Successfully unloaded plugin: {plugin_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to unload plugin {plugin_name}: {e}")
        return False


__all__ = [
    "discover_plugins",
    "load_plugin",
    "DEFAULT_PLUGIN_PATHS",
    "PluginBase",
    "get_loaded_plugins",
    "unload_plugin",
]
