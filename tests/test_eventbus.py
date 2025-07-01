from core.event_bus import EventBus


def test_eventbus_publish_subscribe():
    bus = EventBus()
    received = {}

    class MockModuleA:
        def send(self):
            bus.publish("TestEvent", data=42)

    class MockModuleB:
        def __init__(self):
            self.data = None
            bus.subscribe("TestEvent", self.on_event)

        def on_event(self, data=None):
            received["data"] = data
            self.data = data

    a = MockModuleA()
    b = MockModuleB()
    a.send()
    assert received["data"] == 42
    assert b.data == 42


def test_eventbus_unsubscribe():
    """Test unsubscribing from events."""
    bus = EventBus()
    called = []

    def callback1():
        called.append("callback1")

    def callback2():
        called.append("callback2")

    # Subscribe both callbacks
    bus.subscribe("test_event", callback1)
    bus.subscribe("test_event", callback2)

    # Publish event - both should be called
    bus.publish("test_event")
    assert "callback1" in called
    assert "callback2" in called

    # Clear and unsubscribe one callback
    called.clear()
    bus.unsubscribe("test_event", callback1)

    # Publish again - only callback2 should be called
    bus.publish("test_event")
    assert "callback1" not in called
    assert "callback2" in called


def test_eventbus_get_listeners():
    """Test getting listeners for an event type."""
    bus = EventBus()

    def callback1():
        pass

    def callback2():
        pass

    # No listeners initially
    assert len(bus.get_listeners("test_event")) == 0

    # Add listeners
    bus.subscribe("test_event", callback1)
    bus.subscribe("test_event", callback2)

    # Check listeners count
    listeners = bus.get_listeners("test_event")
    assert len(listeners) == 2
    assert callback1 in listeners
    assert callback2 in listeners


def test_eventbus_clear_listeners():
    """Test clearing listeners for specific event type."""
    bus = EventBus()

    def callback():
        pass

    bus.subscribe("test_event1", callback)
    bus.subscribe("test_event2", callback)

    # Clear one event type
    bus.clear_listeners("test_event1")

    assert len(bus.get_listeners("test_event1")) == 0
    assert len(bus.get_listeners("test_event2")) == 1


def test_eventbus_clear_all_listeners():
    """Test clearing all listeners."""
    bus = EventBus()

    def callback():
        pass

    bus.subscribe("test_event1", callback)
    bus.subscribe("test_event2", callback)

    # Clear all
    bus.clear_all_listeners()

    assert len(bus.get_listeners("test_event1")) == 0
    assert len(bus.get_listeners("test_event2")) == 0


def test_eventbus_publish_no_listeners():
    """Test publishing to event type with no listeners."""
    bus = EventBus()

    # Should not raise any exception
    bus.publish("nonexistent_event", data="test")


def test_eventbus_multiple_args_kwargs():
    """Test publishing events with multiple arguments."""
    bus = EventBus()
    received_args = []
    received_kwargs = {}

    def callback(*args, **kwargs):
        received_args.extend(args)
        received_kwargs.update(kwargs)

    bus.subscribe("test_event", callback)
    bus.publish("test_event", "arg1", "arg2", key1="value1", key2="value2")

    assert "arg1" in received_args
    assert "arg2" in received_args
    assert received_kwargs["key1"] == "value1"
    assert received_kwargs["key2"] == "value2"
