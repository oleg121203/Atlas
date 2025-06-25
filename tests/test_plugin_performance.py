import pytest
import time
from typing import List
from plugins.base import PluginBase
from tests.mock_plugin_metadata import MockPluginMetadata as PluginMetadata
from tests.test_plugin_dependencies import MockPluginRegistry  # Import from existing test file

# Register performance marker
pytestmark = pytest.mark.performance

class PerfTestPlugin(PluginBase):
    """Plugin for performance testing."""
    def __init__(self, name: str, deps: List[str]):
        self.metadata = PluginMetadata(
            name=name,
            version="1.0.0",
            description="Performance test plugin",
            author="Test",
            dependencies=deps
        )
        self.active = False
        super().__init__()

    def _get_metadata(self): return self.metadata
    def _get_settings(self): return {}
    def activate(self, ctx=None): self.active = True
    def deactivate(self): self.active = False
    def is_active(self): return self.active

@pytest.mark.performance
def test_dependency_resolution_performance(benchmark):
    """Benchmark dependency resolution with 100 plugins."""
    registry = MockPluginRegistry()
    
    # Create plugin dependency graph
    plugins = [PerfTestPlugin(f"plugin_{i}", [] if i < 10 else [f"plugin_{i-1}"]) 
               for i in range(100)]
    
    for p in plugins:
        registry.register_plugin(p)
    
    # Benchmark activation of all plugins
    def activate_all():
        for p in plugins:
            registry.activate_plugin(p.get_metadata().name)
    
    benchmark(activate_all)
    assert all(p.is_active() for p in plugins)

@pytest.mark.performance
def test_mass_plugin_activation_memory():
    """Test memory usage during mass plugin activation."""
    import tracemalloc
    tracemalloc.start()
    
    registry = MockPluginRegistry()
    plugins = [PerfTestPlugin(f"plugin_{i}", []) for i in range(1000)]
    
    snapshot1 = tracemalloc.take_snapshot()
    
    for p in plugins:
        registry.register_plugin(p)
        registry.activate_plugin(p.get_metadata().name)
    
    snapshot2 = tracemalloc.take_snapshot()
    
    # Calculate memory difference
    diff = snapshot2.compare_to(snapshot1, 'lineno')
    total = sum(stat.size_diff for stat in diff)
    
    assert total < 100 * 1024 * 1024  # < 100MB for 1000 plugins
    tracemalloc.stop()
