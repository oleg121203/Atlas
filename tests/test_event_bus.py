#!/usr/bin/env python3
"""
Tests for the Event Bus core module.
"""

import unittest

from atlas.core.event_bus import EventBus


def dummy_callback(**kwargs):
    pass


class TestEventBus(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.event_bus = EventBus()

    def test_initialization(self):
        """Test initialization of EventBus."""
        self.assertIsInstance(self.event_bus, EventBus)
        self.assertEqual(len(self.event_bus._subscribers), 0)

    def test_subscribe(self):
        """Test subscribe method."""
        callback = dummy_callback
        event_type = "test_event"
        self.event_bus.subscribe(event_type, callback)
        self.assertIn(event_type, self.event_bus._subscribers)
        self.assertIn(callback, self.event_bus._subscribers[event_type])

    def test_unsubscribe(self):
        """Test unsubscribe method."""
        callback = dummy_callback
        event_type = "test_event"
        self.event_bus.subscribe(event_type, callback)
        self.event_bus.unsubscribe(event_type, callback)
        self.assertNotIn(callback, self.event_bus._subscribers.get(event_type, set()))

    def test_publish_with_subscriber(self):
        """Test publish method with a subscriber."""
        callback = dummy_callback
        event_type = "test_event"
        event_data = {"key": "value"}
        self.event_bus.subscribe(event_type, callback)
        self.event_bus.publish(event_type, data=event_data)
        self.assertIn(callback, self.event_bus._subscribers.get(event_type, set()))

    def test_publish_without_subscriber(self):
        """Test publish method with no subscribers."""
        event_type = "test_event"
        event_data = {"key": "value"}
        # Should not raise any error
        self.event_bus.publish(event_type, data=event_data)

    def test_publish_multiple_subscribers(self):
        """Test publish method with multiple subscribers."""
        callback1 = dummy_callback
        callback2 = dummy_callback
        event_type = "test_event"
        event_data = {"key": "value"}
        self.event_bus.subscribe(event_type, callback1)
        self.event_bus.subscribe(event_type, callback2)
        self.event_bus.publish(event_type, data=event_data)
        self.assertIn(callback1, self.event_bus._subscribers.get(event_type, set()))
        self.assertIn(callback2, self.event_bus._subscribers.get(event_type, set()))

    def test_subscribe_multiple_callbacks(self):
        """Test subscribing multiple callbacks to the same event type."""
        callback1 = dummy_callback
        callback2 = dummy_callback
        event_type = "test_event"
        self.event_bus.subscribe(event_type, callback1)
        self.event_bus.subscribe(event_type, callback2)
        self.assertEqual(len(self.event_bus._subscribers[event_type]), 1)
        self.assertIn(callback1, self.event_bus._subscribers[event_type])
        self.assertIn(callback2, self.event_bus._subscribers[event_type])

    def test_unsubscribe_nonexistent(self):
        """Test unsubscribing a non-existent callback."""
        callback = dummy_callback
        event_type = "test_event"
        # Should not raise any error
        self.event_bus.unsubscribe(event_type, callback)


if __name__ == "__main__":
    unittest.main()
