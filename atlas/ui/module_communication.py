"""Module for standardized cross-module communication protocols.

This module defines a standardized way for different UI modules in the Atlas application
to communicate with each other, ensuring clear and predictable interactions. It uses
a simple event bus mechanism to publish and subscribe to events across modules.
"""

from typing import Any, Callable, Dict

from PySide6.QtCore import QObject, Signal, Slot


class ModuleEventBus(QObject):
    """A centralized event bus for cross-module communication.

    This class allows modules to publish events and subscribe to events from other
    modules, ensuring a decoupled and standardized communication protocol.
    """

    # Custom signal to emit events with a name and optional data
    event_signal = Signal(str, dict)

    def __init__(self):
        """Initialize the event bus."""
        super().__init__()
        self._subscribers: Dict[str, list[Callable[[dict], None]]] = {}

    def subscribe(self, event_name: str, callback: Callable[[dict], None]) -> None:
        """Subscribe a callback function to a specific event.

        Args:
            event_name: The name of the event to subscribe to.
            callback: The function to call when the event is published. The callback
                      should accept a single dictionary argument for event data.
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)
        # Connect the signal to the internal handler if not already connected
        if not hasattr(self, "_signal_connected"):
            self.event_signal.connect(self._handle_event)
            self._signal_connected = True

    def unsubscribe(self, event_name: str, callback: Callable[[dict], None]) -> None:
        """Unsubscribe a callback function from a specific event.

        Args:
            event_name: The name of the event to unsubscribe from.
            callback: The function to remove from the event subscribers.
        """
        if (
            event_name in self._subscribers
            and callback in self._subscribers[event_name]
        ):
            self._subscribers[event_name].remove(callback)
        if event_name in self._subscribers and not self._subscribers[event_name]:
            del self._subscribers[event_name]

    def publish(self, event_name: str, data: dict = None) -> None:
        """Publish an event to all subscribers.

        Args:
            event_name: The name of the event to publish.
            data: Optional dictionary containing event-specific data. If None, an empty dict is used.
        """
        if data is None:
            data = {}
        self.event_signal.emit(event_name, data)

    @Slot(str, dict)
    def _handle_event(self, event_name: str, data: dict) -> None:
        """Internal handler to process events and call subscribers.

        Args:
            event_name: The name of the event.
            data: The data associated with the event.
        """
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"ERROR: Event callback for {event_name} failed: {e}")


# Singleton instance of the event bus for global access
EVENT_BUS = ModuleEventBus()


def register_module_events(
    module: Any, event_mappings: Dict[str, Callable[[dict], None]]
) -> None:
    """Helper function to register multiple event handlers for a module.

    Args:
        module: The module instance registering for events.
        event_mappings: A dictionary mapping event names to callback functions.
    """
    for event_name, callback in event_mappings.items():
        EVENT_BUS.subscribe(event_name, callback)
        print(
            f"DEBUG: Module {module.__class__.__name__} subscribed to event {event_name}"
        )


def publish_module_event(event_name: str, data: dict = None) -> None:
    """Helper function to publish an event to the bus.

    Args:
        event_name: The name of the event to publish.
        data: Optional dictionary containing event-specific data.
    """
    EVENT_BUS.publish(event_name, data)
    print(f"DEBUG: Event {event_name} published with data {data}")
