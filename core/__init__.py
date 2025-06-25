# Initialize the core module

"""
Core package for Atlas application.

This package contains the central application logic, configuration,
event handling, plugin system, and module registry.
"""

from core.atlas_application import AtlasApplication
from core.event_system import EventBus
from core.config import ConfigManager, get_config
from core.plugin_system import PluginRegistry, PluginBase, PluginMetadata
from core.module_system import ModuleRegistry
from core.module_base import ModuleBase
from core.network_client import NetworkClient
# Import logging, monitoring, and alerting systems
from core.logging import get_logger, setup_logging, set_log_level, log_performance
from core.monitoring import initialize_monitoring, track_performance, get_performance_stats, register_alert_handler, alert, stop_monitoring
from core.alerting import initialize_alerting, alert as alert_user, SEVERITY_INFO, SEVERITY_WARNING, SEVERITY_ERROR, SEVERITY_CRITICAL, register_ui_alert_handler, register_desktop_alert_handler, register_email_alert_handler, register_webhook_alert_handler

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
    "set_log_level",
    "log_performance",
    "initialize_monitoring",
    "track_performance",
    "get_performance_stats",
    "register_alert_handler",
    "alert",
    "stop_monitoring",
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
]
