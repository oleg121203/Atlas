import logging
from typing import Any, Dict, List, Optional

# Set up logging
logger = logging.getLogger(__name__)


class ModuleBase:
    """Base class for all Atlas modules"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.is_initialized = False
        self.config: Dict[str, Any] = {}

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the module with optional configuration

        Args:
            config (Optional[Dict[str, Any]]): Configuration dictionary for the module

        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.config = config or {}
            self.is_initialized = True
            logger.info(f"Module {self.name} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing module {self.name}: {e}")
            self.is_initialized = False
            return False

    def shutdown(self) -> None:
        """Shut down the module and release resources"""
        try:
            self.is_initialized = False
            logger.info(f"Module {self.name} shut down")
        except Exception as e:
            logger.error(f"Error shutting down module {self.name}: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the module

        Returns:
            Dict[str, Any]: Status information about the module
        """
        return {
            "name": self.name,
            "initialized": self.is_initialized,
            "description": self.description,
        }

    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Handle an event dispatched to the module

        Args:
            event_type (str): Type of event
            event_data (Any): Data associated with the event

        Returns:
            bool: True if event was handled, False otherwise
        """
        logger.debug(f"Module {self.name} received event: {event_type}")
        return False

    def get_supported_events(self) -> List[str]:
        """Get list of event types this module can handle

        Returns:
            List[str]: List of supported event types
        """
        return []
