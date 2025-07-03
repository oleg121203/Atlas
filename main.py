# Standard library imports
import argparse
import logging
import os
import sys

# Local imports
try:
    import asyncio
except ImportError:
    asyncio = None

from core.application import AtlasApplication
from sentry_config import init_sentry

# Configure logging before any other code
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Sentry for crash reporting
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
if SENTRY_DSN:
    init_sentry(
        SENTRY_DSN,
        environment=os.environ.get("ATLAS_ENV", "development"),
        release="atlas@1.0.0",
    )
else:
    print("Sentry DSN not found in environment variables. Crash reporting disabled.")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Atlas AI Assistant")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--no-ui", action="store_true", help="Run without GUI")
    return parser.parse_args()


def main():
    """Main entry point for Atlas application."""
    args = parse_arguments()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug mode enabled")

    try:
        # Create and run the Atlas application
        app = AtlasApplication()

        if not args.no_ui:
            return app.run()
        else:
            logger.info("Running Atlas in headless mode")
            # Headless mode implementation would go here
            return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
