"""
Sentry Configuration Module

This module provides configuration for Sentry crash reporting in the Atlas application.
"""

import logging
import os

logger = logging.getLogger(__name__)

# Sentry SDK might not be installed, so we'll use a placeholder
sentry_sdk = None

def init_sentry(dsn: str = "", environment: str = "production", release: str = "atlas@1.0.0") -> bool:
    """Initialize Sentry error tracking.

    Args:
        dsn (str): Data Source Name for Sentry connection.
        environment (str): Environment name (e.g., 'production', 'staging').
        release (str): Release version identifier.

    Returns:
        bool: True if Sentry was initialized successfully, False otherwise.
    """
    global sentry_sdk
    try:
        import sentry_sdk

        # Use environment variable if DSN not provided explicitly
        if not dsn:
            dsn = os.environ.get("SENTRY_DSN", "")

        if not dsn:
            logger.warning("Sentry DSN not found, crash reporting disabled")
            return False

        # Initialize Sentry with provided or environment DSN
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            enable_tracing=True
        )
        logger.info("Sentry initialized for crash reporting")
        return True
    except ImportError:
        logger.warning("Sentry SDK not installed, crash reporting disabled")
        return False
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
            sentry_sdk.set_user({
                "id": user_id,
                "email": email,
                "username": username
            })
            logger.info(f"User information set for Sentry: {user_id}")
        except Exception as e:
            logger.error(f"Failed to set user information: {e}")
    else:
        logger.warning("Sentry SDK not available, user information not set")
