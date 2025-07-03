#!/usr/bin/env python3
"""
Tests for the Atlas Plugin System.
"""

from unittest.mock import Mock, patch

from core.plugin_system import PluginBase, PluginMetadata, PluginSystem


class TestPluginMetadata:
    """Test cases for PluginMetadata."""

    def test_init(self):
        """Test PluginMetadata initialization."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            category="test",
        )

        assert metadata.name == "test_plugin"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test plugin"
        assert metadata.author == "Test Author"
        assert metadata.category == "test"
        assert metadata.dependencies == []

    def test_init_with_dependencies(self):
        """Test PluginMetadata initialization with dependencies."""
        deps = ["dep1", "dep2"]
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            category="test",
            dependencies=deps,
        )

        assert metadata.dependencies == deps

    def test_to_dict(self):
        """Test PluginMetadata to_dict conversion."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            category="test",
        )

        result = metadata.to_dict()

        assert result["name"] == "test_plugin"
        assert result["version"] == "1.0.0"
        assert result["description"] == "Test plugin"
        assert result["author"] == "Test Author"
        assert result["category"] == "test"
        assert result["dependencies"] == []


class TestPluginBase:
    """Test cases for PluginBase."""

    def test_init(self):
        """Test PluginBase initialization."""
        plugin = PluginBase("test_plugin", "1.0.0")

        assert plugin.name == "test_plugin"
        assert plugin.version == "1.0.0"

    def test_abstract_methods(self):
        """Test that abstract methods exist."""
        plugin = PluginBase("test_plugin", "1.0.0")

        # These should not raise NotImplementedError since they have default implementations
        plugin.initialize()
        plugin.shutdown()

        # get_metadata should return a dict
        metadata = plugin.get_metadata()
        assert isinstance(metadata, dict)
        assert metadata["name"] == "test_plugin"
        assert metadata["version"] == "1.0.0"


class MockPlugin(PluginBase):
    """Mock plugin for testing."""

    def __init__(self, name="mock_plugin", version="1.0.0"):
        super().__init__(name, version)
        self.initialized = False
        self.shutdown_called = False

    def initialize(self):
        self.initialized = True

    def shutdown(self):
        self.shutdown_called = True


class TestPluginSystem:
    """Test cases for PluginSystem."""

    def test_init(self):
        """Test PluginSystem initialization."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        assert plugin_system.event_bus == event_bus
        assert plugin_system.loaded_plugins == {}
        assert plugin_system.active_plugins == {}

    def test_list_plugins(self):
        """Test listing plugins."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        # Mock the discover method
        with patch.object(plugin_system, "_discover_plugins") as mock_discover:
            mock_discover.return_value = ["plugin1", "plugin2"]

            plugins = plugin_system.list_plugins()

            assert plugins == ["plugin1", "plugin2"]
            mock_discover.assert_called_once()

    def test_list_active_plugins(self):
        """Test listing active plugins."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        # Add some active plugins
        plugin_system.active_plugins["plugin1"] = Mock()
        plugin_system.active_plugins["plugin2"] = Mock()

        active_plugins = plugin_system.list_active_plugins()

        assert set(active_plugins) == {"plugin1", "plugin2"}

    def test_load_plugin_success(self):
        """Test successful plugin loading."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        # Mock plugin loading
        mock_plugin = MockPlugin()
        with patch.object(plugin_system, "_load_plugin_module") as mock_load:
            mock_load.return_value = mock_plugin

            result = plugin_system.load_plugin("test_plugin")

            assert result is True
            assert "test_plugin" in plugin_system.loaded_plugins
            assert plugin_system.loaded_plugins["test_plugin"] == mock_plugin

    def test_load_plugin_failure(self):
        """Test plugin loading failure."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        # Mock plugin loading to fail
        with patch.object(plugin_system, "_load_plugin_module") as mock_load:
            mock_load.side_effect = Exception("Load failed")

            result = plugin_system.load_plugin("test_plugin")

            assert result is False
            assert "test_plugin" not in plugin_system.loaded_plugins

    def test_activate_plugin_success(self):
        """Test successful plugin activation."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        # Add a loaded plugin
        mock_plugin = MockPlugin()
        plugin_system.loaded_plugins["test_plugin"] = mock_plugin

        result = plugin_system.activate_plugin("test_plugin")

        assert result is True
        assert mock_plugin.initialized is True
        assert "test_plugin" in plugin_system.active_plugins

    def test_activate_plugin_not_loaded(self):
        """Test activating a plugin that's not loaded."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        result = plugin_system.activate_plugin("nonexistent_plugin")

        assert result is False

    def test_deactivate_plugin_success(self):
        """Test successful plugin deactivation."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        # Add an active plugin
        mock_plugin = MockPlugin()
        plugin_system.loaded_plugins["test_plugin"] = mock_plugin
        plugin_system.active_plugins["test_plugin"] = mock_plugin

        result = plugin_system.deactivate_plugin("test_plugin")

        assert result is True
        assert mock_plugin.shutdown_called is True
        assert "test_plugin" not in plugin_system.active_plugins

    def test_deactivate_plugin_not_active(self):
        """Test deactivating a plugin that's not active."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        result = plugin_system.deactivate_plugin("nonexistent_plugin")

        assert result is False

    def test_get_plugin(self):
        """Test getting a plugin instance."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        # Add a loaded plugin
        mock_plugin = MockPlugin()
        plugin_system.loaded_plugins["test_plugin"] = mock_plugin

        result = plugin_system.get_plugin("test_plugin")

        assert result == mock_plugin

    def test_get_plugin_nonexistent(self):
        """Test getting a nonexistent plugin."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        result = plugin_system.get_plugin("nonexistent_plugin")

        assert result is None

    def test_shutdown(self):
        """Test plugin system shutdown."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        # Add some active plugins
        mock_plugin1 = MockPlugin("plugin1")
        mock_plugin2 = MockPlugin("plugin2")
        plugin_system.active_plugins["plugin1"] = mock_plugin1
        plugin_system.active_plugins["plugin2"] = mock_plugin2

        plugin_system.shutdown()

        # All plugins should be shut down
        assert mock_plugin1.shutdown_called is True
        assert mock_plugin2.shutdown_called is True
        assert len(plugin_system.active_plugins) == 0

    def test_event_publishing(self):
        """Test that events are published correctly."""
        event_bus = Mock()
        plugin_system = PluginSystem(event_bus)

        # Test load event
        mock_plugin = MockPlugin()
        with patch.object(plugin_system, "_load_plugin_module") as mock_load:
            mock_load.return_value = mock_plugin

            plugin_system.load_plugin("test_plugin")

            # Check that plugin_loaded event was published
            event_bus.publish.assert_called_with(
                "plugin_loaded", plugin_name="test_plugin", plugin=mock_plugin
            )
