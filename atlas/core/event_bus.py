"""
Event Bus system for Atlas application.

This module provides a centralized event handling system that allows different
components of the application to communicate through a publish-subscribe pattern.
"""

from typing import Any, Callable, Dict, List


class EventBus:
    """
    Central event bus for application-wide event handling.

    The EventBus class implements a publish-subscribe pattern that allows
    loose coupling between different components. Components can subscribe
    to events they are interested in and publish events when something
    significant happens.

    Example:
        ```python
        event_bus = EventBus()

        # Subscribe to an event
        def on_user_login(user_id: str):
            print(f"User {user_id} logged in")

        event_bus.subscribe("user_login", on_user_login)

        # Publish an event
        event_bus.publish("user_login", user_id="123")
        ```
    """

    def __init__(self) -> None:
        """Initialize the event bus with an empty listeners dictionary."""
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    def __iter__(self):
        """Allow iteration over event types in the listeners dictionary."""
        return iter(self._listeners.keys())

    def subscribe(self, event_type: str, callback: Callable[..., Any]) -> None:
        """
        Subscribe a callback function to a specific event type.

        Args:
            event_type (str): The type of event to subscribe to.
            callback (Callable): The function to call when the event is published.
                The callback can accept any number of positional and keyword arguments.

        Raises:
            ValueError: If event_type is empty or None.
            TypeError: If event_type is not a string or callback is not callable.

        Example:
            ```python
            def handle_save(filename: str):
                print(f"File saved: {filename}")

            event_bus.subscribe("file_saved", handle_save)
            ```
        """
        if not event_type:
            raise ValueError("Event type cannot be empty")
        if event_type is None:
            raise ValueError("Event type cannot be None")
        if not isinstance(event_type, str):
            raise TypeError("Event type must be a string")
        if callback is None:
            raise ValueError("Callback cannot be None")
        if not callable(callback):
            raise TypeError("Callback must be callable")

        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[..., Any]) -> None:
        """
        Unsubscribe a callback function from a specific event type.

        Args:
            event_type (str): The type of event to unsubscribe from.
            callback (Callable): The function to remove from the subscribers list.

        Raises:
            ValueError: If event_type is empty or None.
            TypeError: If event_type is not a string.

        Note:
            If the callback is not found in the subscribers list, this method
            does nothing (no exception is raised).

        Example:
            ```python
            event_bus.unsubscribe("file_saved", handle_save)
            ```
        """
        if not event_type:
            raise ValueError("Event type cannot be empty")
        if event_type is None:
            raise ValueError("Event type cannot be None")
        if not isinstance(event_type, str):
            raise TypeError("Event type must be a string")

        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)
            if not self._listeners[event_type]:
                del self._listeners[event_type]

    def publish(self, event_type: str, *args: Any, **kwargs: Any) -> None:
        """
        Publish an event to all subscribed callback functions.

        Args:
            event_type (str): The type of event to publish.
            *args: Positional arguments to pass to the callback functions.
            **kwargs: Keyword arguments to pass to the callback functions.

        Raises:
            ValueError: If event_type is empty or None.
            TypeError: If event_type is not a string.

        Note:
            If no callbacks are subscribed to the event type, this method
            does nothing. All subscribed callbacks are called synchronously
            in the order they were subscribed.

        Example:
            ```python
            # Publish with positional arguments
            event_bus.publish("user_login", "user123", timestamp=datetime.now())

            # Publish with keyword arguments only
            event_bus.publish("data_updated", table="users", count=42)
            ```
        """
        if not event_type:
            raise ValueError("Event type cannot be empty")
        if event_type is None:
            raise ValueError("Event type cannot be None")
        if not isinstance(event_type, str):
            raise TypeError("Event type must be a string")

        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                callback(*args, **kwargs)

    def get_listeners(self, event_type: str) -> List[Callable[..., Any]]:
        """
        Get all callback functions subscribed to a specific event type.

        Args:
            event_type (str): The type of event to get listeners for.

        Returns:
            List[Callable]: A list of callback functions subscribed to the event type.
                Returns an empty list if no callbacks are subscribed.

        Example:
            ```python
            listeners = event_bus.get_listeners("user_login")
            print(f"Number of listeners: {len(listeners)}")
            ```
        """
        return self._listeners.get(event_type, [])

    def clear_listeners(self, event_type: str) -> None:
        """
        Remove all callback functions subscribed to a specific event type.

        Args:
            event_type (str): The type of event to clear all listeners for.

        Example:
            ```python
            event_bus.clear_listeners("user_login")
            ```
        """
        if event_type in self._listeners:
            self._listeners[event_type].clear()

    def clear_all_listeners(self) -> None:
        """
        Remove all callback functions from all event types.

        This method clears the entire event bus, removing all subscriptions.
        Use with caution as this will affect all components using the event bus.

        Example:
            ```python
            # Reset the entire event bus
            event_bus.clear_all_listeners()
            ```
        """
        self._listeners.clear()
