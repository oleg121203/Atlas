"""
Sentry configuration for Atlas crash reporting.
This module initializes Sentry SDK for monitoring application crashes and errors.
"""

import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration


def init_sentry(
    dsn: str, environment: str = "production", release: str = "atlas@1.0.0"
) -> None:
    """
    Initialize Sentry SDK with the provided DSN and configuration.

    Args:
        dsn (str): Data Source Name for Sentry project.
        environment (str): Deployment environment (e.g., production, staging).
        release (str): Release version of the application.
    """
    sentry_sdk.init(
        dsn=dsn,
        integrations=[AsyncioIntegration()],
        environment=environment,
        release=release,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        # Capture 100% of profiles. In production, reduce this.
        profiles_sample_rate=1.0,
    )
    print("Sentry SDK initialized successfully.")


# Example usage in main application
if __name__ == "__main__":
    # Replace with actual DSN from Sentry project settings
    SENTRY_DSN = "https://examplePublicKey@o0.ingest.sentry.io/0"
    init_sentry(SENTRY_DSN, environment="development", release="atlas@1.0.0")
