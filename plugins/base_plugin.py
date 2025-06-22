"""
Base Plugin System for Atlas

This module provides the foundation for creating plugins that integrate
with the active provider in the chat system.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: str
    category: str
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PluginResult:
    """Result from a plugin operation."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BasePlugin(ABC):
    """Base class for all Atlas plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metadata = self.get_metadata()
        self.is_initialized = False
        self.active_provider = None
        self.logger = logging.getLogger(f"plugin.{self.metadata.name}")
        
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self, provider: Any) -> bool:
        """Initialize the plugin with the active provider."""
        pass
    
    @abstractmethod
    def execute(self, command: str, **kwargs) -> PluginResult:
        """Execute a plugin command."""
        pass
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        self.is_initialized = False
        self.active_provider = None
        self.logger.info(f"Plugin {self.metadata.name} cleaned up")
    
    def get_commands(self) -> List[str]:
        """Get list of available commands."""
        return []
    
    def get_help(self) -> str:
        """Get help information for the plugin."""
        return f"Plugin: {self.metadata.name}\n{self.metadata.description}"
    
    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        return True
    
    def set_provider(self, provider: Any) -> None:
        """Set the active provider for the plugin."""
        self.active_provider = provider
        self.logger.info(f"Provider set for plugin {self.metadata.name}")

class PluginManager:
    """Manages plugin loading and execution."""
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.active_provider = None
        self.logger = logging.getLogger("plugin_manager")
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Register a plugin."""
        try:
            metadata = plugin.get_metadata()
            self.plugins[metadata.name] = plugin
            self.logger.info(f"Registered plugin: {metadata.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register plugin: {e}")
            return False
    
    def set_provider(self, provider: Any) -> None:
        """Set the active provider for all plugins."""
        self.active_provider = provider
        for plugin in self.plugins.values():
            plugin.set_provider(provider)
        self.logger.info("Provider set for all plugins")
    
    def initialize_plugin(self, plugin_name: str) -> bool:
        """Initialize a specific plugin."""
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            if plugin.initialize(self.active_provider):
                plugin.is_initialized = True
                self.logger.info(f"Plugin initialized: {plugin_name}")
                return True
            else:
                self.logger.error(f"Failed to initialize plugin: {plugin_name}")
                return False
        except Exception as e:
            self.logger.error(f"Error initializing plugin {plugin_name}: {e}")
            return False
    
    def execute_plugin(self, plugin_name: str, command: str, **kwargs) -> PluginResult:
        """Execute a command on a specific plugin."""
        if plugin_name not in self.plugins:
            return PluginResult(
                success=False,
                error=f"Plugin not found: {plugin_name}"
            )
        
        plugin = self.plugins[plugin_name]
        
        if not plugin.is_initialized:
            if not self.initialize_plugin(plugin_name):
                return PluginResult(
                    success=False,
                    error=f"Failed to initialize plugin: {plugin_name}"
                )
        
        try:
            return plugin.execute(command, **kwargs)
        except Exception as e:
            self.logger.error(f"Error executing plugin {plugin_name}: {e}")
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    def get_available_plugins(self) -> List[str]:
        """Get list of available plugin names."""
        return list(self.plugins.keys())
    
    def get_plugin_help(self, plugin_name: str) -> str:
        """Get help for a specific plugin."""
        if plugin_name not in self.plugins:
            return f"Plugin not found: {plugin_name}"
        
        return self.plugins[plugin_name].get_help()
    
    def cleanup_all(self) -> None:
        """Clean up all plugins."""
        for plugin in self.plugins.values():
            plugin.cleanup()
        self.logger.info("All plugins cleaned up")

# Global plugin manager instance
_plugin_manager = None

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager

def register_plugin(plugin: BasePlugin) -> bool:
    """Register a plugin with the global manager."""
    return get_plugin_manager().register_plugin(plugin)

def set_active_provider(provider: Any) -> None:
    """Set the active provider for all plugins."""
    get_plugin_manager().set_provider(provider)

def execute_plugin_command(plugin_name: str, command: str, **kwargs) -> PluginResult:
    """Execute a command on a plugin."""
    return get_plugin_manager().execute_plugin(plugin_name, command, **kwargs) 