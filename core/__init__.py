# Initialize the core module

"""
Core package for Atlas application.

This package contains the central application logic, configuration,
event handling, plugin system, and module registry.
"""

# Core components
from core.atlas_application import AtlasApplication
from core.module_system import ModuleRegistry
from core.logging import setup_logging, get_logger

from core.event_system import EventBus
from core.config import ConfigManager, get_config
try:
    from core.plugin_system import PluginRegistry, PluginBase, PluginMetadata
except ImportError as e:
    print(f"Plugin system import failed: {e}")
    print("Using fallback for plugin system components.")
    class PluginRegistry:
        pass
    class PluginBase:
        pass
    class PluginMetadata:
        def __init__(self, name, version, description, author, category, dependencies=None):
            self.name = name
            self.version = version
            self.description = description
            self.author = author
            self.category = category
            self.dependencies = dependencies or []
        def to_dict(self):
            return {
                'name': self.name,
                'version': self.version,
                'description': self.description,
                'author': self.author,
                'category': self.category,
                'dependencies': self.dependencies
            }
from core.module_base import ModuleBase
try:
    from core.module_base import ModuleBase
except ImportError as e:
    print(f"Module base import failed: {e}")
    print("Using fallback for ModuleBase.")
    class ModuleBase:
        def __init__(self, name, description=""):
            self.name = name
            self.description = description
            self.is_initialized = False
            self.config = {}
        def initialize(self, config=None):
            self.config = config or {}
            self.is_initialized = True
            return True
        def shutdown(self):
            self.is_initialized = False
        def get_status(self):
            return {
                "name": self.name,
                "initialized": self.is_initialized,
                "description": self.description
            }
        def handle_event(self, event_type, event_data):
            return False
        def get_supported_events(self):
            return []
from core.network_client import NetworkClient
# Import logging, monitoring, and alerting systems
from core.monitoring import initialize_monitoring, track_performance, get_performance_stats, register_alert_handler, alert, stop_monitoring, start_monitoring
from core.alerting import initialize_alerting, alert as alert_user, SEVERITY_INFO, SEVERITY_WARNING, SEVERITY_ERROR, SEVERITY_CRITICAL, register_ui_alert_handler, register_desktop_alert_handler, register_email_alert_handler, register_webhook_alert_handler, raise_alert

__all__ = [
    "AtlasApplication",
    "EventBus",
    "ConfigManager",
    "get_config",
    "PluginRegistry",
    "PluginBase",
    "PluginMetadata",
    "ModuleRegistry",
    "ModuleBase",
    "NetworkClient",
    "get_logger",
    "setup_logging",
    "log_performance",
    "initialize_monitoring",
    "track_performance",
    "get_performance_stats",
    "register_alert_handler",
    "alert",
    "stop_monitoring",
    "start_monitoring",
    "initialize_alerting",
    "alert_user",
    "SEVERITY_INFO",
    "SEVERITY_WARNING",
    "SEVERITY_ERROR",
    "SEVERITY_CRITICAL",
    "register_ui_alert_handler",
    "register_desktop_alert_handler",
    "register_email_alert_handler",
    "register_webhook_alert_handler",
    "raise_alert",
]
