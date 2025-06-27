from typing import Any, Dict, List, Optional, Set

from plugins.base import PluginBase


class MockPluginRegistry:
    """Mock PluginRegistry class for testing."""

    def __init__(self):
        """Initialize mock plugin registry."""
        self.plugins: Dict[str, PluginBase] = {}
        self.active_plugins: Set[str] = set()

    def register_plugin(self, plugin: PluginBase) -> None:
        """Register a plugin."""
        self.plugins[plugin.get_metadata().name] = plugin

    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Get a plugin by name."""
        return self.plugins.get(name)

    def activate_plugin(self, name: str) -> bool:
        """Activate a plugin."""
        plugin = self.get_plugin(name)
        if not plugin:
            return False

        try:
            plugin.activate()
            self.active_plugins.add(name)
            return True
        except Exception:
            return False

    def deactivate_plugin(self, name: str) -> bool:
        """Deactivate a plugin."""
        plugin = self.get_plugin(name)
        if not plugin:
            return False

        try:
            plugin.deactivate()
            self.active_plugins.discard(name)
            return True
        except Exception:
            return False

    def reload_all_plugins(self) -> None:
        """Reload all plugins."""
        self.plugins.clear()
        self.active_plugins.clear()

    def list_plugins(self) -> List[PluginBase]:
        """Get list of all loaded plugins."""
        return list(self.plugins.values())

    def get_active_plugins(self) -> List[PluginBase]:
        """Get list of active plugins."""
        return [
            self.plugins[name] for name in self.active_plugins if name in self.plugins
        ]

    def get_plugin_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a plugin."""
        plugin = self.get_plugin(name)
        if not plugin:
            return {}
        return plugin.info()
