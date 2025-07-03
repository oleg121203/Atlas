"""
Main application class for Atlas.

This module defines the central application logic, orchestrating the initialization
and lifecycle management of core systems, modules, and plugins.
"""

import logging
import sys
from typing import Optional

from PySide6.QtWidgets import QApplication

from core.config import Config
from core.event_bus import EventBus
from core.module_registry import ModuleRegistry
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
        self.qt_app: Optional[QApplication] = None
        self.config = Config()
        self.event_bus = EventBus()
        self.module_registry = ModuleRegistry(self.event_bus)
        self.plugin_system = PluginSystem(self.event_bus)

        # Import ToolManager here to avoid circular imports
        from tools.tool_manager import ToolManager

        self.tool_manager = ToolManager(self.event_bus)

        self.self_healing = SelfHealingSystem(self.event_bus)
        self.main_window = None

        # Initialize core systems
        self._initialize_core_systems()

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

        logger.info("Core systems initialized successfully")

    def initialize_ui(self):
        """Initialize the Qt application and main window."""
        if not self.qt_app:
            self.qt_app = QApplication.instance()
            if not self.qt_app:
                self.qt_app = QApplication(sys.argv)

        # Import here to avoid circular imports
        from ui.main_window import AtlasMainWindow

        self.main_window = AtlasMainWindow(
            event_bus=self.event_bus,
            config=self.config,
            plugin_system=self.plugin_system,
            tool_manager=self.tool_manager,
        )

        # Connect application-level events
        self.event_bus.subscribe("app_exit", self.shutdown)

        logger.info("UI initialized successfully")

    def run(self):
        """Start the application event loop."""
        logger.info("Starting Atlas Application")

        try:
            # Initialize UI if not already done
            if not self.main_window:
                self.initialize_ui()

            # Show main window
            self.main_window.show()

            # Publish application started event
            self.event_bus.publish("app_started")

            # Start Qt event loop
            return self.qt_app.exec()

        except Exception as e:
            logger.error(f"Error starting application: {e}")
            self.event_bus.publish("system_error", error=e, component="application")
            return 1

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
