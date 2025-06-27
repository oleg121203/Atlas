"""
Atlas Application Core

This module defines the main application class for Atlas, handling initialization,
module and plugin management, and application lifecycle.
"""

import sys
from typing import Any, Dict, Optional

from PySide6.QtWidgets import QApplication

from core.alerting import initialize_alerting, raise_alert
from core.config import ConfigManager, get_config
from core.event_system import EventBus
from core.logging import get_logger, setup_logging
from core.module_registry import MODULE_REGISTRY, initialize_module, load_all_modules
from core.module_system import ModuleRegistry
from core.monitoring import start_monitoring, stop_monitoring
from core.plugin_system import PluginRegistry

try:
    from security.security_utils import check_environment_security, initialize_security
except ImportError:

    def check_environment_security() -> bool:
        print("Security environment check not available, using fallback.")
        return True

    def initialize_security(config=None) -> bool:
        print("Security initialization not available, using fallback.")
        return True


from core.ai_integration import get_ai_model_manager
from core.async_task_manager import AsyncTaskManager
from core.feature_flags import get_feature_flag_manager
from core.network_client import NetworkClient
from core.self_healing import SelfHealingManager, initialize_self_healing
from core.workflow_manager import WorkflowManager
from security.rbac import get_rbac_manager

logger = get_logger("AtlasApplication")


