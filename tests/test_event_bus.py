"""
Test cases for core Event Bus system.
"""

import unittest
from unittest.mock import MagicMock

from core.event_bus import EventBus


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

    def test_publish_nonexistent_event(self):
        """Test publishing event with no subscribers."""
        test_data = {"message": "test"}
        self.event_bus.publish("nonexistent_event", test_data)
        # Should not raise any exception


if __name__ == "__main__":
    unittest.main()
