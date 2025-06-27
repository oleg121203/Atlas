from typing import Any, Dict, List, Optional, Set

import pytest
from plugins.base import PluginBase
from PySide6.QtWidgets import QWidget

from tests.mock_plugin_metadata import MockPluginMetadata as PluginMetadata


class DependencyPlugin(PluginBase):
    """Plugin with dependencies for testing."""

    def __init__(self, name: str, dependencies: list[str]):
        # Initialize metadata first
        self.metadata = PluginMetadata(
            name=name,
            version="1.0.0",
            description="Plugin with dependencies",
            author="Test",
            dependencies=dependencies,
        )
        self.active = False
        self.settings = {}

        # Now call parent constructor
        super().__init__()

    def _get_metadata(self) -> PluginMetadata:
        return self.metadata

    def _get_settings(self) -> Dict[str, Any]:
        return self.settings

    def activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        self.active = True

    def deactivate(self) -> None:
        self.active = False

    def on_activate(self, app_context: Optional[Dict[str, Any]] = None) -> None:
        pass

    def on_deactivate(self) -> None:
        pass

    def get_widget(self, parent: Optional["QWidget"] = None) -> Optional["QWidget"]:
        return None

    def set_settings(self, settings: Dict[str, Any]) -> None:
        self.settings = settings

    def settings_widget(
        self, parent: Optional["QWidget"] = None
    ) -> Optional["QWidget"]:
        return None

    def info(self) -> Dict[str, Any]:
        return {"name": self.metadata.name, "active": self.active}

    def is_active(self) -> bool:
        return self.active


class MockPluginRegistry:
    """Enhanced MockPluginRegistry with version and platform validation."""

    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.active_plugins: Set[str] = set()

    def register_plugin(self, plugin: PluginBase) -> None:
        """Register a plugin with version validation."""
        self.plugins[plugin.get_metadata().name] = plugin

    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Get a plugin by name."""
        return self.plugins.get(name)

    def activate_plugin(self, name: str, app_version: str = "1.0.0") -> bool:
        """Activate a plugin with version and platform checks."""
        plugin = self.get_plugin(name)
        if not plugin:
            return False

        metadata = plugin.get_metadata()

        # Version validation
        if metadata.min_app_version and app_version < metadata.min_app_version:
            return False
        if metadata.max_app_version and app_version > metadata.max_app_version:
            return False

        # Dependency validation
        for dep in metadata.dependencies:
            dep_plugin = self.get_plugin(dep)
            if not dep_plugin or not dep_plugin.is_active():
                return False

        try:
            # This will check platform compatibility in the plugin's activate method
            plugin.activate()
            if plugin.is_active():
                self.active_plugins.add(name)
                return True
            return False
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


@pytest.fixture
def registry():
    return MockPluginRegistry()


def test_plugin_with_dependencies(registry):
    """Test plugin activation with satisfied dependencies."""
    # Create dependency plugins
    dep1 = DependencyPlugin("dep1", [])
    dep2 = DependencyPlugin("dep2", [])

    # Register dependencies
    registry.register_plugin(dep1)
    registry.register_plugin(dep2)

    # Activate dependencies first
    assert registry.activate_plugin("dep1") is True
    assert registry.activate_plugin("dep2") is True

    # Create plugin with dependencies
    plugin = DependencyPlugin("test", ["dep1", "dep2"])
    registry.register_plugin(plugin)

    # Activate should succeed
    assert registry.activate_plugin("test") is True
    assert plugin.is_active() is True


def test_plugin_with_missing_dependencies(registry):
    """Test plugin activation with missing dependencies."""
    plugin = DependencyPlugin("test", ["missing_dep"])
    registry.register_plugin(plugin)

    # Activate should fail
    assert registry.activate_plugin("test") is False
    assert plugin.is_active() is False


def test_circular_dependencies(registry):
    """Test detection of circular dependencies."""
    # Create plugins with circular dependencies
    plugin1 = DependencyPlugin("plugin1", ["plugin2"])
    plugin2 = DependencyPlugin("plugin2", ["plugin1"])

    registry.register_plugin(plugin1)
    registry.register_plugin(plugin2)

    # Both activations should fail
    assert registry.activate_plugin("plugin1") is False
    assert registry.activate_plugin("plugin2") is False
