from typing import Optional, Dict, Any, List, Type, TypeVar
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from PySide6.QtWidgets import QWidget

# Ensure dataclasses is imported
import dataclasses
assert hasattr(dataclasses, 'field'), "dataclasses.field is not available"

T = TypeVar('T', bound='PluginBase')

@dataclass
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
    tags: List[str] = field(default_factory=list)


class PluginBase(ABC):
    """Base class for all Atlas plugins.

    Attributes:
        active: Plugin activation status
        metadata: Plugin metadata
    """

    metadata: PluginMetadata
    active: bool = False
    settings: Dict[str, Any] = field(default_factory=dict)

    def __init__(self):
        """Initialize the plugin."""
        self.active = False
        self.metadata = self._get_metadata()
        self.settings = self._get_settings()

    @abstractmethod
    def _get_metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata: Plugin metadata
        """
        pass

    @abstractmethod
    def _get_settings(self) -> Dict[str, Any]:
        """Get plugin settings.

        Returns:
            Dict[str, Any]: Plugin settings
        """
        pass

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self.metadata

    def get_settings(self) -> Dict[str, Any]:
        """Get plugin settings."""
        return self.settings

    @abstractmethod
    def activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        """Activate the plugin.

        Args:
            app_context: Application context dictionary
        """
        self.active = True
        self.on_activate(app_context)

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        self.on_deactivate()
        self.active = False

    def on_activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        """Called when plugin is activated.

        Args:
            app_context: Application context dictionary
        """
        pass

    def on_deactivate(self) -> None:
        """Called when plugin is deactivated."""
        pass

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