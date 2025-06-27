"""
Tests for the event_system module.
"""

import logging
import unittest
from unittest.mock import MagicMock, patch

from core.event_system import (
    EVENT_BUS,
    EventBus,
    publish_module_event,
    register_module_events,
)


class TestEventBus(unittest.TestCase):
    """Test cases for the EventBus class."""

    def setUp(self):
        """Set up a new EventBus for each test."""
        self.event_bus = EventBus()
        self.callback = MagicMock()

    def test_subscribe(self):
        """Test subscribing to an event."""
        # Execute
        self.event_bus.subscribe("test_event", self.callback)

        # Assert
        self.assertIn("test_event", self.event_bus._subscribers)
        self.assertIn(self.callback, self.event_bus._subscribers["test_event"])

    def test_unsubscribe(self):
        """Test unsubscribing from an event."""
        # Setup
        self.event_bus.subscribe("test_event", self.callback)

        # Execute
        self.event_bus.unsubscribe("test_event", self.callback)

        # Assert
        self.assertNotIn(self.callback, self.event_bus._subscribers["test_event"])

    def test_unsubscribe_nonexistent(self):
        """Test unsubscribing from a non-existent event."""
        # Execute - should not raise an exception
        self.event_bus.unsubscribe("nonexistent_event", self.callback)

    def test_publish(self):
        """Test publishing an event."""
        # Setup
        self.event_bus.subscribe("test_event", self.callback)

        # Execute
        self.event_bus.publish("test_event", "arg1", "arg2", kwarg1="value1")

        # Assert
        self.callback.assert_called_once_with("arg1", "arg2", kwarg1="value1")

    def test_publish_multiple_subscribers(self):
        """Test publishing an event to multiple subscribers."""
        # Setup
        callback2 = MagicMock()
        self.event_bus.subscribe("test_event", self.callback)
        self.event_bus.subscribe("test_event", callback2)

        # Execute
        self.event_bus.publish("test_event")

        # Assert
        self.callback.assert_called_once()
        callback2.assert_called_once()

    def test_publish_no_subscribers(self):
        """Test publishing an event with no subscribers."""
        # Execute - should not raise an exception
        self.event_bus.publish("nonexistent_event")

    def test_callback_exception_handling(self):
        """Test that exceptions in callbacks are properly handled."""
        # Setup
        error_callback = MagicMock(side_effect=Exception("Test exception"))
        self.event_bus.subscribe("test_event", error_callback)

        # Execute
        with self.assertLogs(level=logging.ERROR) as cm:
            self.event_bus.publish("test_event")

        # Assert
        self.assertIn("Error in callback for event test_event", cm.output[0])


class TestModuleEvents(unittest.TestCase):
    """Test cases for module event functions."""

    def setUp(self):
        """Set up tests for module events."""
        self.callback = MagicMock()
        # Patch the global EVENT_BUS to use a fresh instance for each test
        self.patcher = patch("core.event_system.EVENT_BUS", EventBus())
        self.mock_event_bus = self.patcher.start()
        # Also get a reference to the real EventBus instance for assertions
        from core.event_system import EVENT_BUS

        self.event_bus = EVENT_BUS

    def tearDown(self):
        """Clean up after each test."""
        self.patcher.stop()

    @patch("core.event_system.logger")
    def test_register_module_events(self, mock_logger):
        """Test registering module events."""
        # Execute
        register_module_events("test_module", ["event1", "event2"])

        # Assert
        mock_logger.info.assert_called_once()
        self.assertEqual(mock_logger.debug.call_count, 2)

    def test_publish_module_event(self):
        """Test publishing a module event."""
        # Setup
        self.event_bus.subscribe("test_module.test_event", self.callback)

        # Execute
        publish_module_event("test_module", "test_event", "arg1", kwarg1="value1")

        # Assert
        self.callback.assert_called_once_with("arg1", kwarg1="value1")

    def test_global_event_bus_instance(self):
        """Test that a global EVENT_BUS instance exists."""
        # Import the module to get the actual EVENT_BUS instance
        from core.event_system import EVENT_BUS

        # Assert
        self.assertIsInstance(EVENT_BUS, EventBus)
