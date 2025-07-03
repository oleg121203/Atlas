import logging
import unittest
from unittest.mock import Mock

from core.event_system import EventBus, publish_module_event, register_module_events


class TestEventSystem(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.event_bus = EventBus()
        # Disable logging for tests to avoid clutter
        logging.getLogger().setLevel(logging.CRITICAL)

    def test_initialization(self):
        """Test that the event system initializes correctly."""
        self.assertIsNotNone(self.event_bus)

    def test_subscribe(self):
        """Test subscribing to an event."""
        listener = Mock()
        event_type = "test_event"
        self.event_bus.subscribe(event_type, listener)
        # Indirectly verify subscription by publishing
        self.event_bus.publish(event_type, event_type)
        listener.assert_called_once_with(event_type)

    def test_unsubscribe(self):
        """Test unsubscribing from an event."""
        listener = Mock()
        event_type = "test_event"
        self.event_bus.subscribe(event_type, listener)
        self.event_bus.unsubscribe(event_type, listener)
        # Verify unsubscription by publishing and checking listener not called
        self.event_bus.publish(event_type, event_type)
        listener.assert_not_called()

    def test_unsubscribe_nonexistent(self):
        """Test unsubscribing a non-existent listener or event type."""
        listener = Mock()
        event_type = "nonexistent_event"
        # Should not raise error when unsubscribing non-existent listener or event
        try:
            self.event_bus.unsubscribe(event_type, listener)
        except Exception as e:
            self.fail(
                f"Unsubscribing non-existent listener raised an unexpected exception: {e}"
            )

    def test_publish_event(self):
        """Test publishing an event and notifying listeners."""
        listener1 = Mock()
        listener2 = Mock()
        event_type = "test_event"
        event_data = {"key": "value"}
        self.event_bus.subscribe(event_type, listener1)
        self.event_bus.subscribe(event_type, listener2)
        self.event_bus.publish(event_type, event_type, event_data)
        listener1.assert_called_once_with(event_type, event_data)
        listener2.assert_called_once_with(event_type, event_data)

    def test_publish_event_no_listeners(self):
        """Test publishing an event with no listeners."""
        event_type = "test_event"
        event_data = {"key": "value"}
        try:
            self.event_bus.publish(event_type, event_data)
        except Exception as e:
            self.fail(
                f"Publishing event with no listeners raised an unexpected exception: {e}"
            )

    def test_multiple_event_types(self):
        """Test that listeners for different event types are isolated."""
        listener1 = Mock()
        listener2 = Mock()
        event_type1 = "event1"
        event_type2 = "event2"
        event_data = {"key": "value"}
        self.event_bus.subscribe(event_type1, listener1)
        self.event_bus.subscribe(event_type2, listener2)
        self.event_bus.publish(event_type1, event_type1, event_data)
        listener1.assert_called_once_with(event_type1, event_data)
        listener2.assert_not_called()

    def test_error_handling_in_callbacks(self):
        """Test that errors in callbacks do not stop event processing."""

        def error_callback(*args, **kwargs):
            raise ValueError("Test error")

        listener1 = Mock()
        listener2 = Mock(side_effect=error_callback)
        listener3 = Mock()
        event_type = "error_event"
        event_data = {"key": "value"}
        self.event_bus.subscribe(event_type, listener1)
        self.event_bus.subscribe(event_type, listener2)
        self.event_bus.subscribe(event_type, listener3)
        self.event_bus.publish(event_type, event_type, event_data)
        listener1.assert_called_once_with(event_type, event_data)
        listener3.assert_called_once_with(event_type, event_data)

    def test_publish_module_event(self):
        """Test publishing a module-specific event."""
        listener = Mock()
        module_name = "test_module"
        event_type = "module_event"
        full_event_type = f"{module_name}.{event_type}"
        event_data = {"key": "value"}
        self.event_bus.subscribe(full_event_type, listener)
        from core import event_system

        original_event_bus = event_system.EVENT_BUS
        event_system.EVENT_BUS = self.event_bus
        try:
            publish_module_event(module_name, event_type, event_data)
            listener.assert_called_once_with(event_data)
        finally:
            event_system.EVENT_BUS = original_event_bus

    def test_register_module_events(self):
        """Test registering events for a module."""
        module_name = "test_module"
        events = ["event1", "event2"]
        try:
            register_module_events(module_name, events)
        except Exception as e:
            self.fail(f"Registering module events raised an unexpected exception: {e}")


if __name__ == "__main__":
    unittest.main()
