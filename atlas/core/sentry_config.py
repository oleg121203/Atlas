"""Sentry configuration and error reporting for Atlas application.

This module provides a centralized error reporting system that integrates with Sentry.io
for tracking errors, exceptions, and performance issues in the Atlas application.
"""

import logging
import os
from typing import Any, Dict, Optional

# Try to import sentry_sdk, but don't require it
SENTRY_AVAILABLE = False
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    pass

logger = logging.getLogger(__name__)


class SentryManager:
    """Manager for Sentry error reporting and performance monitoring.

    This class provides a centralized way to configure Sentry and report errors,
    messages, and performance issues to Sentry.io for monitoring and debugging.

    Attributes:
        is_initialized (bool): Whether Sentry has been successfully initialized
        environment (str): The current deployment environment (dev, staging, prod)
        user_context (Dict): Current user context information
    """

    def __init__(self):
        """Initialize the Sentry manager."""
        self.is_initialized = False
        self.environment = os.environ.get("ATLAS_ENV", "development")
        self.user_context = {}
        self._initialize()

    def _initialize(self) -> bool:
        """Initialize the Sentry SDK with proper configuration.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if not SENTRY_AVAILABLE:
            logger.info("Sentry SDK not available. Error reporting disabled.")
            return False

        # Get DSN from environment variable
        dsn = os.environ.get("SENTRY_DSN")
        if not dsn:
            logger.info("Sentry DSN not configured. Error reporting disabled.")
            return False

        try:
            # Configure logging integration
            logging_integration = LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR,  # Send errors as events
            )

            # Initialize Sentry SDK
            sentry_sdk.init(
                dsn=dsn,
                environment=self.environment,
                traces_sample_rate=0.1,  # Capture 10% of transactions for performance
                integrations=[logging_integration],
                release=os.environ.get("ATLAS_VERSION", "0.1.0"),
                max_breadcrumbs=50,
                send_default_pii=False,  # Don't send personally identifiable info
            )

            self.is_initialized = True
            logger.info(f"Sentry initialized for environment: {self.environment}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
            return False

    def capture_exception(self, exception: Optional[Exception] = None) -> Optional[str]:
        """Capture an exception and send to Sentry.

        Args:
            exception: The exception to capture, or None to capture current exception

        Returns:
            Optional[str]: Event ID if sent successfully, None otherwise
        """
        if not self.is_initialized or not SENTRY_AVAILABLE:
            logger.warning("Sentry not initialized. Exception not reported.")
            return None

        try:
            event_id = sentry_sdk.capture_exception(exception)
            logger.debug(f"Exception reported to Sentry. Event ID: {event_id}")
            return event_id
        except Exception as e:
            logger.error(f"Failed to report exception to Sentry: {e}")
            return None

    def capture_message(
        self, message: str, level: str = "info", tags: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Capture a message and send to Sentry.

        Args:
            message: The message to capture
            level: The level of the message (debug, info, warning, error)
            tags: Optional tags to associate with the message

        Returns:
            Optional[str]: Event ID if sent successfully, None otherwise
        """
        if not self.is_initialized or not SENTRY_AVAILABLE:
            logger.warning("Sentry not initialized. Message not reported.")
            return None

        try:
            with sentry_sdk.configure_scope() as scope:
                if tags:
                    for key, value in tags.items():
                        scope.set_tag(key, value)

            event_id = sentry_sdk.capture_message(message, level=level)
            logger.debug(f"Message reported to Sentry. Event ID: {event_id}")
            return event_id
        except Exception as e:
            logger.error(f"Failed to report message to Sentry: {e}")
            return None

    def set_user(
        self, user_id: str, email: Optional[str] = None, username: Optional[str] = None
    ) -> None:
        """Set the current user context for Sentry events.

        Args:
            user_id: The user's ID
            email: The user's email address
            username: The user's username
        """
        if not self.is_initialized or not SENTRY_AVAILABLE:
            return

        try:
            user_context = {"id": user_id}
            if email:
                user_context["email"] = email
            if username:
                user_context["username"] = username

            sentry_sdk.set_user(user_context)
            self.user_context = user_context
            logger.debug(f"Set Sentry user context: {user_id}")
        except Exception as e:
            logger.error(f"Failed to set Sentry user context: {e}")

    def clear_user(self) -> None:
        """Clear the current user context for Sentry events."""
        if not self.is_initialized or not SENTRY_AVAILABLE:
            return

        try:
            sentry_sdk.set_user(None)
            self.user_context = {}
            logger.debug("Cleared Sentry user context")
        except Exception as e:
            logger.error(f"Failed to clear Sentry user context: {e}")

    def start_transaction(self, name: str, op: str) -> Any:
        """Start a performance transaction for monitoring.

        Args:
            name: The transaction name
            op: The operation type

        Returns:
            Any: Transaction object or None if Sentry is not initialized
        """
        if not self.is_initialized or not SENTRY_AVAILABLE:
            return None

        try:
            transaction = sentry_sdk.start_transaction(name=name, op=op)
            return transaction
        except Exception as e:
            logger.error(f"Failed to start Sentry transaction: {e}")
            return None

    def set_tag(self, key: str, value: str) -> None:
        """Set a tag for the current scope.

        Args:
            key: The tag key
            value: The tag value
        """
        if not self.is_initialized or not SENTRY_AVAILABLE:
            return

        try:
            sentry_sdk.set_tag(key, value)
            logger.debug(f"Set Sentry tag: {key}={value}")
        except Exception as e:
            logger.error(f"Failed to set Sentry tag: {e}")

    def set_context(self, name: str, context: Dict[str, Any]) -> None:
        """Set a context for the current scope.

        Args:
            name: The context name
            context: The context data dictionary
        """
        if not self.is_initialized or not SENTRY_AVAILABLE:
            return

        try:
            with sentry_sdk.configure_scope() as scope:
                scope.set_context(name, context)
            logger.debug(f"Set Sentry context: {name}")
        except Exception as e:
            logger.error(f"Failed to set Sentry context: {e}")

    def add_breadcrumb(
        self,
        category: str,
        message: str,
        level: str = "info",
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a breadcrumb to the current scope.

        Args:
            category: The breadcrumb category
            message: The breadcrumb message
            level: The breadcrumb level (debug, info, warning, error)
            data: Additional data for the breadcrumb
        """
        if not self.is_initialized or not SENTRY_AVAILABLE:
            return

        try:
            sentry_sdk.add_breadcrumb(
                category=category, message=message, level=level, data=data
            )
            logger.debug(f"Added Sentry breadcrumb: {category} - {message}")
        except Exception as e:
            logger.error(f"Failed to add Sentry breadcrumb: {e}")


# Singleton instance
_instance = None


def get_sentry_manager() -> SentryManager:
    """Get the global Sentry manager instance.

    Returns:
        SentryManager: Singleton instance of SentryManager
    """
    global _instance
    if _instance is None:
        _instance = SentryManager()
    return _instance


def init_sentry(dsn: str, environment: str = "development", release: str = "1.0.0"):
    """
    Initialize Sentry for error tracking.

    Args:
        dsn: Sentry DSN string
        environment: Environment name (development, production, etc.)
        release: Release version
    """
    if not SENTRY_AVAILABLE:
        logger.warning("Sentry SDK not installed, skipping error tracking setup")
        return

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            traces_sample_rate=1.0,
        )
        logger.info(f"Sentry initialized for {environment} environment")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def capture_exception(exception):
    """
    Capture exception with Sentry if available.

    Args:
        exception: Exception to capture
    """
    if not SENTRY_AVAILABLE:
        logger.warning("Sentry SDK not available, exception not captured")
        return

    try:
        sentry_sdk.capture_exception(exception)
    except Exception as e:
        logger.error(f"Failed to capture exception: {e}")


def capture_message(message, level="info"):
    """
    Capture message with Sentry if available.

    Args:
        message: Message to capture
        level: Log level (info, warning, error, etc.)
    """
    if not SENTRY_AVAILABLE:
        logger.warning("Sentry SDK not available, message not captured")
        return

    try:
        sentry_sdk.capture_message(message, level)
    except Exception as e:
        logger.error(f"Failed to capture message: {e}")
