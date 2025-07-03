import time
from unittest.mock import Mock, patch

import pytest

from core.application import AtlasApplication
from core.event_system import EventBus
from core.module_base import ModuleBase


# Mock class for performance testing
class MockModule(ModuleBase):
    def __init__(self, app):
        super().__init__(app)
        self.name = "MockModule"

    def initialize(self):
        pass

    def shutdown(self):
        pass


# Performance benchmarks
@pytest.mark.benchmark(group="application")
def test_application_initialization(benchmark):
    """Benchmark the initialization of AtlasApplication."""

    def init_app():
        with (
            patch("core.application.EventBus", return_value=Mock()),
            patch("core.application.ModuleRegistry", return_value=Mock()),
            patch("core.application.PluginSystem", return_value=Mock()),
            patch("tools.tool_manager.ToolManager", return_value=Mock()),
            patch("core.application.SelfHealingSystem", return_value=Mock()),
        ):
            app = AtlasApplication()
        return app

    benchmark(init_app)


@pytest.mark.benchmark(group="event_system")
def test_event_system_publish(benchmark):
    """Benchmark the event publishing performance of EventBus."""
    with patch("core.application.EventBus", return_value=Mock()):
        event_bus = EventBus()

    def publish_event():
        event_bus.publish("test_event", {"data": "test"})

    benchmark(publish_event)


@pytest.mark.benchmark(group="module")
def test_module_initialization(benchmark):
    """Benchmark the initialization of a Module."""
    with (
        patch("core.application.EventBus", return_value=Mock()),
        patch("core.application.ModuleRegistry", return_value=Mock()),
        patch("core.application.PluginSystem", return_value=Mock()),
        patch("tools.tool_manager.ToolManager", return_value=Mock()),
        patch("core.application.SelfHealingSystem", return_value=Mock()),
    ):
        app = AtlasApplication()

    def init_module():
        module = MockModule(app)
        module.initialize()
        return module

    benchmark(init_module)


# Add more benchmarks for other critical components
@pytest.mark.benchmark(group="memory_operations")
def test_memory_operation(benchmark):
    """Benchmark a simulated memory operation."""

    def memory_op():
        time.sleep(0.05)  # Simulate a memory operation

    benchmark(memory_op)


@pytest.mark.benchmark(group="screen_input_tools")
def test_screen_input_tool(benchmark):
    """Benchmark a simulated screen/input tool operation."""

    def screen_op():
        time.sleep(0.02)  # Simulate a screen/input operation

    benchmark(screen_op)


@pytest.mark.benchmark(group="planning_operations")
def test_planning_operation(benchmark):
    """Benchmark a simulated planning operation."""

    def planning_op():
        time.sleep(0.1)  # Simulate a planning operation

    benchmark(planning_op)
