"""
Sentry configuration for Atlas application.
"""

import logging

logger = logging.getLogger(__name__)


def init_sentry(dsn: str, environment: str = "development", release: str = "1.0.0"):
    """
    Initialize Sentry for error tracking.

    Args:
        dsn: Sentry DSN string
        environment: Environment name (development, production, etc.)
        release: Release version
    """
    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            traces_sample_rate=1.0,
        )
        logger.info(f"Sentry initialized for {environment} environment")
    except ImportError:
        logger.warning("Sentry SDK not installed, skipping error tracking setup")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def capture_exception(exception):
    """
    Capture exception with Sentry if available.

    Args:
        exception: Exception to capture
    """
    try:
        import sentry_sdk

        sentry_sdk.capture_exception(exception)
    except ImportError:
        logger.warning("Sentry SDK not available, exception not captured")
    except Exception as e:
        logger.error(f"Failed to capture exception: {e}")


def capture_message(message, level="info"):
    """
    Capture message with Sentry if available.

    Args:
        message: Message to capture
        level: Log level (info, warning, error, etc.)
    """
    try:
        import sentry_sdk

        sentry_sdk.capture_message(message, level)
    except ImportError:
        logger.warning("Sentry SDK not available, message not captured")
    except Exception as e:
        logger.error(f"Failed to capture message: {e}")


def set_context(key, data):
    """
    Set context data for Sentry if available.

    Args:
        key: Context key
        data: Context data
    """
    try:
        import sentry_sdk

        sentry_sdk.set_context(key, data)
    except ImportError:
        logger.warning("Sentry SDK not available, context not set")
    except Exception as e:
        logger.error(f"Failed to set context: {e}")


def set_user(user_data):
    """
    Set user data for Sentry if available.

    Args:
        user_data: User data dictionary
    """
    try:
        import sentry_sdk

        sentry_sdk.set_user(user_data)
    except ImportError:
        logger.warning("Sentry SDK not available, user not set")
    except Exception as e:
        logger.error(f"Failed to set user: {e}")


def start_transaction(name, op="ui"):
    """
    Start a Sentry transaction if available.

    Args:
        name: Transaction name
        op: Operation type
    """
    try:
        import sentry_sdk

        return sentry_sdk.start_transaction(name=name, op=op)
    except ImportError:
        logger.warning("Sentry SDK not available, transaction not started")
        return None
    except Exception as e:
        logger.error(f"Failed to start transaction: {e}")
        return None
