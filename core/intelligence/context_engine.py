import time
from logging import getLogger
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Union

from PySide6.QtCore import QObject, Signal

logger = getLogger(__name__)


class SystemContextProvider:
    """Placeholder for a provider of system context data."""

    def __init__(self, config=None):
        self.config = config or {}

    def __call__(self):
        return {"cpu_usage": 0.5, "memory_usage": 0.7, "disk_space": 0.3}

    def stop(self):
        pass


class UserContextProvider:
    """Placeholder for a provider of user context data."""

    def __init__(self, config=None):
        self.config = config or {}

    def __call__(self):
        return {
            "activity_level": "moderate",
            "last_input": time.time(),
            "preferences": {"theme": "dark"},
        }

    def stop(self):
        pass


class EnvironmentalContextProvider:
    """Placeholder for a provider of environmental context data."""

    def __init__(self, config=None):
        self.config = config or {}

    def __call__(self):
        return {
            "time_of_day": "afternoon",
            "location": "office",
            "network_status": "connected",
        }

    def stop(self):
        pass


class ContextEngine(QObject):
    """Manages context awareness for Atlas, integrating environmental, user, and system contexts."""

    context_updated = Signal(str, dict)

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        parent: Union[QObject, None] = None,
    ):
        """Initialize the ContextEngine with configuration.

        Args:
            config: Optional configuration dictionary for context providers.
            parent: Optional parent QObject for Qt integration.
        """
        super().__init__(parent)
        self.config = config or {}
        self.context_data: Dict[str, Any] = {
            "environmental": {},
            "user": {},
            "system": {},
            "historical": {},
        }
        self.context_providers: Dict[str, Any] = {}
        self.context_listeners: Dict[str, List[Callable[[str, dict], None]]] = {}
        self.is_running = False
        self._update_thread = None
        self._lock = Lock()
        logger.info("ContextEngine initialized with config: %s", self.config)

    def start(self) -> None:
        """Start the context engine to begin collecting and updating context data."""
        if not self.is_running:
            self.is_running = True
            self.initialize_providers()
            logger.info("ContextEngine started")
            self.start_continuous_update()

    def stop(self) -> None:
        """Stop the context engine and any associated providers."""
        if self.is_running:
            self.is_running = False
            if self._update_thread:
                self._update_thread = None
            for provider_id, provider in self.context_providers.items():
                try:
                    if hasattr(provider, "stop"):
                        provider.stop()
                    logger.info("Stopped context provider: %s", provider_id)
                except Exception as e:
                    logger.error("Error stopping provider %s: %s", provider_id, str(e))
            logger.info("ContextEngine stopped")

    def initialize_providers(self) -> None:
        """Initialize default context providers based on configuration."""
        logger.info("Initializing context providers")
        # Initialize providers from configuration
        providers_config = self.config.get("providers", {})
        for category, provider_config in providers_config.items():
            try:
                provider_module = provider_config.get("module")
                provider_class = provider_config.get("class")
                if provider_module and provider_class:
                    module = __import__(provider_module, fromlist=[provider_class])
                    provider_cls = getattr(module, provider_class)
                    provider_instance = provider_cls(provider_config.get("config", {}))
                    self.context_providers[category] = provider_instance
                    logger.info("Initialized provider for category: %s", category)
                else:
                    logger.warning(
                        "Invalid provider configuration for category: %s", category
                    )
            except Exception as e:
                logger.error(
                    "Failed to initialize provider for category %s: %s",
                    category,
                    str(e),
                )

        # Default providers if not specified in config
        if not self.context_providers:
            self.context_providers.update(
                {
                    "system": SystemContextProvider(),
                    "user": UserContextProvider(),
                    "environmental": EnvironmentalContextProvider(),
                }
            )
            logger.info("Initialized default context providers")

    def register_provider(self, category: str, provider: Callable[[], dict]) -> None:
        """Register a context provider for a specific category.

        Args:
            category: The category of context data (e.g., 'system', 'user').
            provider: A callable that returns a dictionary of context data.
        """
        self.context_providers[category] = provider
        logger.info(f"Registered context provider for category: {category}")

    def unregister_provider(self, provider_id: str) -> bool:
        """Unregister a context provider.

        Args:
            provider_id: The ID of the provider to unregister.

        Returns:
            bool: True if successfully unregistered, False otherwise.
        """
        if provider_id in self.context_providers:
            try:
                provider = self.context_providers[provider_id]
                if hasattr(provider, "stop"):
                    provider.stop()
                del self.context_providers[provider_id]
                logger.info("Unregistered context provider: %s", provider_id)
                return True
            except Exception as e:
                logger.error("Error unregistering provider %s: %s", provider_id, str(e))
                return False
        return False

    def register_listener(
        self, listener_id: str, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Register a listener to be notified of context updates.

        Args:
            listener_id: Unique identifier for the listener.
            callback: Function to call when context is updated, with parameters (context_type, context_data).
        """
        if listener_id not in self.context_listeners:
            self.context_listeners[listener_id] = []
        if callback not in self.context_listeners[listener_id]:
            self.context_listeners[listener_id].append(callback)
            logger.info(f"Registered context listener: {listener_id}")

    def unregister_listener(self, listener_id: str) -> bool:
        """Unregister a context listener.

        Args:
            listener_id: The ID of the listener to unregister.

        Returns:
            bool: True if successfully unregistered, False otherwise.
        """
        if listener_id in self.context_listeners:
            del self.context_listeners[listener_id]
            logger.info(f"Unregistered context listener: {listener_id}")
            return True
        return False

    def start_continuous_update(self, interval: int = 60) -> None:
        """Start continuous context updates at the specified interval (in seconds).

        Args:
            interval: Time in seconds between updates.
        """
        if self.is_running:
            logger.warning("Continuous update already running.")
            return

        self.is_running = True
        logger.info(f"Starting continuous context updates every {interval} seconds.")

        import threading

        def update_loop():
            while self.is_running:
                start_time = time.time()
                self.update_all_contexts()
                elapsed = time.time() - start_time
                if elapsed > interval:
                    logger.warning(
                        f"Context update took {elapsed:.2f} seconds, longer than interval {interval}"
                    )
                else:
                    time.sleep(interval - elapsed)

        self._update_thread = threading.Thread(target=update_loop, daemon=True)
        self._update_thread.start()

    def stop_continuous_update(self) -> None:
        """Stop continuous context updates."""
        self.is_running = False
        logger.info("Stopped continuous context updates.")
        if self._update_thread:
            self._update_thread = None

    def update_all_contexts(self) -> None:
        """Update all contexts from registered providers."""
        with self._lock:
            for category, provider in self.context_providers.items():
                try:
                    new_data = provider()
                    for key, value in new_data.items():
                        if (
                            key in self.context_data[category]
                            and self.context_data[category][key] == value
                        ):
                            continue
                        self.context_data[category][key] = value
                        self.notify_listeners(category, {key: value})
                        self.context_updated.emit(category, {key: value})
                    logger.debug(f"Updated context for category: {category}")
                except Exception as e:
                    logger.error(
                        f"Error updating context for category {category}: {str(e)}"
                    )

    def notify_listeners(self, context_type: str, context_data: Dict[str, Any]) -> None:
        """Notify all registered listeners of a context update.

        Args:
            context_type: The type of context being updated.
            context_data: The updated context data.
        """
        for listener_id, callbacks in self.context_listeners.items():
            for callback in callbacks:
                try:
                    callback(context_type, context_data)
                except Exception as e:
                    logger.error(f"Error notifying listener {listener_id}: {str(e)}")

    def get_context(self, category: str) -> Dict[str, Any]:
        """Get the current context data for a specific category.

        Args:
            category: The category of context data to retrieve.

        Returns:
            Dict[str, Any]: The current context data for the category.
        """
        return self.context_data.get(category, {})

    def get_all_contexts(self) -> Dict[str, Any]:
        """Get all current context data.

        Returns:
            Dict[str, Any]: All current context data.
        """
        return self.context_data

    def add_historical_context(self, category: str, key: str, value: Any) -> None:
        """Add data to historical context for trend analysis.

        Args:
            category: The category of context.
            key: The key for the data point.
            value: The value of the data point.
        """
        if category not in self.context_data["historical"]:
            self.context_data["historical"][category] = {}
        if key not in self.context_data["historical"][category]:
            self.context_data["historical"][category][key] = []
        self.context_data["historical"][category][key].append(
            {"timestamp": time.time(), "value": value}
        )
        # Limit history to last 100 entries to prevent unbounded growth
        if len(self.context_data["historical"][category][key]) > 100:
            self.context_data["historical"][category][key] = self.context_data[
                "historical"
            ][category][key][-100:]
        logger.debug(f"Added historical context for {category}.{key}")
        self.notify_listeners("historical", {category: {key: value}})
        self.context_updated.emit("historical", {category: {key: value}})

    def get_historical_context(self, category: str, key: str) -> List[Dict[str, Any]]:
        """Get historical context data for a specific category and key.

        Args:
            category: The category of historical context.
            key: The key for the historical data.

        Returns:
            List[Dict[str, Any]]: List of historical data points with timestamps.
        """
        return self.context_data["historical"].get(category, {}).get(key, [])
