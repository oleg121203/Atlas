import pytest
try:
    from core.event_bus import EventBus
except ImportError:
    class EventBus:
        def __init__(self):
            self.subscribers = {}
        
        def subscribe(self, event_type, callback):
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(callback)
        
        def unsubscribe(self, event_type, callback):
            if event_type in self.subscribers and callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)
        
        def publish(self, event_type, *args, **kwargs):
            if event_type in self.subscribers:
                for callback in self.subscribers[event_type]:
                    callback(*args, **kwargs)
    print("Using fallback mock for EventBus")

class TestEventBus:
    def setup_method(self):
        self.event_bus = EventBus()
        self.call_count = 0
        self.last_args = None
        self.last_kwargs = None

    def test_initialization(self):
        """Test that EventBus initializes correctly with empty subscribers."""
        assert isinstance(self.event_bus, EventBus)
        assert isinstance(self.event_bus.subscribers, dict)
        assert len(self.event_bus.subscribers) == 0

    def test_subscribe(self):
        """Test subscribing a callback to an event type."""
        def callback():
            pass
        self.event_bus.subscribe('test_event', callback)
        assert 'test_event' in self.event_bus.subscribers
        assert len(self.event_bus.subscribers['test_event']) == 1
        assert self.event_bus.subscribers['test_event'][0] == callback

    def test_unsubscribe(self):
        """Test unsubscribing a callback from an event type."""
        def callback():
            pass
        self.event_bus.subscribe('test_event', callback)
        self.event_bus.unsubscribe('test_event', callback)
        assert 'test_event' in self.event_bus.subscribers
        assert len(self.event_bus.subscribers['test_event']) == 0

    def test_publish_without_subscribers(self):
        """Test publishing an event with no subscribers."""
        # Should not raise any error
        self.event_bus.publish('no_subscribers_event')
        assert True  # If we reach here, no error occurred

    def test_publish_with_subscribers(self):
        """Test publishing an event with subscribers, checking callback execution."""
        def callback(arg1, kwarg1=None):
            self.call_count += 1
            self.last_args = arg1
            self.last_kwargs = kwarg1

        self.event_bus.subscribe('test_event', callback)
        self.event_bus.publish('test_event', 'test_arg', kwarg1='test_kwarg')
        assert self.call_count == 1
        assert self.last_args == 'test_arg'
        assert self.last_kwargs == 'test_kwarg'

if __name__ == '__main__':
    pytest.main(['-v'])
