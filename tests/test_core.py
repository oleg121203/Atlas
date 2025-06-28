"""
Test cases for core components of the Atlas application.
"""

import unittest
from unittest.mock import MagicMock, patch

from core.atlas_application import AtlasApplication
from core.event_bus import EventBus
from core.module_system import ModuleRegistry as ModuleRegistrySystem


class TestEventBus(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.event_bus = EventBus()

    def test_event_bus_subscription(self):
        """Test event bus subscription and publishing."""
        test_data = {"message": "test"}
        callback = MagicMock()

        self.event_bus.subscribe("test_event", callback)
        self.event_bus.publish("test_event", test_data)

        callback.assert_called_once_with(test_data)

    def test_event_bus_multiple_subscribers(self):
        """Test multiple subscribers for same event."""
        test_data = {"message": "test"}
        callback1 = MagicMock()
        callback2 = MagicMock()

        self.event_bus.subscribe("test_event", callback1)
        self.event_bus.subscribe("test_event", callback2)
        self.event_bus.publish("test_event", test_data)

        callback1.assert_called_once_with(test_data)
        callback2.assert_called_once_with(test_data)

    def test_event_bus_unsubscribe(self):
        """Test unsubscribing from events."""
        test_data = {"message": "test"}
        callback = MagicMock()

        self.event_bus.subscribe("test_event", callback)
        self.event_bus.unsubscribe("test_event", callback)
        self.event_bus.publish("test_event", test_data)

        callback.assert_not_called()


class TestAtlasApplication(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.app_name = "test_atlas"
        with patch("PySide6.QtWidgets.QApplication"):
            self.app = AtlasApplication(self.app_name)

    @patch("core.atlas_application.setup_logging")
    @patch("core.atlas_application.check_environment_security")
    @patch("core.atlas_application.initialize_security")
    @patch("core.atlas_application.initialize_alerting")
    @patch("core.atlas_application.start_monitoring")
    def test_application_initialization(
        self,
        mock_monitoring,
        mock_alerting,
        mock_security_init,
        mock_security_check,
        mock_logging,
    ):
        """Test if the application initializes correctly."""
        # Verify initialization
        mock_security_check.return_value = True
        mock_security_init.return_value = True
        mock_alerting.return_value = True

        with patch("PySide6.QtWidgets.QApplication"):
            app = AtlasApplication(self.app_name)

        self.assertIsNotNone(app)
        mock_logging.assert_called_once()
        mock_security_check.assert_called_once()
        mock_security_init.assert_called_once()
        mock_alerting.assert_called_once()
        mock_monitoring.assert_called_once()


class TestModuleSystem(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.module_registry = ModuleRegistrySystem()

    def test_module_registration(self):
        """Test module registration and retrieval."""
        mock_module = MagicMock()
        module_name = "test_module"

        # Test registration
        self.module_registry.register_module(module_name, mock_module)
        self.assertIn(module_name, self.module_registry.modules)

        # Test retrieval
        retrieved_module = self.module_registry.get_module(module_name)
        self.assertEqual(retrieved_module, mock_module)

    def test_module_duplicate_registration(self):
        """Test that duplicate module registration raises error."""
        mock_module = MagicMock()
        module_name = "test_module"

        self.module_registry.register_module(module_name, mock_module)
        with self.assertRaises(ValueError):
            self.module_registry.register_module(module_name, mock_module)


if __name__ == "__main__":
    unittest.main()
