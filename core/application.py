"""
Main application class for Atlas.

This module defines the central application logic, orchestrating the initialization
and lifecycle management of core systems, modules, and plugins.
"""

import logging
import sys

from PySide6.QtWidgets import QApplication

from core.config import Config
from core.event_bus import EventBus
from core.plugin_system import PluginSystem
from core.self_healing import SelfHealingSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AtlasApplication:
    """
    Main application class that orchestrates all Atlas components.

    This class is responsible for initializing and managing the lifecycle
    of all core systems, modules, and plugins in the Atlas application.
    """

    def __init__(self):
        # Initialize the Atlas application with all core systems
        self.qt_app = None
        self.main_window = None
        self.event_bus = EventBus()
        self.config = self.load_config()
        self.plugin_system = PluginSystem([])
        self.tool_manager = None
        self.memory_manager = None
        logger.info("AtlasApplication initialized")

        self.self_healing = SelfHealingSystem(self.event_bus)

        # Initialize core systems
        self._initialize_core_systems()

    def load_config(self):
        return Config()

    def _initialize_core_systems(self):
        """Initialize all core systems and register event handlers."""
        logger.info("Initializing core systems...")

        # Register self-healing event handlers
        self.event_bus.subscribe("system_error", self.self_healing.handle_error)
        self.event_bus.subscribe("module_failure", self.self_healing.restart_module)

        # Initialize configuration
        self.config.load()

        # Initialize plugin system
        self.plugin_system.initialize()

        # Now initialize tool_manager and memory_manager after imports are resolved
        from data.memory_manager import MemoryManager
        from tools.tool_manager import ToolManager

        self.tool_manager = ToolManager()
        self.memory_manager = MemoryManager()
        logger.info("ToolManager and MemoryManager initialized")

        logger.info("Core systems initialized successfully")

    def initialize_ui(self):
        """Initialize the Qt application and main window."""
        logger.info("Entering initialize_ui method in AtlasApplication")
        logger.info("Starting UI initialization from AtlasApplication")

        # Initialize QApplication first, before any UI imports
        if not self.qt_app:
            self.qt_app = QApplication.instance()
            if not self.qt_app:
                self.qt_app = QApplication(sys.argv)
                logger.info("QApplication initialized")

        # Delay UI imports until after QApplication is initialized
        logger.info("QApplication ready, proceeding with UI imports")
        try:
            logger.debug("Importing ui module")
            import ui

            logger.debug("ui module imported successfully")

            logger.debug("Calling ui.initialize_ui")
            self.main_window = ui.initialize_ui(self)
            logger.debug("ui.initialize_ui completed")

            logger.info(
                "UI initialization completed successfully from AtlasApplication"
            )
        except Exception as e:
            logger.error(
                f"Error during UI initialization in AtlasApplication: {str(e)}",
                exc_info=True,
            )
            raise

        # Connect application-level events
        self.event_bus.subscribe("app_exit", self.shutdown)

        logger.info("UI initialized successfully")

    def run(self):
        """Run the application."""
        logger.info("Starting Atlas application run")
        if not self.qt_app:
            logger.error("QApplication not initialized before run")
            raise RuntimeError(
                "QApplication must be initialized before running the application"
            )
        if not hasattr(self, "main_window") or self.main_window is None:
            logger.error("Main window not initialized before run")
            raise RuntimeError(
                "Main window must be initialized before running the application"
            )
        logger.info("Showing main window")
        self.main_window.show()
        logger.info("Entering Qt event loop")
        exit_code = self.qt_app.exec()
        logger.info(f"Qt event loop exited with code: {exit_code}")
        return exit_code

    def start(self):
        """Start the application without UI (for headless operation)."""
        logger.info("Starting Atlas Application (headless mode)")

        # Initialize tool manager
        if self.tool_manager:
            self.tool_manager.initialize_all_tools()

        # Publish application started event
        self.event_bus.publish("app_started")

        logger.info("Atlas Application started successfully")

    def shutdown(self):
        """Gracefully shutdown the application."""
        logger.info("Shutting down Atlas Application")

        # Publish shutdown event
        self.event_bus.publish("app_shutdown")

        # Cleanup plugin system
        if self.plugin_system:
            self.plugin_system.shutdown()

        # Save configuration
        if self.config:
            self.config.save()

        # Close main window
        if self.main_window:
            self.main_window.close()

        # Quit Qt application
        if self.qt_app:
            self.qt_app.quit()

        logger.info("Application shutdown complete")


if __name__ == "__main__":
    app = AtlasApplication()
    sys.exit(app.run())
