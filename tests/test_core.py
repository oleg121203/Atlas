"""
Test cases for the core module of Atlas application.
"""

import unittest
from core.application import AtlasApplication
from core.event_system import EVENT_BUS
from core.config import CONFIG
from core.plugin_system import PLUGIN_REGISTRY
from core.module_registry import MODULE_REGISTRY

class TestCoreComponents(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.app = AtlasApplication([])

    def test_application_initialization(self):
        """Test if the application initializes correctly."""
        self.assertIsNotNone(self.app)
        self.assertTrue(hasattr(self.app, 'token_tracker'))
        self.assertTrue(hasattr(self.app, 'llm_manager'))
        self.assertTrue(hasattr(self.app, 'master_agent'))

    def test_event_bus_subscription(self):
        """Test event bus subscription and publishing."""
        def callback(event_data):
            self.assertEqual(event_data, {'message': 'test'})
        EVENT_BUS.subscribe('test_event', callback)
        EVENT_BUS.publish('test_event', {'message': 'test'})

    def test_config_loading(self):
        """Test configuration loading and retrieval."""
        self.assertIsNotNone(CONFIG.get('environment'))
        self.assertEqual(CONFIG.get('environment'), 'development')

    def test_plugin_registry(self):
        """Test plugin registry initialization."""
        self.assertIsNotNone(PLUGIN_REGISTRY)
        self.assertTrue(hasattr(PLUGIN_REGISTRY, 'discover_plugins'))

    def test_module_registry(self):
        """Test module registry initialization and module loading."""
        self.assertIsNotNone(MODULE_REGISTRY)
        self.assertTrue(hasattr(MODULE_REGISTRY, 'register_module'))

if __name__ == '__main__':
    unittest.main()
