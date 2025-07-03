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
        plugin_system = PluginSystem([])

        assert plugin_system.plugins == {}
        assert plugin_system.active_plugins == {}

    def test_list_plugins(self):
        """Test listing plugins."""
        plugin_system = PluginSystem([])
        plugins = plugin_system.list_plugins()
        assert isinstance(plugins, list)

    def test_list_active_plugins(self):
        """Test listing active plugins."""
        plugin_system = PluginSystem([])
        active_plugins = plugin_system.list_active_plugins()
        assert isinstance(active_plugins, list)
        assert len(active_plugins) == 0

    def test_load_plugin_success(self):
        """Test successful plugin loading."""
        plugin_system = PluginSystem([])
        # We can't test real loading without a real plugin, so we'll mock the metadata
        plugin_system.plugin_metadata["test_plugin"] = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            category="test",
        )
        with patch("core.plugin_system.PluginSystem._load_plugin_module") as mock_load:
            mock_plugin_instance = Mock(spec=PluginBase)
            mock_plugin_instance.get_metadata.return_value = PluginMetadata(
                name="test_plugin",
                version="1.0.0",
                description="Test",
                author="Test",
                category="test",
            )
            mock_load.return_value = mock_plugin_instance
            result = plugin_system.load_plugin("test_plugin")
            assert result is True
            assert "test_plugin" in plugin_system.plugins

    def test_load_plugin_failure(self):
        """Test plugin loading failure."""
        plugin_system = PluginSystem([])
        with patch("core.plugin_system.importlib.import_module") as mock_import:
            mock_import.side_effect = ImportError("Module not found")
            result = plugin_system.load_plugin("nonexistent_plugin")
            assert result is False
            assert "nonexistent_plugin" not in plugin_system.plugins

    def test_activate_plugin_success(self):
        """Test successful plugin activation."""
        plugin_system = PluginSystem([])
        # Add a loaded plugin
        mock_plugin = MockPlugin()
        plugin_system.plugins["test_plugin"] = mock_plugin

        result = plugin_system.activate_plugin("test_plugin")

        assert result is True
        assert "test_plugin" in plugin_system.active_plugins

    def test_activate_plugin_not_loaded(self):
        """Test activating a plugin that's not loaded."""
        plugin_system = PluginSystem([])

        result = plugin_system.activate_plugin("nonexistent_plugin")

        assert result is False

    def test_deactivate_plugin_success(self):
        """Test successful plugin deactivation."""
        plugin_system = PluginSystem([])
        # Add an active plugin
        mock_plugin = MockPlugin()
        plugin_system.plugins["test_plugin"] = mock_plugin
        plugin_system.active_plugins["test_plugin"] = mock_plugin

        result = plugin_system.deactivate_plugin("test_plugin")

        assert result is True
        assert "test_plugin" not in plugin_system.active_plugins

    def test_deactivate_plugin_not_active(self):
        """Test deactivating a plugin that's not active."""
        plugin_system = PluginSystem([])

        result = plugin_system.deactivate_plugin("nonexistent_plugin")

        assert result is False

    def test_get_plugin(self):
        """Test getting a plugin instance."""
        plugin_system = PluginSystem([])
        # Add a loaded plugin
        mock_plugin = MockPlugin()
        plugin_system.plugins["test_plugin"] = mock_plugin

        result = plugin_system.get_plugin("test_plugin")

        assert result == mock_plugin

    def test_get_plugin_nonexistent(self):
        """Test getting a nonexistent plugin."""
        plugin_system = PluginSystem([])

        result = plugin_system.get_plugin("nonexistent_plugin")

        assert result is None

    def test_shutdown(self):
        """Test plugin system shutdown."""
        plugin_system = PluginSystem([])
        # Add some active plugins
        mock_plugin1 = MockPlugin("plugin1")
        mock_plugin2 = MockPlugin("plugin2")
        plugin_system.plugins["plugin1"] = mock_plugin1
        plugin_system.plugins["plugin2"] = mock_plugin2
        plugin_system.active_plugins["plugin1"] = mock_plugin1
        plugin_system.active_plugins["plugin2"] = mock_plugin2

        plugin_system.shutdown()

        assert plugin_system.active_plugins == {}
        assert mock_plugin1.shutdown_called
        assert mock_plugin2.shutdown_called

    def test_event_publishing(self):
        """Test that events are published correctly."""
        plugin_system = PluginSystem([])
        plugin_system.plugin_metadata["test_plugin"] = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            category="test",
        )
        with patch("core.plugin_system.PluginSystem._load_plugin_module") as mock_load:
            mock_plugin_instance = Mock(spec=PluginBase)
            mock_plugin_instance.get_metadata.return_value = PluginMetadata(
                name="test_plugin",
                version="1.0.0",
                description="Test",
                author="Test",
                category="test",
            )
            mock_load.return_value = mock_plugin_instance
            plugin_system.load_plugin("test_plugin")
            plugin_system.activate_plugin("test_plugin")

            # Publish an event
            plugin_system.publish_event("test_event", {"data": "test"})

            # Check if the active plugin received the event
            mock_plugin_instance.on_event.assert_called_once_with(
                "test_event", {"data": "test"}
            )
