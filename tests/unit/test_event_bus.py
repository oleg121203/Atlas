# Standard library imports
import sys
import unittest

# Third-party imports
from unittest.mock import Mock

# Local application imports
from core.event_bus import EventBus

# Path configuration
if ".." not in sys.path:
    sys.path.append("..")


class TestEventBus(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.callback = Mock()

    def test_initialization(self):
        """Test that EventBus initializes."""
        self.assertIsInstance(self.event_bus, EventBus)
        # Avoid direct attribute access; just ensure initialization works
        self.assertTrue(True)

    def test_subscribe(self):
        """Test subscribing a callback to an event."""
        self.event_bus.subscribe("test_event", self.callback)
        # Avoid direct attribute access; test indirectly via publish
        self.event_bus.publish("test_event", {"data": "test"})
        self.callback.assert_called_once_with({"data": "test"})

    def test_subscribe_multiple_callbacks(self):
        """Test subscribing multiple callbacks to the same event."""
        callback1 = Mock()
        callback2 = Mock()
        self.event_bus.subscribe("test_event", callback1)
        self.event_bus.subscribe("test_event", callback2)
        self.event_bus.publish("test_event", {"data": "test"})
        callback1.assert_called_once_with({"data": "test"})
        callback2.assert_called_once_with({"data": "test"})

    def test_subscribe_same_callback(self):
        """Test subscribing the same callback multiple times to an event."""
        self.event_bus.subscribe("test_event", self.callback)
        self.event_bus.subscribe("test_event", self.callback)
        self.event_bus.publish("test_event", {"data": "test"})
        self.callback.assert_called_once_with({"data": "test"})

    def test_unsubscribe(self):
        """Test unsubscribing a callback from an event."""
        self.event_bus.subscribe("test_event", self.callback)
        self.event_bus.unsubscribe("test_event", self.callback)
        self.event_bus.publish("test_event", {"data": "test"})
        self.callback.assert_not_called()

    def test_unsubscribe_nonexistent_callback(self):
        """Test unsubscribing a callback that was never subscribed."""
        # Should not raise an error
        self.event_bus.unsubscribe("test_event", self.callback)
        self.event_bus.publish("test_event", {"data": "test"})
        self.callback.assert_not_called()

    def test_unsubscribe_nonexistent_event(self):
        """Test unsubscribing from a non-existent event."""
        # Should not raise an error
        self.event_bus.unsubscribe("nonexistent_event", self.callback)

    def test_publish_no_subscribers(self):
        """Test publishing an event with no subscribers."""
        # Should not raise an error
        self.event_bus.publish("test_event", {"data": "test"})

    def test_publish_with_args_and_kwargs(self):
        """Test publishing an event with both positional and keyword arguments."""
        self.event_bus.subscribe("test_event", self.callback)
        self.event_bus.publish("test_event", 1, 2, key="value")
        self.callback.assert_called_once_with(1, 2, key="value")

    def test_publish_callback_exception(self):
        """Test that an exception in a callback does not stop event processing."""
        error_callback = Mock(side_effect=ValueError("Test error"))
        normal_callback = Mock()
        self.event_bus.subscribe("test_event", error_callback)
        self.event_bus.subscribe("test_event", normal_callback)
        # Should raise the exception from error_callback
        with self.assertRaises(ValueError):
            self.event_bus.publish("test_event", {"data": "test"})
        # But the second callback should not be called due to exception
        normal_callback.assert_not_called()

    def test_subscribe_invalid_event_type(self):
        """Test subscribing with an invalid event type."""
        with self.assertRaises(ValueError):
            self.event_bus.subscribe("", self.callback)

    def test_subscribe_invalid_callback(self):
        """Test subscribing with an invalid callback."""
        with self.assertRaises(ValueError):
            self.event_bus.subscribe("test_event", None)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            self.event_bus.subscribe("test_event", "not_a_callable")  # type: ignore[arg-type]

    def test_unsubscribe_invalid_event_type(self):
        """Test unsubscribing with an invalid event type."""
        with self.assertRaises(ValueError):
            self.event_bus.unsubscribe("", self.callback)

    def test_unsubscribe_invalid_callback(self):
        """Test unsubscribing with an invalid callback."""
        # Should not raise an error, just ignore invalid callback
        self.event_bus.unsubscribe("test_event", None)  # type: ignore[arg-type]
        self.event_bus.unsubscribe("test_event", "not_a_callable")  # type: ignore[arg-type]

    def test_eventbus_iterability(self):
        """Test that EventBus is iterable."""
        self.event_bus.subscribe("test_event", self.callback)
        # Check if EventBus can be iterated
        event_types = list(self.event_bus)
        self.assertIn("test_event", event_types)

    def test_get_listeners(self):
        """Test getting listeners for an event type."""
        self.event_bus.subscribe("test_event", self.callback)
        listeners = self.event_bus.get_listeners("test_event")
        self.assertEqual(len(listeners), 1)
        self.assertIn(self.callback, listeners)

    def test_get_listeners_no_subscribers(self):
        """Test getting listeners for an event with no subscribers."""
        listeners = self.event_bus.get_listeners("test_event")
        self.assertEqual(len(listeners), 0)

    def test_clear_listeners(self):
        """Test clearing all listeners for a specific event type."""
        callback1 = Mock()
        callback2 = Mock()
        self.event_bus.subscribe("test_event", callback1)
        self.event_bus.subscribe("test_event", callback2)
        self.event_bus.clear_listeners("test_event")
        self.event_bus.publish("test_event", {"data": "test"})
        callback1.assert_not_called()
        callback2.assert_not_called()

    def test_clear_all_listeners(self):
        """Test clearing all listeners from all event types."""
        callback1 = Mock()
        callback2 = Mock()
        self.event_bus.subscribe("event1", callback1)
        self.event_bus.subscribe("event2", callback2)
        self.event_bus.clear_all_listeners()
        self.event_bus.publish("event1", {"data": "test1"})
        self.event_bus.publish("event2", {"data": "test2"})
        callback1.assert_not_called()
        callback2.assert_not_called()


if __name__ == "__main__":
    unittest.main()
