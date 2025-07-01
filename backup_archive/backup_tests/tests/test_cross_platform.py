import sys
from unittest.mock import patch

import pytest

from plugins.base import PluginBase
from tests.mock_plugin_metadata import MockPluginMetadata as PluginMetadata
from tests.test_plugin_dependencies import MockPluginRegistry


class PlatformTestPlugin(PluginBase):
    """Plugin for cross-platform compatibility testing."""

    def __init__(self, name: str, supported_platforms: list = None):
        self.metadata = PluginMetadata(
            name=name,
            version="1.0.0",
            description="Platform test plugin",
            author="Test",
            dependencies=[],
        )
        self.active = False
        self.supported_platforms = supported_platforms or ["darwin", "linux", "win32"]
        super().__init__()

    def _get_metadata(self):
        return self.metadata

    def _get_settings(self):
        return {}

    def activate(self, ctx=None):
        if sys.platform in self.supported_platforms:
            self.active = True
        return self.active

    def deactivate(self):
        self.active = False

    def is_active(self):
        return self.active


@pytest.mark.platform
def test_platform_compatibility():
    """Test plugin activation on supported platforms."""
    registry = MockPluginRegistry()

    # Test macOS compatibility
    with patch("sys.platform", "darwin"):
        mac_plugin = PlatformTestPlugin("mac_test", ["darwin"])
        registry.register_plugin(mac_plugin)
        assert registry.activate_plugin("mac_test") is True
        assert mac_plugin.is_active() is True

    # Test Linux compatibility
    with patch("sys.platform", "linux"):
        linux_plugin = PlatformTestPlugin("linux_test", ["linux"])
        registry.register_plugin(linux_plugin)
        assert registry.activate_plugin("linux_test") is True
        assert linux_plugin.is_active() is True

    # Test Windows compatibility
    with patch("sys.platform", "win32"):
        win_plugin = PlatformTestPlugin("win_test", ["win32"])
        registry.register_plugin(win_plugin)
        assert registry.activate_plugin("win_test") is True
        assert win_plugin.is_active() is True


@pytest.mark.platform
def test_unsupported_platform():
    """Test plugin activation fails on unsupported platforms."""
    registry = MockPluginRegistry()

    with patch("sys.platform", "darwin"):
        win_only_plugin = PlatformTestPlugin("win_only", ["win32"])
        registry.register_plugin(win_only_plugin)
        assert registry.activate_plugin("win_only") is False
        assert win_only_plugin.is_active() is False


@pytest.mark.platform
def test_multi_platform_support():
    """Test plugin activation on multiple supported platforms."""
    registry = MockPluginRegistry()
    multi_plugin = PlatformTestPlugin("multi", ["darwin", "linux"])
    registry.register_plugin(multi_plugin)

    with patch("sys.platform", "darwin"):
        assert registry.activate_plugin("multi") is True
        assert multi_plugin.is_active() is True
    multi_plugin.deactivate()

    with patch("sys.platform", "linux"):
        assert registry.activate_plugin("multi") is True
        assert multi_plugin.is_active() is True
    multi_plugin.deactivate()

    with patch("sys.platform", "win32"):
        assert registry.activate_plugin("multi") is False
        assert multi_plugin.is_active() is False
