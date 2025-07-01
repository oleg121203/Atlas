import pytest

from plugins.base import PluginBase
from tests.mock_plugin_metadata import MockPluginMetadata as PluginMetadata
from tests.test_plugin_dependencies import MockPluginRegistry


class VersionTestPlugin(PluginBase):
    """Plugin for version compatibility testing."""

    def __init__(
        self, name: str, version: str, min_app: str = None, max_app: str = None
    ):
        self.metadata = PluginMetadata(
            name=name,
            version=version,
            description="Version test plugin",
            author="Test",
            dependencies=[],
            min_app_version=min_app,
            max_app_version=max_app,
        )
        self.active = False
        super().__init__()

    def _get_metadata(self):
        return self.metadata

    def _get_settings(self):
        return {}

    def activate(self, ctx=None):
        self.active = True

    def deactivate(self):
        self.active = False

    def is_active(self):
        return self.active


@pytest.mark.version
def test_version_compatibility():
    """Test successful activation with compatible versions."""
    registry = MockPluginRegistry()
    plugin = VersionTestPlugin("test", "1.2.3", "1.0.0", "2.0.0")
    registry.register_plugin(plugin)

    # Should activate successfully with app version 1.5.0
    assert registry.activate_plugin("test", app_version="1.5.0") is True


@pytest.mark.version
def test_min_version_failure():
    """Test activation fails when app version is too old."""
    registry = MockPluginRegistry()
    plugin = VersionTestPlugin("test", "1.2.3", "1.5.0", "2.0.0")
    registry.register_plugin(plugin)

    # Should fail with app version 1.4.9
    assert registry.activate_plugin("test", app_version="1.4.9") is False


@pytest.mark.version
def test_max_version_failure():
    """Test activation fails when app version is too new."""
    registry = MockPluginRegistry()
    plugin = VersionTestPlugin("test", "1.2.3", "1.0.0", "1.9.9")
    registry.register_plugin(plugin)

    # Should fail with app version 2.0.0
    assert registry.activate_plugin("test", app_version="2.0.0") is False
