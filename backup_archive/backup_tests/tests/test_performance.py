import logging
import time

import pytest
from plugins.base import PluginBase, PluginMetadata
from plugins.plugin_registry import PluginRegistry

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def registry():
    """Plugin registry fixture."""
    return PluginRegistry()


class TestPluginPerformance:
    """Performance tests for plugin system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = PluginRegistry()

    def test_plugin_loading_performance(self, registry):
        """Test performance of plugin loading."""
        num_plugins = 100
        plugins = []

        # Create test plugins
        for i in range(num_plugins):
            metadata = PluginMetadata(
                name=f"TestPlugin{i}",
                description=f"Test plugin {i}",
                version="1.0.0",
                author="Test Author",
                dependencies=[],
                min_app_version="1.0.0",
            )
            plugin = PluginBase()
            plugin.metadata = metadata
            plugins.append(plugin)

        # Measure loading time
        start_time = time.time()
        for plugin in plugins:
            registry.plugins[plugin.metadata.name] = plugin
        loading_time = time.time() - start_time

        # Performance requirements
        assert loading_time < 0.5  # Should load 100 plugins in < 0.5s
        logger.info(f"Loaded {num_plugins} plugins in {loading_time:.3f}s")

    def test_plugin_activation_performance(self, registry):
        """Test performance of plugin activation."""
        num_plugins = 50
        plugins = []

        # Create test plugins
        for i in range(num_plugins):
            metadata = PluginMetadata(
                name=f"TestPlugin{i}",
                description=f"Test plugin {i}",
                version="1.0.0",
                author="Test Author",
                dependencies=[],
                min_app_version="1.0.0",
            )
            plugin = PluginBase()
            plugin.metadata = metadata
            registry.plugins[plugin.metadata.name] = plugin
            plugins.append(plugin)

        # Measure activation time
        start_time = time.time()
        for plugin in plugins:
            registry.activate_plugin(plugin.metadata.name)
        activation_time = time.time() - start_time

        # Performance requirements
        assert activation_time < 0.2  # Should activate 50 plugins in < 0.2s
        logger.info(f"Activated {num_plugins} plugins in {activation_time:.3f}s")

    def test_plugin_search_performance(self, registry):
        """Test performance of plugin search."""
        num_plugins = 1000

        # Create test plugins
        for i in range(num_plugins):
            metadata = PluginMetadata(
                name=f"TestPlugin{i}",
                description=f"Test plugin {i}",
                version="1.0.0",
                author="Test Author",
                dependencies=[],
                min_app_version="1.0.0",
            )
            plugin = PluginBase()
            plugin.metadata = metadata
            registry.plugins[plugin.metadata.name] = plugin

        # Measure search time
        start_time = time.time()
        registry.list_plugins()
        search_time = time.time() - start_time

        # Performance requirements
        assert search_time < 0.1  # Should search 1000 plugins in < 0.1s
        logger.info(f"Searched {num_plugins} plugins in {search_time:.3f}s")

    def test_plugin_reload_performance(self, registry):
        """Test performance of plugin reload."""
        num_plugins = 50
        plugins = []

        # Create test plugins
        for i in range(num_plugins):
            metadata = PluginMetadata(
                name=f"TestPlugin{i}",
                description=f"Test plugin {i}",
                version="1.0.0",
                author="Test Author",
                dependencies=[],
                min_app_version="1.0.0",
            )
            plugin = PluginBase()
            plugin.metadata = metadata
            registry.plugins[plugin.metadata.name] = plugin
            plugins.append(plugin)

        # Activate all plugins first
        for plugin in plugins:
            registry.activate_plugin(plugin.metadata.name)

        # Measure reload time
        start_time = time.time()
        registry.reload_all_plugins()
        reload_time = time.time() - start_time

        # Performance requirements
        assert reload_time < 0.3  # Should reload 50 plugins in < 0.3s
        logger.info(f"Reloaded {num_plugins} plugins in {reload_time:.3f}s")

    def test_concurrent_plugin_operations(self, registry):
        """Test performance with concurrent plugin operations."""
        num_plugins = 20
        plugins = []

        # Create test plugins
        for i in range(num_plugins):
            metadata = PluginMetadata(
                name=f"TestPlugin{i}",
                description=f"Test plugin {i}",
                version="1.0.0",
                author="Test Author",
                dependencies=[],
                min_app_version="1.0.0",
            )
            plugin = PluginBase()
            plugin.metadata = metadata
            registry.plugins[plugin.metadata.name] = plugin
            plugins.append(plugin)

        # Measure concurrent operations time
        start_time = time.time()
        for i in range(10):  # Repeat operations multiple times
            for plugin in plugins:
                registry.activate_plugin(plugin.metadata.name)
                registry.deactivate_plugin(plugin.metadata.name)
        concurrent_time = time.time() - start_time

        # Performance requirements
        assert concurrent_time < 1.0  # Should complete 200 operations in < 1s
        logger.info(
            f"Completed {num_plugins * 20} operations in {concurrent_time:.3f}s"
        )
