"""Plugin ecosystem for Atlas.

This module manages the plugin system for the Atlas application, allowing for
extensible functionality through modular plugins.
"""

__all__ = ["PluginManager", "PluginInterface"]

# Import plugin components for easy access
from .plugin_interface import PluginInterface
from .plugin_manager import PluginManager
