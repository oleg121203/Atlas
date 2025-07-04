"""
Sentry Configuration Module

Sentry integration for error tracking and monitoring.

This module provides integration with Sentry.io for error tracking,
performance monitoring, and crash reporting in Atlas.
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Attempt to import sentry_sdk, but don't fail if it's not installed
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logger.warning("Sentry SDK not installed. Error tracking disabled.")


def init_sentry(
    dsn: str,
    environment: str = "development",
    release: str = "atlas@1.0.0",
    traces_sample_rate: float = 0.2,
    profiles_sample_rate: float = 0.1,
) -> bool:
    """Initialize Sentry SDK for error reporting and performance monitoring.

    Args:
        dsn: Sentry DSN for the project
        environment: Environment name (development, staging, production)
        release: Release version string
        traces_sample_rate: Percentage of transactions to sample for performance
        profiles_sample_rate: Percentage of transactions to sample for profiling

    Returns:
        Boolean indicating whether Sentry was successfully initialized
    """
    if not SENTRY_AVAILABLE:
        logger.warning("Cannot initialize Sentry: SDK not available")
        return False

    if not dsn:
        logger.warning("Cannot initialize Sentry: DSN not provided")
        return False

    try:
        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )

        # Initialize the SDK
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            # Performance monitoring
            traces_sample_rate=traces_sample_rate,
            # Profiling
            profiles_sample_rate=profiles_sample_rate,
            # Integrations
            integrations=[
                logging_integration,
            ],
            # Configure which in-app frames should be captured
            in_app_include=["atlas", "core", "ui", "plugins", "tools"],
        )

        # Set user information if available
        user_id = os.environ.get("ATLAS_USER_ID")
        if user_id:
            sentry_sdk.set_user({"id": user_id})

        logger.info(f"Sentry initialized for environment: {environment}")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def capture_exception(
    exception: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None
) -> str:
    """Capture and report an exception to Sentry.

    Args:
        exception: Exception object to report, or current exception if None
        context: Additional contextual data for the event

    Returns:
        Event ID if captured successfully, empty string otherwise
    """
    if not SENTRY_AVAILABLE:
        logger.warning("Cannot capture exception: Sentry SDK not available")
        return ""

    try:
        # Add extra context to the event
        if context:
            with sentry_sdk.configure_scope() as scope:
                for key, value in context.items():
                    scope.set_extra(key, value)

        # Capture the exception
        return sentry_sdk.capture_exception(exception)
    except Exception as e:
        logger.error(f"Failed to capture exception in Sentry: {e}")
        return ""


def set_tag(key: str, value: str) -> bool:
    """Set a tag for all future events.

    Args:
        key: Tag name
        value: Tag value

    Returns:
        Boolean indicating success
    """
    if not SENTRY_AVAILABLE:
        return False

    try:
        sentry_sdk.set_tag(key, value)
        return True
    except Exception as e:
        logger.error(f"Failed to set Sentry tag: {e}")
        return False


def set_context(name: str, data: Dict[str, Any]) -> bool:
    """Add contextual data to future events.

    Args:
        name: Context name
        data: Context data dictionary

    Returns:
        Boolean indicating success
    """
    if not SENTRY_AVAILABLE:
        return False

    try:
        with sentry_sdk.configure_scope() as scope:
            scope.set_context(name, data)
        return True
    except Exception as e:
        logger.error(f"Failed to set Sentry context: {e}")
        return False


def start_transaction(name: str, op: str) -> Any:
    """Start a performance transaction for profiling.

    Args:
        name: Transaction name
        op: Operation type

    Returns:
        Transaction object or None if not available
    """
    if not SENTRY_AVAILABLE:
        return None

    try:
        return sentry_sdk.start_transaction(name=name, op=op)
    except Exception as e:
        logger.error(f"Failed to start Sentry transaction: {e}")
        return None


import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Attempt to import sentry_sdk, but don't fail if it's not installed
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None
    logger.warning("Sentry SDK not installed. Error tracking disabled.")


def init_sentry(
    dsn: str, environment: str = "development", release: str = "atlas@1.0.0"
):
    """Initialize Sentry SDK for error reporting and performance monitoring.

    Args:
        dsn: Sentry DSN for the project
        environment: Environment name (development, staging, production)
        release: Release version string

    Returns:
        Boolean indicating whether Sentry was successfully initialized
    """
    if not SENTRY_AVAILABLE:
        logger.warning("Cannot initialize Sentry: SDK not available")
        return False

    if not dsn:
        logger.warning("Cannot initialize Sentry: DSN not provided")
        return False

    try:
        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )

        # Initialize the SDK
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            # Performance monitoring
            traces_sample_rate=0.2,
            # Profiling
            profiles_sample_rate=0.1,
            # Integrations
            integrations=[
                logging_integration,
            ],
            # Configure which in-app frames should be captured
            in_app_include=["atlas", "core", "ui", "plugins", "tools"],
        )

        # Set user information if available
        user_id = os.environ.get("ATLAS_USER_ID")
        if user_id:
            sentry_sdk.set_user({"id": user_id})

        logger.info(f"Sentry initialized for environment: {environment}")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def capture_exception(exception: Exception, extra_data: dict = None) -> str:
    """Capture an exception and send it to Sentry.

    Args:
        exception (Exception): The exception to capture.
        extra_data (dict, optional): Additional data to send with the exception.

    Returns:
        str: Event ID if captured successfully, empty string otherwise.
    """
    if sentry_sdk:
        try:
            event_id = sentry_sdk.capture_exception(exception)
            if extra_data is not None:
                with sentry_sdk.push_scope() as scope:
                    for key, value in extra_data.items():
                        scope.set_extra(key, value)
            logger.info(f"Exception captured and sent to Sentry with ID: {event_id}")
            return event_id if event_id else ""
        except Exception as e:
            logger.error(f"Failed to capture exception: {e}")
            return ""
    else:
        logger.warning("Sentry SDK not available, exception not captured")
        return ""


def capture_message(message: str, level: str = "info", extra_data: dict = None) -> str:
    """Capture a custom message and send it to Sentry.

    Args:
        message (str): The message to capture.
        level (str): The severity level ('debug', 'info', 'warning', 'error', 'fatal').
        extra_data (dict, optional): Additional data to send with the message.

    Returns:
        str: Event ID if captured successfully, empty string otherwise.
    """
    if sentry_sdk:
        try:
            # Ensure level is one of the valid options
            valid_levels = ["debug", "info", "warning", "error", "fatal"]
            selected_level = level if level in valid_levels else "info"
            event_id = sentry_sdk.capture_message(message, level=selected_level)
            if extra_data is not None:
                with sentry_sdk.push_scope() as scope:
                    for key, value in extra_data.items():
                        scope.set_extra(key, value)
            logger.info(f"Message captured and sent to Sentry with ID: {event_id}")
            return event_id if event_id else ""
        except Exception as e:
            logger.error(f"Failed to capture message: {e}")
            return ""
    else:
        logger.warning("Sentry SDK not available, message not captured")
        return ""


def set_user(user_id: str, email: str = "", username: str = "") -> None:
    """Set user information for Sentry error tracking.

    Args:
        user_id (str): Unique identifier for the user.
        email (str, optional): User's email address.
        username (str, optional): User's username or display name.
    """
    if sentry_sdk:
        try:
            sentry_sdk.set_user({"id": user_id, "email": email, "username": username})
            logger.info(f"User information set for Sentry: {user_id}")
        except Exception as e:
            logger.error(f"Failed to set user information: {e}")
    else:
        logger.warning("Sentry SDK not available, user information not set")


def start_transaction(name: str, op: str) -> Any:
    """Start a performance transaction for profiling.

    Args:
        name: Transaction name
        op: Operation type

    Returns:
        Transaction object or None if not available
    """
    if not SENTRY_AVAILABLE:
        return None

    try:
        return sentry_sdk.start_transaction(name=name, op=op)
    except Exception as e:
        logger.error(f"Failed to start Sentry transaction: {e}")
        return None
