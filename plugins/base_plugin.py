"""
Base Plugin System for Atlas

This module provides the foundation for creating plugins that integrate
with the active provider in the chat system.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
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
    """Manages plugin loading, initialization, and execution.
    
    Attributes:
        plugins (Dict[str, BasePlugin]): Registered plugins by name
        active_provider (Optional[Any]): Current active provider
        logger (logging.Logger): Plugin manager logger
    """
    
    def __init__(self):
        """Initialize the PluginManager."""
        self.plugins: Dict[str, BasePlugin] = {}
        self.active_provider: Optional[Any] = None
        self.logger = logging.getLogger("plugin_manager")
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Register a new plugin.
        
        Args:
            plugin (BasePlugin): Plugin instance to register
            
        Returns:
            bool: True if registration was successful
        """
        try:
            metadata = plugin.get_metadata()
            if not isinstance(metadata, PluginMetadata):
                raise ValueError("Plugin must return valid PluginMetadata")
                
            if metadata.name in self.plugins:
                self.logger.warning(f"Overwriting existing plugin: {metadata.name}")
            
            self.plugins[metadata.name] = plugin
            self.logger.info(f"Registered plugin: {metadata.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register plugin: {e}", exc_info=True)
            return False
    
    def set_provider(self, provider: Any) -> None:
        """Set the active provider for all plugins.
        
        Args:
            provider (Any): Provider instance to set
        """
        self.active_provider = provider
        for plugin in self.plugins.values():
            plugin.set_provider(provider)
        self.logger.info("Provider set for all plugins")
    
    def initialize_plugin(self, plugin_name: str) -> bool:
        """Initialize a specific plugin.
        
        Args:
            plugin_name (str): Name of the plugin to initialize
            
        Returns:
            bool: True if initialization was successful
        """
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            if not plugin.active_provider:
                self.logger.error(f"No active provider set for plugin: {plugin_name}")
                return False
                
            if plugin.initialize(plugin.active_provider):
                plugin.is_initialized = True
                self.logger.info(f"Plugin initialized: {plugin_name}")
                return True
            else:
                self.logger.error(f"Failed to initialize plugin: {plugin_name}")
                return False
        except Exception as e:
            self.logger.error(f"Error initializing plugin {plugin_name}: {e}", exc_info=True)
            return False
    
    def execute_plugin(self, plugin_name: str, command: str, **kwargs) -> PluginResult:
        """Execute a command on a specific plugin.
        
        Args:
            plugin_name (str): Name of the plugin
            command (str): Command to execute
            **kwargs: Additional arguments for the command
            
        Returns:
            PluginResult: Result of the command execution
        """
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
            result = plugin.execute(command, **kwargs)
            if not isinstance(result, PluginResult):
                self.logger.error(f"Plugin {plugin_name} returned invalid result type")
                return PluginResult(
                    success=False,
                    error="Plugin returned invalid result type"
                )
            return result
        except Exception as e:
            self.logger.error(f"Error executing plugin {plugin_name}: {e}", exc_info=True)
            return PluginResult(
                success=False,
                error=str(e)
            )
    
    def get_available_plugins(self) -> List[str]:
        """Get list of available plugin names.
        
        Returns:
            List[str]: List of registered plugin names
        """
        return list(self.plugins.keys())
    
    def get_plugin_help(self, plugin_name: str) -> str:
        """Get help information for a specific plugin.
        
        Args:
            plugin_name (str): Name of the plugin
            
        Returns:
            str: Help information or error message
        """
        if plugin_name not in self.plugins:
            return f"Plugin not found: {plugin_name}"
        
        return self.plugins[plugin_name].get_help()
    
    def cleanup_all(self) -> None:
        """Clean up all registered plugins."""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up plugin {plugin.metadata.name}: {e}")
        self.logger.info("All plugins cleaned up")
    
    def validate_plugin(self, plugin: BasePlugin) -> bool:
        """Validate a plugin instance.
        
        Args:
            plugin (BasePlugin): Plugin instance to validate
            
        Returns:
            bool: True if plugin is valid
        """
        try:
            metadata = plugin.get_metadata()
            if not isinstance(metadata, PluginMetadata):
                return False
                
            if not metadata.name or not metadata.version:
                return False
                
            if not hasattr(plugin, 'initialize') or not callable(plugin.initialize):
                return False
                
            return True
        except Exception:
            return False
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """Get metadata for a specific plugin.
        
        Args:
            plugin_name (str): Name of the plugin
            
        Returns:
            Optional[PluginMetadata]: Plugin metadata or None if not found
        """
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].get_metadata()
        return None
    
    def get_plugin_commands(self, plugin_name: str) -> List[str]:
        """Get list of available commands for a plugin.
        
        Args:
            plugin_name (str): Name of the plugin
            
        Returns:
            List[str]: List of available commands
        """
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].get_commands()
        return []

# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance.
    
    Returns:
        PluginManager: Singleton instance of PluginManager
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager

def register_plugin(plugin: BasePlugin) -> bool:
    """Register a plugin with the global manager.
    
    Args:
        plugin (BasePlugin): Plugin instance to register
        
    Returns:
        bool: True if registration was successful
    """
    return get_plugin_manager().register_plugin(plugin)

def set_active_provider(provider: Any) -> None:
    """Set the active provider for all plugins.
    
    Args:
        provider (Any): Provider instance to set
    """
    get_plugin_manager().set_provider(provider)

def execute_plugin_command(plugin_name: str, command: str, **kwargs) -> PluginResult:
    """Execute a command on a plugin.
    
    Args:
        plugin_name (str): Name of the plugin
        command (str): Command to execute
        **kwargs: Additional arguments for the command
        
    Returns:
        PluginResult: Result of the command execution
    """
    return get_plugin_manager().execute_plugin(plugin_name, command, **kwargs) 

def validate_plugin(plugin: BasePlugin) -> bool:
    """Validate a plugin instance.
    
    Args:
        plugin (BasePlugin): Plugin instance to validate
        
    Returns:
        bool: True if plugin is valid
    """
    return get_plugin_manager().validate_plugin(plugin)

def get_plugin_metadata(plugin_name: str) -> Optional[PluginMetadata]:
    """Get metadata for a plugin.
    
    Args:
        plugin_name (str): Name of the plugin
        
    Returns:
        Optional[PluginMetadata]: Plugin metadata or None
    """
    return get_plugin_manager().get_plugin_metadata(plugin_name)

def get_plugin_commands(plugin_name: str) -> List[str]:
    """Get available commands for a plugin.
    
    Args:
        plugin_name (str): Name of the plugin
        
    Returns:
        List[str]: List of available commands
    """
    return get_plugin_manager().get_plugin_commands(plugin_name)