"""
Plugin System for Atlas

This module provides the plugin infrastructure for Atlas, allowing
dynamic loading and execution of plugins that integrate with the
active provider in the chat system.
"""

from .base_plugin import (
    BasePlugin,
    PluginMetadata,
    PluginResult,
    PluginManager,
    get_plugin_manager,
    register_plugin,
    set_active_provider,
    execute_plugin_command
)

# Register built-in plugins
def register_builtin_plugins():
    """Register all built-in plugins."""
    plugin_manager = get_plugin_manager()

# Export main functions
__all__ = [
    'BasePlugin',
    'PluginMetadata', 
    'PluginResult',
    'PluginManager',
    'get_plugin_manager',
    'register_plugin',
    'set_active_provider',
    'execute_plugin_command',
    'register_builtin_plugins'
]
