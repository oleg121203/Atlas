import unittest
from unittest.mock import Mock

from core.module_registry import ModuleBase, ModuleRegistry


class TestModuleRegistry(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.event_bus = Mock()
        self.registry = ModuleRegistry(event_bus=self.event_bus)

    def test_initialization(self):
        """Test that the module registry initializes correctly."""
        self.assertEqual(self.registry.event_bus, self.event_bus)
        self.assertEqual(len(self.registry._modules), 0)
        self.assertEqual(len(self.registry._module_classes), 0)
        self.assertEqual(len(self.registry._dependencies), 0)
        self.assertEqual(len(self.registry._initialization_order), 0)

    def test_register_module(self):
        """Test registering a module with the registry."""

        class TestModule(ModuleBase):
            def __init__(self, name=None):
                super().__init__(name)

            def initialize(self):
                pass

            def start(self):
                pass

            def stop(self):
                pass

        self.registry.register_module(TestModule, "test_module")
        self.assertIn("test_module", self.registry._module_classes)
        self.assertEqual(self.registry._module_classes["test_module"], TestModule)

    def test_get_module(self):
        """Test retrieving a module from the registry."""

        class TestModule(ModuleBase):
            def __init__(self, name=None):
                super().__init__(name)

            def initialize(self):
                pass

            def start(self):
                pass

            def stop(self):
                pass

        self.registry.register_module(TestModule, "test_module")
        module = self.registry.get_module("test_module")
        self.assertIsNone(module)  # Module instance is not created yet


if __name__ == "__main__":
    unittest.main()
