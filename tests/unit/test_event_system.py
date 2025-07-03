# Standard library imports
import logging
import sys
import unittest
from unittest.mock import MagicMock, patch

# Third-party imports
# Local application imports
from core.event_system import EVENT_BUS, publish_module_event, register_module_events

# Path configuration
if ".." not in sys.path:
    sys.path.append("..")


class TestEventSystem(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        from core.event_system import EVENT_BUS

        self.event_bus = EVENT_BUS
        # Clear all listeners to ensure a clean state for each test
        for event_type in list(self.event_bus._subscribers.keys()):
            self.event_bus._subscribers[event_type].clear()
            del self.event_bus._subscribers[event_type]
        # Disable logging for tests to avoid clutter
        logging.getLogger().setLevel(logging.CRITICAL)

    def test_initialization(self):
        """Test that the event system initializes correctly."""
        self.assertIsNotNone(self.event_bus)

    def test_subscribe(self):
        """Test subscribing to an event."""
        listener = MagicMock()
        event_type = "test_event"
        self.event_bus.subscribe(event_type, listener)
        # Indirectly verify subscription by publishing
        self.event_bus.publish(event_type, event_type)
        listener.assert_called_once_with(event_type)

    def test_unsubscribe(self):
        """Test unsubscribing from an event."""
        listener = MagicMock()
        event_type = "test_event"
        self.event_bus.subscribe(event_type, listener)
        self.event_bus.unsubscribe(event_type, listener)
        # Verify unsubscription by publishing and checking listener not called
        self.event_bus.publish(event_type, event_type)
        listener.assert_not_called()

    def test_unsubscribe_nonexistent(self):
        """Test unsubscribing a non-existent listener or event type."""
        listener = MagicMock()
        event_type = "nonexistent_event"
        # Should not raise error when unsubscribing non-existent listener or event
        try:
            self.event_bus.unsubscribe(event_type, listener)
        except Exception as e:
            self.fail(
                f"Unsubscribing non-existent listener raised an unexpected exception: {e}"
            )

    def test_publish_event(self):
        """Test publishing a basic event."""
        listener = MagicMock()
        event_type = "test_event"
        self.event_bus.subscribe(event_type, listener)
        self.event_bus.publish(event_type, event_type)
        listener.assert_called_once_with(event_type)

    def test_publish_module_event(self):
        """Test publishing a module-specific event using the utility function."""
        listener = MagicMock()
        module_name = "test_module"
        event_type = "test_event"
        full_event_type = f"{module_name}:{event_type}"
        EVENT_BUS.subscribe(full_event_type, listener)
        # Verify subscription
        self.assertIn(full_event_type, EVENT_BUS._subscribers)
        self.assertIn(listener, EVENT_BUS._subscribers[full_event_type])
        publish_module_event(module_name, event_type, data="test_data")
        listener.assert_called_once_with(data="test_data")

    def test_publish_module_event_invalid_module(self):
        """Test publishing a module event with an invalid module name."""
        with self.assertRaises(ValueError):
            publish_module_event("", "test_event")

    def test_publish_module_event_invalid_event(self):
        """Test publishing a module event with an invalid event type."""
        with self.assertRaises(ValueError):
            publish_module_event("test_module", "")

    def test_register_module_events(self):
        """Test registering module events with listeners."""
        with patch("core.event_system.logger") as mock_logger:
            register_module_events("module1", ["event1", "event2"])
            mock_logger.info.assert_called_once_with(
                "Registering events for module: module1"
            )
            mock_logger.debug.assert_any_call(
                "Event registered: event1 for module: module1"
            )
            mock_logger.debug.assert_any_call(
                "Event registered: event2 for module: module1"
            )

    def test_register_module_events_invalid_module(self):
        """Test registering module events with invalid module name."""
        with self.assertRaises(ValueError):
            register_module_events("", ["event1"])

    def test_register_module_events_invalid_events_type(self):
        """Test registering module events with invalid events type."""
        with self.assertRaises(TypeError):
            register_module_events("test_module", {"event1": "listener"})

    def test_subscribe_multiple_listeners(self):
        """Test subscribing multiple listeners to the same event."""
        listener1 = MagicMock()
        listener2 = MagicMock()
        event_type = "test_event"
        self.event_bus.subscribe(event_type, listener1)
        self.event_bus.subscribe(event_type, listener2)
        self.event_bus.publish(event_type, event_type)
        listener1.assert_called_once_with(event_type)
        listener2.assert_called_once_with(event_type)

    def test_subscribe_invalid_event_type_non_string(self):
        """Test subscribing with a non-string event type."""
        listener = MagicMock()
        with self.assertRaises(TypeError):
            EVENT_BUS.subscribe(123, listener)

    def test_unsubscribe_invalid_event_type_non_string(self):
        """Test unsubscribing with a non-string event type."""
        listener = MagicMock()
        with self.assertRaises(TypeError):
            EVENT_BUS.unsubscribe(123, listener)

    def test_register_module_events_invalid_module_name(self):
        """Test registering module events with an invalid module name."""
        with self.assertRaises(ValueError):
            register_module_events("", ["event1"])

    def test_register_module_events_invalid_event_name(self):
        """Test registering module events with an invalid event name."""
        with self.assertRaises(ValueError):
            register_module_events("test_module", [""])

        with self.assertRaises(ValueError):
            register_module_events("test_module", ["", "event2"])

    def test_publish_module_event_valid(self):
        """Test publishing a module event with valid parameters."""
        mock_callback = MagicMock()
        full_event_type = "module1:event1"
        EVENT_BUS.subscribe(full_event_type, mock_callback)
        # Verify subscription
        self.assertIn(full_event_type, EVENT_BUS._subscribers)
        self.assertIn(mock_callback, EVENT_BUS._subscribers[full_event_type])
        publish_module_event("module1", "event1", data="test_data")
        mock_callback.assert_called_once_with(data="test_data")

    def test_publish_module_event_empty_module(self):
        """Test publishing a module event with an empty module name."""
        with self.assertRaises(ValueError):
            publish_module_event("", "event1")

    def test_publish_module_event_empty_event(self):
        """Test publishing a module event with an empty event type."""
        with self.assertRaises(ValueError):
            publish_module_event("module1", "")

    def test_register_module_events_valid(self):
        """Test registering module events with valid parameters."""
        with patch("core.event_system.logger") as mock_logger:
            register_module_events("module1", ["event1", "event2"])
            mock_logger.info.assert_called_once_with(
                "Registering events for module: module1"
            )
            mock_logger.debug.assert_any_call(
                "Event registered: event1 for module: module1"
            )
            mock_logger.debug.assert_any_call(
                "Event registered: event2 for module: module1"
            )

    def test_register_module_events_empty_module(self):
        """Test registering module events with an empty module name."""
        with self.assertRaises(ValueError):
            register_module_events("", ["event1"])

    def test_register_module_events_empty_events(self):
        """Test registering module events with an empty events list."""
        with self.assertRaises(ValueError):
            register_module_events("module1", [])

    def test_subscribe_invalid_event_type(self):
        """Test subscribing with an invalid event type."""
        with self.assertRaises(TypeError):
            EVENT_BUS.subscribe(123, MagicMock())

    def test_unsubscribe_invalid_event_type(self):
        """Test unsubscribing with an invalid event type."""
        with self.assertRaises(TypeError):
            EVENT_BUS.unsubscribe(123, MagicMock())

    def test_register_module_events_type_mismatch_events(self):
        """Test registering module events with a type mismatch in events parameter."""
        with self.assertRaises(TypeError):
            register_module_events("module1", {"event1": "value1"})


if __name__ == "__main__":
    unittest.main()
