# Initialize the core module

"""
Core package for Atlas application.

This package contains the central application logic, configuration,
event handling, plugin system, and module registry.
"""

from .application import AtlasApplication
from .event_system import EVENT_BUS, register_module_events, publish_module_event
from .config import CONFIG, ConfigurationError
from .plugin_system import PLUGIN_REGISTRY, PluginBase
from .module_registry import MODULE_REGISTRY, ModuleBase

__all__ = [
    "AtlasApplication",
    "EVENT_BUS",
    "register_module_events",
    "publish_module_event",
    "CONFIG",
    "ConfigurationError",
    "PLUGIN_REGISTRY",
    "PluginBase",
    "MODULE_REGISTRY",
    "ModuleBase",
]
