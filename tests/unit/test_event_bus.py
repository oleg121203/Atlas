import unittest
from unittest.mock import Mock

from core.event_bus import EventBus


class TestEventBus(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.event_bus = EventBus()

    def test_initialization(self):
        """Test that the event bus initializes correctly."""
        self.assertEqual(len(self.event_bus._listeners), 0)

    def test_subscribe(self):
        """Test subscribing a listener to an event."""
        listener = Mock()
        self.event_bus.subscribe("test_event", listener)
        self.assertIn("test_event", self.event_bus._listeners)
        self.assertIn(listener, self.event_bus._listeners["test_event"])

    def test_unsubscribe(self):
        """Test unsubscribing a listener from an event."""
        listener = Mock()
        self.event_bus.subscribe("test_event", listener)
        self.event_bus.unsubscribe("test_event", listener)
        self.assertIn("test_event", self.event_bus._listeners)
        self.assertNotIn(listener, self.event_bus._listeners["test_event"])

    def test_publish(self):
        """Test publishing an event to listeners."""
        listener = Mock()
        self.event_bus.subscribe("test_event", listener)
        event_data = {"key": "value"}
        self.event_bus.publish("test_event", event_data)
        listener.assert_called_once_with(event_data)


if __name__ == "__main__":
    unittest.main()
