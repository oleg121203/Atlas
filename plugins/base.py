"""
Base Plugin Class for Atlas

This module defines the base class for all plugins in the Atlas system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from PySide6.QtWidgets import QWidget

import logging
import dataclasses

logger = logging.getLogger(__name__)

# Ensure dataclasses is imported
assert hasattr(dataclasses, 'field'), "dataclasses.field is not available"

@dataclasses.dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    description: str
    version: str
    author: str
    dependencies: List[str]
    min_app_version: str
    max_app_version: Optional[str] = None
    icon: Optional[str] = None
    tags: List[str] = dataclasses.field(default_factory=list)


class PluginBase(ABC):
    """Abstract base class for all Atlas plugins."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin with a name and optional configuration.
        
        Args:
            name: The name of the plugin.
            config: Optional configuration dictionary for the plugin.
        """
        self.name = name
        self.config = config or {}
        self.active = False
        self.metadata = self._get_metadata()
        self.settings = self._get_settings()
        logger.info(f"Plugin {name} initialized")

    @abstractmethod
    def _get_metadata(self) -> PluginMetadata:
        """Define plugin metadata.
        
        Returns:
            PluginMetadata object containing plugin information.
        """
        pass

    @abstractmethod
    def _get_settings(self) -> Dict[str, Any]:
        """Define plugin settings.
        
        Returns:
            Dictionary of plugin settings.
        """
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the main functionality of the plugin.
        
        This method must be implemented by all derived classes.
        """
        pass

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self.metadata

    def get_settings(self) -> Dict[str, Any]:
        """Get plugin settings."""
        return self.settings

    def activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        """Activate the plugin.

        Args:
            app_context: Optional application context dictionary.
        """
        self.active = True
        logger.info(f"Plugin {self.name} activated")

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        self.active = False
        logger.info(f"Plugin {self.name} deactivated")

    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the plugin.
        
        Returns:
            Dictionary representing the current state of the plugin.
        """
        return {
            "active": self.active,
            "settings": self.settings,
            "metadata": self.metadata
        }

    def get_metadata_dict(self) -> Dict[str, Any]:
        """Return metadata about the plugin.
        
        Returns:
            A dictionary containing metadata about the plugin such as name, version, etc.
        """
        return {
            "name": self.name,
            "version": getattr(self, "version", "1.0.0"),
            "description": getattr(self, "description", "No description available")
        }

    def configure(self, config: Dict[str, Any]) -> None:
        """Update the plugin configuration.
        
        Args:
            config: A dictionary with configuration settings.
        """
        self.config.update(config)
        logger.info(f"Plugin {self.name} configuration updated")

    def initialize(self) -> bool:
        """Initialize any resources or setup required by the plugin.
        
        Returns:
            True if initialization is successful, False otherwise.
        """
        logger.info(f"Plugin {self.name} initialization started")
        return True

    def start(self) -> bool:
        """Start the plugin's main operation or background tasks.
        
        Returns:
            True if start is successful, False otherwise.
        """
        logger.info(f"Plugin {self.name} starting")
        self.activate()
        return True

    def stop(self) -> bool:
        """Stop the plugin's main operation or background tasks.
        
        Returns:
            True if stop is successful, False otherwise.
        """
        logger.info(f"Plugin {self.name} stopping")
        self.deactivate()
        return True

    def shutdown(self) -> bool:
        """Cleanup any resources used by the plugin.
        
        Returns:
            True if shutdown is successful, False otherwise.
        """
        logger.info(f"Plugin {self.name} shutdown started")
        return True

    def get_widget(self, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """Get the main widget for UI integration.

        Returns:
            Optional[QWidget]: Main widget or None
        """
        return None

    def set_settings(self, settings: Dict[str, Any]) -> None:
        """Set plugin settings.

        Args:
            settings: New settings dictionary
        """
        self.settings = settings

    def settings_widget(self, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """Get settings widget for editing.

        Args:
            parent: Parent widget

        Returns:
            Optional[QWidget]: Settings widget or None
        """
        return None

    def info(self) -> Dict[str, Any]:
        """Get plugin information.

        Returns:
            Dict[str, Any]: Plugin information
        """
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "version": self.metadata.version,
            "author": self.metadata.author,
            "active": self.active,
            "settings": self.settings,
            "metadata": self.metadata
        }

    def on_activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        """Called when plugin is activated.

        Args:
            app_context: Application context dictionary
        """
        pass

    def on_deactivate(self) -> None:
        """Called when plugin is deactivated."""
        pass