"""
Sentry Configuration Module

This module provides configuration for Sentry crash reporting in the Atlas application.
"""

import logging

logger = logging.getLogger(__name__)

# Sentry SDK might not be installed, so we'll use a placeholder
sentry_sdk = None


def init_sentry(dsn, environment=None, release=None):
    """Stub for Sentry initialization."""
    pass


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