class AtlasApplication:
    """
    Main application class for Atlas.

    Manages application lifecycle, configuration, events, modules, plugins, and UI.
    """

    def __init__(
        self,
        app_name: str = "Atlas",
        version: str = "1.0.0",
        config: Dict[str, Any] = None,
    ):
        """Initialize the Atlas application."""
        if config is None:
            config = {}
        self.app_name = app_name
        self.version = version
        self.config = config
        self.initialized = False

        # Initialize logging first
        setup_logging()

        # Initialize security
        initialize_security()

        # Initialize core components
        self.app: Optional[QApplication] = None
        self.config_manager = ConfigManager()
        self.event_bus = EventBus()
        self.module_registry = ModuleRegistry()
        self.plugin_registry = PluginRegistry()
        self.running = False
        self.network_client = None
        self.rbac_manager = None
        self.feature_flags = None
        self.ai_manager = None
        self.self_healing_manager: Optional[SelfHealingManager] = None
        self.workflow_manager: Optional[WorkflowManager] = None
        self.async_task_manager: Optional[AsyncTaskManager] = None

        # Check environment security
        if not check_environment_security():
            logger.warning(
                "Environment security checks failed, proceeding with caution"
            )
            raise_alert(
                "security",
                "Environment security check failed",
                "Some security requirements are not met in the current environment",
            )

        logger.info("Initializing Atlas application: %s v%s", app_name, version)

    def initialize(self) -> bool:
        """
        Initialize application components.

        Returns:
            bool: True if initialization successful
        """
        if self.initialized:
            logger.info(f"{self.app_name} is already initialized")
            return True

        logger.info(f"Initializing {self.app_name} version {self.version}...")

        try:
            # Initialize logging
            log_config = self.config.get("logging", {})
            setup_logging(
                log_config.get("level", "INFO"),
                log_config.get("file", f"{self.app_name}.log"),
            )
            logger.info("Logging initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize logging: %s", str(e))
            raise_alert(
                "error",
                "Logging Initialization Failed",
                "Logging system could not be initialized. Using default logging settings.",
            )

        try:
            # Initialize alerting
            alert_config = self.config.get("alerting", {})
            initialize_alerting(
                {
                    "enabled": alert_config.get("enabled", True),
                    "channels": alert_config.get("channels", ["qt", "desktop"]),
                    "qt_handler": None,
                }
            )
            logger.info("Alerting system initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize alerting: %s", str(e))
            raise_alert(
                "error",
                "Alerting Initialization Failed",
                "Alerting system could not be initialized. Alerts may not be displayed.",
            )

        try:
            # Initialize monitoring if available
            monitoring_config = self.config.get("monitoring", {})
            if monitoring_config.get("enabled", False):
                start_monitoring(monitoring_config.get("interval", 60))
                logger.info("Monitoring initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize monitoring: %s", str(e))
            raise_alert(
                "error",
                "Monitoring Initialization Failed",
                "Monitoring system could not be initialized. Performance metrics may not be available.",
            )

        try:
            # Initialize network client
            network_config = self.config.get("network", {})
            self.network_client = NetworkClient(
                {
                    "base_url": network_config.get("base_url", ""),
                    "api_key": network_config.get("api_key", ""),
                    "timeout": network_config.get("timeout", 30),
                }
            )
            logger.info("Network client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize network client: %s", str(e))
            raise_alert(
                "error",
                "Network Initialization Failed",
                "Network client could not be initialized. Online features may be unavailable.",
            )

        try:
            # Initialize RBAC manager
            self.rbac_manager = get_rbac_manager()
            logger.info("RBAC manager initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize RBAC manager: %s", str(e))
            raise_alert(
                "error",
                "RBAC Initialization Failed",
                "Role-based access control could not be initialized. Default permissions will be used.",
            )

        try:
            # Initialize feature flags
            self.feature_flags = get_feature_flag_manager()
            logger.info("Feature flags initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize feature flags: %s", str(e))
            raise_alert(
                "error",
                "Feature Flags Initialization Failed",
                "Feature flags could not be initialized. Default feature settings will be used.",
            )

        try:
            # Initialize AI model manager
            self.ai_manager = get_ai_model_manager()
            logger.info("AI model manager initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize AI model manager: %s", str(e))
            raise_alert(
                "error",
                "AI Model Manager Initialization Failed",
                "AI model manager could not be initialized. AI features may be unavailable.",
            )

        try:
            # Initialize self-healing system
            self.self_healing_manager = initialize_self_healing(
                {"plugin_registry": self.plugin_registry}
            )
            logger.info("Self-healing system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize self-healing system: {str(e)}")
            raise_alert(
                "Self-Healing Initialization Failed", f"Error: {str(e)}", "error"
            )

        try:
            # Initialize workflow manager
            self.workflow_manager = WorkflowManager()
            logger.info("Workflow manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize workflow manager: {str(e)}")
            raise_alert(
                "Workflow Manager Initialization Failed", f"Error: {str(e)}", "error"
            )

        try:
            # Initialize async task manager for UI responsiveness
            self.async_task_manager = AsyncTaskManager()
            self.async_task_manager.start()
            logger.info("Async task manager initialized and started")
        except Exception as e:
            logger.error(f"Failed to initialize async task manager: {str(e)}")
            raise_alert(
                "Async Task Manager Initialization Failed", f"Error: {str(e)}", "error"
            )

        try:
            # Run diagnostics and attempt auto-healing if issues are found
            if self.self_healing_manager:
                diagnostics = self.self_healing_manager.diagnose_system()
                issues_detected = any(
                    not status
                    for component in diagnostics.values()
                    for status in component.values()
                )
                if issues_detected:
                    logger.warning("System issues detected during initialization")
                    raise_alert(
                        "System Issues Detected",
                        "Running auto-healing procedures",
                        "warning",
                    )
                    healing_results = self.self_healing_manager.auto_heal()
                    for component_type, component_name, success in healing_results:
                        if success:
                            logger.info(
                                f"Successfully healed {component_type}: {component_name}"
                            )
                            raise_alert(
                                f"Healed {component_type}",
                                f"Successfully restored {component_name}",
                                "info",
                            )
                        else:
                            logger.error(
                                f"Failed to heal {component_type}: {component_name}"
                            )
                            raise_alert(
                                f"Failed to Heal {component_type}",
                                f"Could not restore {component_name}",
                                "error",
                            )
        except Exception as e:
            logger.error(f"Error during system diagnostics and healing: {str(e)}")
            raise_alert(
                "Diagnostics Error", f"Error during diagnostics: {str(e)}", "error"
            )

        try:
            # Initialize security utilities
            security_config = self.config.get("security", {})
            if not initialize_security(security_config):
                logger.warning(
                    "Security initialization failed, proceeding without security features"
                )
                raise_alert(
                    "error",
                    "Security Initialization Failed",
                    "Security utilities could not be initialized. Encryption and other security features may be unavailable.",
                )
            else:
                logger.info("Security utilities initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize security utilities: %s", str(e))
            raise_alert(
                "error",
                "Security Initialization Failed",
                "Security utilities could not be initialized due to an error.",
            )

        # Initialize UI application
        if not self.app:
            self.app = QApplication(sys.argv)
            logger.info("QApplication initialized successfully")

        # Set application context for plugins
        app_context = {
            "app_name": self.app_name,
            "version": self.version,
            "config": get_config(),
            "event_bus": self.event_bus,
        }
        self.plugin_registry.set_application_context(app_context)

        logger.info("Application initialization completed")
        self.initialized = True
        return True

    def start(self) -> bool:
        """
        Start the application and its components.

        Returns:
            bool: True if startup successful
        """
        logger.info("Starting %s application...", self.app_name)
        try:
            # Register core modules
            self._register_modules()
            logger.info("Core modules registered successfully")

            # Discover and load plugins
            self.plugin_registry.discover_plugins()
            plugin_config = get_config().get("plugins", {})
            loaded_plugins = self.plugin_registry.load_plugins(
                plugin_config.get("enabled", [])
            )
            logger.info(
                "Loaded plugins: %s",
                ", ".join(loaded_plugins) if loaded_plugins else "None",
            )
            raise_alert(
                "info",
                "Plugins Loaded",
                f"Loaded {len(loaded_plugins)} plugin(s): {', '.join(loaded_plugins) if loaded_plugins else 'None'}",
            )

            # Start plugins
            started_plugins = self.plugin_registry.start_all_plugins()
            logger.info(
                "Started plugins: %s",
                ", ".join(started_plugins) if started_plugins else "None",
            )

            self.running = True
            logger.info("Application startup completed")
            return True
        except Exception as e:
            logger.error("Startup failed: %s", str(e))
            raise_alert(
                "error",
                "Application Startup Failed",
                f"Failed to start {self.app_name} due to: {str(e)}",
            )
            return False

    def _register_modules(self) -> None:
        """Register core modules."""
        try:
            # Register core modules
            self.module_registry.register_module("chat")
            self.module_registry.register_module("tasks")
            self.module_registry.register_module("agents")
            self.module_registry.register_module("ui")

            # Initialize modules
            for module_name in self.module_registry.get_module_names():
                module = self.module_registry.get_module(module_name)
                if module:
                    logger.info(f"Initialized module: {module_name}")
                else:
                    logger.error(f"Failed to initialize module: {module_name}")
        except Exception as e:
            logger.error(f"Error registering modules: {e}")

    def load_modules(self) -> None:
        """Load all registered modules."""
        logger.info("Loading modules")
        load_all_modules()

        for module_name, module_class in MODULE_REGISTRY.items():
            try:
                logger.debug("Initializing module: %s", module_name)
                module_instance = initialize_module(module_class, self)
                if module_instance:
                    self.module_registry.register_module(module_name, module_instance)
                    logger.info("Module loaded: %s", module_name)
                else:
                    logger.warning(
                        "Module initialization returned None: %s", module_name
                    )
                    raise_alert(
                        "warning",
                        f"Module Initialization Issue: {module_name}",
                        "Module initialized but returned None, possible configuration issue.",
                    )
            except Exception as e:
                logger.error(
                    "Failed to load module %s: %s", module_name, str(e), exc_info=True
                )
                raise_alert("error", f"Module Load Failure: {module_name}", str(e))

    def run(self) -> int:
        """Run the application main loop.

        Returns:
            Exit code from the application.
        """
        if not self.running and not self.start():
            logger.error("Failed to start application")
            return 1

        # Initialize UI module if available
        ui_module = self.module_registry.get_module("ui")
        if ui_module:
            ui_module.show_main_window()

        logger.info("Entering application main loop")
        return self.app.exec()

    def stop(self) -> bool:
        """Stop the application and its components.

        Returns:
            True if stop successful, False otherwise.
        """
        if not self.running:
            logger.warning("Application is not running")
            return True

        logger.info("Stopping %s application...", self.app_name)

        # Stop all plugins
        stopped_plugins = self.plugin_registry.stop_all_plugins()
        if stopped_plugins:
            logger.info(f"Stopped plugins: {', '.join(stopped_plugins)}")

        self.running = False
        logger.info("%s application stopped", self.app_name)
        return True

    def shutdown(self) -> bool:
        """Shut down the application, cleaning up resources.

        Returns:
            True if shutdown successful, False otherwise.
        """
        logger.info("Shutting down %s application...", self.app_name)

        if self.running:
            self.stop()

        # Unload all plugins
        unloaded_plugins = self.plugin_registry.unload_all_plugins()
        if unloaded_plugins:
            logger.info(f"Unloaded plugins: {', '.join(unloaded_plugins)}")

        # Stop monitoring
        stop_monitoring()

        # Close network client
        if self.network_client:
            self.network_client.close()
            logger.info("Network client closed")

        # Save RBAC configuration
        if self.rbac_manager:
            self.rbac_manager.save_config()
            logger.info("RBAC configuration saved")

        try:
            if self.async_task_manager:
                self.async_task_manager.stop()
                logger.info("Async task manager stopped")
        except Exception as e:
            logger.error(f"Error stopping async task manager: {str(e)}")

        logger.info("%s application shutdown complete", self.app_name)
        return True
