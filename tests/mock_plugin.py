from typing import Dict, Any, Optional
from plugins.base import PluginBase
from tests.mock_plugin_metadata import MockPluginMetadata as PluginMetadata

class TestPlugin(PluginBase):
    """Mock plugin class for testing."""
    
    def __init__(self):
        """Initialize mock plugin."""
        self.metadata = PluginMetadata(
            name=f"test_plugin_{id(self)}",
            version="1.0.0",
            description="Test plugin for load testing",
            author="Test",
            dependencies=[]
        )
        self.active = False
        
    def _get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self.metadata
        
    def _get_settings(self) -> Dict[str, Any]:
        """Get plugin settings."""
        return {}
        
    def activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        """Activate the plugin."""
        self.active = True
        self.on_activate(app_context)
        
    def deactivate(self) -> None:
        """Deactivate the plugin."""
        self.on_deactivate()
        self.active = False
        
    def on_activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        """Called when plugin is activated."""
        pass
        
    def on_deactivate(self) -> None:
        """Called when plugin is deactivated."""
        pass
        
    def get_widget(self, parent: Optional["QWidget"] = None) -> Optional["QWidget"]:
        """Get the main widget for UI integration."""
        return None
        
    def is_active(self) -> bool:
        """Check if plugin is active."""
        return self.active
