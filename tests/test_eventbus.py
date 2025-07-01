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
