"""
Atlas Application Core

This module defines the main application class for Atlas, handling initialization,
module and plugin management, and application lifecycle.
"""

import logging
import sys
from typing import Dict, Any, Optional, List

from PySide6.QtWidgets import QApplication

from core.config import ConfigManager, get_config
from core.event_system import EventBus
from core.module_system import ModuleRegistry
from core.plugin_system import PluginRegistry
from core.logging import setup_logging, get_logger
from core.monitoring import start_monitoring, stop_monitoring
from core.alerting import initialize_alerting, raise_alert
from core.module_registry import MODULE_REGISTRY, load_all_modules, initialize_module
from security.security_utils import check_environment_security
from core.network_client import NetworkClient
from security.rbac import get_rbac_manager, RBACManager, Role
from core.feature_flags import FeatureFlagManager, get_feature_flag_manager
from core.ai_integration import AIModelManager, get_ai_model_manager

logger = get_logger("AtlasApplication")


class AtlasApplication:
    """
    Main application class for Atlas.
    
    Manages application lifecycle, configuration, events, modules, plugins, and UI.
    """
    def __init__(self, app_name: str = "Atlas", version: str = "1.0.0", config: Dict[str, Any] = {}):
        """Initialize the Atlas application."""
        self.app_name = app_name
        self.version = version
        self.config = config
        self.app: Optional[QApplication] = None
        self.config_manager = ConfigManager()
        self.event_bus = EventBus()
        self.module_registry = ModuleRegistry(self)
        self.plugin_registry = PluginRegistry()
        self.running = False
        self.network_client = None
        self.rbac_manager = None
        self.feature_flags = None
        self.ai_manager = None
        
        # Check environment security
        if not check_environment_security():
            logger.warning("Environment security checks failed, proceeding with caution")
            raise_alert("security", "Environment security check failed", 
                       "Some security requirements are not met in the current environment", 
                       data={"component": "AtlasApplication"})
        
        logger.info("Initializing Atlas application: %s v%s", app_name, version)
    
    def initialize(self) -> bool:
        """
        Initialize application components.
        
        Returns:
            bool: True if initialization successful
        """
        logger.info("Initializing core systems")
        
        # Initialize logging
        log_config = self.config.get("logging", {})
        setup_logging(log_config.get("level", "INFO"), 
                     log_config.get("file", f"{self.app_name}.log"))
        
        # Initialize alerting
        alert_config = self.config.get("alerting", {})
        initialize_alerting({
            "enabled": alert_config.get("enabled", True),
            "channels": alert_config.get("channels", ["qt", "desktop"]),
            "default_severity": alert_config.get("default_severity", "warning")
        })
        logger.info("Alerting system initialized")
        
        # Initialize network client
        self.network_client = NetworkClient()
        logger.info("Network client initialized for secure communications")
        
        # Initialize RBAC manager
        self.rbac_manager = get_rbac_manager()
        # Assign default admin user if configured
        admin_user = self.config.get("security", {}).get("default_admin_user")
        if admin_user and admin_user not in self.rbac_manager.user_roles:
            self.rbac_manager.assign_user_role(admin_user, Role.ADMIN)
            logger.info("Assigned ADMIN role to default user: %s", admin_user)
        logger.info("RBAC manager initialized for access control")
        
        # Initialize feature flags
        self.feature_flags = get_feature_flag_manager()
        flags = self.feature_flags.list_flags()
        logger.info("Feature flags loaded: %s", flags)
        
        # Initialize AI model manager
        self.ai_manager = get_ai_model_manager()
        logger.info("AI model manager initialized with models: %s", list(self.ai_manager.models.keys()))
        
        # Start performance monitoring
        monitoring_config = self.config.get("monitoring", {})
        if monitoring_config.get("enabled", True):
            start_monitoring(
                interval=monitoring_config.get("interval", 60.0),
                cpu_threshold=monitoring_config.get("cpu_threshold", 80.0),
                memory_threshold=monitoring_config.get("memory_threshold", 80.0)
            )
            logger.info("Performance monitoring started")
        else:
            logger.info("Performance monitoring is disabled")
        
        # Load modules
        self.load_modules()
        logger.info("Core systems initialized")
        
        # Initialize configuration
        self.config_manager.load_config()
        
        # Initialize monitoring
        if not start_monitoring():
            logger.warning("Monitoring system failed to initialize")
        
        # Initialize alerting
        if not initialize_alerting():
            logger.warning("Alerting system failed to initialize")
        
        # Initialize security
        if not initialize_security():
            logger.warning("Security system failed to initialize")
            raise_alert(
                "Security Initialization Failed",
                "Security utilities could not be initialized. Encryption and other security features may be unavailable.",
                "error"
            )
        
        # Set application context for plugins
        app_context = {
            "app_name": self.app_name,
            "version": self.version,
            "config": get_config(),
            "event_bus": self.event_bus
        }
        self.plugin_registry.set_application_context(app_context)
        
        logger.info("Application initialization completed")
        return True
    
    def start(self) -> bool:
        """
        Start the application and its components.
        
        Returns:
            bool: True if startup successful
        """
        logger.info("Starting %s application...", self.app_name)
        try:
            # Create Qt Application if not already created
            if self.app is None:
                self.app = QApplication([])
            
            # Register core modules
            self._register_modules()
            
            # Discover and load plugins
            self.plugin_registry.discover_plugins()
            plugin_config = get_config().get("plugins", {})
            loaded_plugins = self.plugin_registry.load_all_plugins(plugin_config)
            logger.info("Loaded plugins: %s", ", ".join(loaded_plugins) if loaded_plugins else "None")
            raise_alert(
                "Plugins Loaded",
                f"Loaded {len(loaded_plugins)} plugin(s): {', '.join(loaded_plugins) if loaded_plugins else 'None'}",
                "info"
            )
            
            # Start plugins
            started_plugins = self.plugin_registry.start_all_plugins()
            logger.info("Started plugins: %s", ", ".join(started_plugins) if started_plugins else "None")
            
            self.running = True
            logger.info("Application startup completed")
            return True
        except Exception as e:
            logger.error("Startup failed: %s", str(e))
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
            except Exception as e:
                logger.error("Failed to load module %s: %s", module_name, str(e), exc_info=True)
                raise_alert("error", f"Module Load Failure: {module_name}", str(e), 
                           data={"module": module_name})
    
    def run(self) -> int:
        """Run the application main loop.
        
        Returns:
            Exit code from the application.
        """
        if not self.running:
            if not self.start():
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
        
        logger.info("%s application shutdown complete", self.app_name)
        return True
