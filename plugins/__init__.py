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

from .gmail_plugin import GmailPlugin, register_gmail_plugin
from .unified_browser_plugin import UnifiedBrowserPlugin, register_unified_browser_plugin

# Auto-register built-in plugins
def register_builtin_plugins():
    """Register all built-in plugins."""
    register_gmail_plugin()
    register_unified_browser_plugin()

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
    'register_builtin_plugins',
    'GmailPlugin',
    'UnifiedBrowserPlugin'
]
