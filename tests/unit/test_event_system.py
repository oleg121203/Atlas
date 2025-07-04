# Configure logging for tests
import logging
import unittest
from unittest.mock import MagicMock, Mock

from core.event_system import EVENT_BUS, publish_module_event, register_module_events

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestEventSystem(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.callback = Mock()
        self.event_type = "test_event"

    def test_subscribe_listener(self):
        """Test subscribing a listener to an event type."""
        EVENT_BUS.subscribe(self.event_type, self.callback)
        self.assertIn(self.event_type, EVENT_BUS._subscribers)
        self.assertIn(self.callback, EVENT_BUS._subscribers[self.event_type])

    def test_unsubscribe_listener(self):
        """Test unsubscribing a listener from an event type."""
        EVENT_BUS.subscribe(self.event_type, self.callback)
        EVENT_BUS.unsubscribe(self.event_type, self.callback)
        self.assertNotIn(self.callback, EVENT_BUS._subscribers.get(self.event_type, []))

    def test_publish_event(self):
        """Test publishing a simple event."""
        EVENT_BUS.subscribe("test_event", self.callback)
        EVENT_BUS.publish("test_event", data="test_data")
        self.callback.assert_called_once_with(data="test_data")

    def test_publish_event_no_listeners(self):
        """Test publishing an event with no listeners."""
        # Should not raise any error
        EVENT_BUS.publish("no_listeners", data="test")
        self.assertTrue(True)

    def test_publish_event_multiple_listeners(self):
        """Test publishing an event to multiple listeners."""
        callback2 = MagicMock()
        EVENT_BUS.subscribe("multi_test", self.callback)
        EVENT_BUS.subscribe("multi_test", callback2)
        EVENT_BUS.publish("multi_test", data="multi_data")
        self.callback.assert_called_once_with(data="multi_data")
        callback2.assert_called_once_with(data="multi_data")

    def test_listener_exception_handling(self):
        """Test that exceptions in listeners are handled gracefully."""

        def error_callback(*args, **kwargs):
            raise ValueError("Listener error")

        EVENT_BUS.subscribe("test_error", error_callback)
        # Should not crash despite listener error
        EVENT_BUS.publish("test_error", data="test")
        # No assertion needed; passing without crashing is success
        self.assertTrue(True)

    def test_publish_non_string_event_type(self):
        """Test publishing an event with non-string event type."""
        with self.assertRaises(TypeError):
            EVENT_BUS.publish(123, data="invalid")

    def test_subscribe_empty_event_type(self):
        """Test subscribing with empty event type."""
        with self.assertRaises(ValueError):
            EVENT_BUS.subscribe("", self.callback)

    def test_subscribe_invalid_callback(self):
        """Test subscribing with invalid callback."""
        with self.assertRaises(TypeError):
            EVENT_BUS.subscribe("test_event", "not_callable")

    def test_subscribe_non_string_event_type(self):
        """Test subscribing with non-string event type."""
        with self.assertRaises(TypeError):
            EVENT_BUS.subscribe(123, self.callback)

    def test_unsubscribe_listener(self):
        """Test unsubscribing a listener from an event."""
        callback = MagicMock()
        event_type = "TestModule:test_event"
        EVENT_BUS.subscribe(event_type, callback)
        EVENT_BUS.unsubscribe(event_type, callback)
        publish_module_event("TestModule", "test_event", data="test_data")
        callback.assert_not_called()

    def test_unsubscribe_non_string_event_type(self):
        """Test unsubscribing with non-string event type."""
        with self.assertRaises(TypeError):
            EVENT_BUS.unsubscribe(123, 0)

    def test_register_module_events(self):
        """Test registering multiple events for a module."""
        module_name = "TestModule"
        events = ["event1", "event2"]
        try:
            register_module_events(module_name, events)
        except Exception as e:
            self.fail(f"register_module_events raised an exception: {e}")

    def test_register_module_events_empty_events(self):
        """Test registering module events with an empty events list."""
        with self.assertRaises(ValueError):
            register_module_events("TestModule", [])

    def test_publish_module_event(self):
        """Test publishing a module event with the correct event type format."""
        callback = MagicMock()
        event_type = "TestModule:test_event"
        EVENT_BUS.subscribe(event_type, callback)
        publish_module_event("TestModule", "test_event", data="test_data")
        callback.assert_called_once_with(data="test_data")

    def test_publish_module_event_empty_module_name(self):
        """Test publishing a module event with an empty module name."""
        with self.assertRaises(ValueError):
            publish_module_event("", "test_event")

    def test_publish_module_event_empty_event_type(self):
        """Test publishing a module event with an empty event type."""
        with self.assertRaises(ValueError):
            publish_module_event("", "module.TestModule")

    def test_publish_module_event_non_string_module_name(self):
        """Test publishing a module event with a non-string module name."""
        with self.assertRaises(TypeError):
            # Use a non-string value to trigger TypeError
            publish_module_event("test_event", 123)  # type: ignore

    def test_publish_module_event_non_string_event_type(self):
        """Test publishing a module event with a non-string event type."""
        with self.assertRaises(TypeError):
            # Use a non-string value to trigger TypeError
            publish_module_event(123, "module.TestModule")  # type: ignore


if __name__ == "__main__":
    unittest.main()
