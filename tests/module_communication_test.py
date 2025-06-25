import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QCoreApplication
from ui.main_window import AtlasMainWindow
from ui.module_communication import EVENT_BUS, publish_module_event

class ModuleCommunicationTest(unittest.TestCase):
    def setUp(self):
        # Ensure a QApplication instance exists for Qt operations
        if QCoreApplication.instance() is None:
            self.app = QApplication([])
        else:
            self.app = QCoreApplication.instance()
        # Mock dependencies to simulate module interactions
        self.mock_meta_agent = MagicMock()
        self.mock_meta_agent.agent_manager = MagicMock()
        # Reset the event bus subscribers for each test
        EVENT_BUS._subscribers = {}

    def test_event_bus_subscription_and_publishing(self):
        """Test that modules can subscribe to and receive events via the event bus."""
        # Initialize main window
        main_window = AtlasMainWindow()
        main_window._init_modules(meta_agent=self.mock_meta_agent)

        # Mock a callback to track event reception
        mock_callback = MagicMock()
        EVENT_BUS.subscribe("test_event", mock_callback)

        # Publish an event
        publish_module_event("test_event", {"key": "value"})

        # Verify the callback was called with the correct data
        mock_callback.assert_called_once_with({"key": "value"})

    def test_module_event_registration(self):
        """Test that modules are registered to receive specific events."""
        main_window = AtlasMainWindow()
        main_window._init_modules(meta_agent=self.mock_meta_agent)

        # Check if modules are subscribed to their respective events
        self.assertIn("task_added", EVENT_BUS._subscribers, "ChatModule should be subscribed to task_added")
        self.assertIn("settings_updated", EVENT_BUS._subscribers, "ChatModule should be subscribed to settings_updated")
        self.assertIn("agent_updated", EVENT_BUS._subscribers, "AgentsModule should be subscribed to agent_updated")
        self.assertIn("plugin_activated", EVENT_BUS._subscribers, "PluginsModule should be subscribed to plugin_activated")
        self.assertIn("stats_updated", EVENT_BUS._subscribers, "StatsModule should be subscribed to stats_updated")
        self.assertIn("system_event", EVENT_BUS._subscribers, "SystemControlModule should be subscribed to system_event")
        self.assertIn("improvement_update", EVENT_BUS._subscribers, "SelfImprovementCenter should be subscribed to improvement_update")

    def test_event_publishing_with_no_subscribers(self):
        """Test that publishing an event with no subscribers does not cause errors."""
        # Publish an event with no subscribers
        try:
            publish_module_event("unsubscribed_event", {"data": "test"})
            self.assertTrue(True, "Publishing with no subscribers should not raise an exception")
        except Exception as e:
            self.fail(f"Publishing with no subscribers raised an exception: {e}")

    @patch('ui_qt.main_window.ChatModule')
    def test_event_handling_with_module_failure(self, mock_chat):
        """Test event handling when a module initialization fails."""
        mock_chat.side_effect = Exception("ChatModule initialization failed")
        main_window = AtlasMainWindow()
        main_window._init_modules(meta_agent=self.mock_meta_agent)

        # Publish an event that ChatModule would normally subscribe to
        publish_module_event("task_added", {"key": "value"})

        # Ensure no crash occurs even if ChatModule failed to initialize
        self.assertTrue(True, "Event publishing should not crash with failed module initialization")

if __name__ == '__main__':
    unittest.main()
