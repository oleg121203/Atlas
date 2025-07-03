"""
Centralized event handling system for Atlas.

This module provides a unified event bus for inter-module communication,
allowing different components to publish and subscribe to events.
"""

import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    """Central event bus for publishing and subscribing to events."""

    def __init__(self):
        """Initialize the event bus with an empty subscriber dictionary."""
        self._subscribers: Dict[str, List[Callable[..., None]]] = {}

    def __iter__(self):
        """Allow iteration over event types in the subscribers dictionary."""
        return iter(self._subscribers.keys())

    def subscribe(self, event_type: str, callback: Callable[..., None]) -> None:
        """Subscribe a callback function to a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable[..., None]) -> None:
        """Unsubscribe a callback function from a specific event type."""
        if (
            event_type in self._subscribers
            and callback in self._subscribers[event_type]
        ):
            self._subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from event: {event_type}")

    def publish(self, event_type: str, *args: Any, **kwargs: Any) -> None:
        """Publish an event to all subscribed callbacks."""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in callback for event {event_type}: {e}")
        logger.debug(f"Published event: {event_type}")


# Global event bus instance
EVENT_BUS = EventBus()


def register_module_events(module_name: str, events: List[str]) -> None:
    """Register events for a specific module."""
    logger.info(f"Registering events for module: {module_name}")
    for event in events:
        logger.debug(f"Event registered: {event} for module: {module_name}")


def publish_module_event(
    module_name: str, event_type: str, *args: Any, **kwargs: Any
) -> None:
    """Publish an event for a specific module."""
    full_event_type = f"{module_name}.{event_type}"
    EVENT_BUS.publish(full_event_type, *args, **kwargs)
    logger.debug(f"Module event published: {full_event_type} by module: {module_name}")
