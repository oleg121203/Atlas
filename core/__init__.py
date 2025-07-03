"""
Core package for Atlas application.

This package contains the central application logic, configuration,
event handling, plugin system, and module registry.
"""

# Core components
from core.application import AtlasApplication
from core.config import Config, ConfigManager, get_config
from core.event_bus import EventBus
from core.module_registry import ModuleBase, ModuleRegistry
from core.plugin_system import PluginBase, PluginSystem
from core.self_healing import SelfHealingManager, SelfHealingSystem

__all__ = [
    "AtlasApplication",
    "Config",
    "ConfigManager",
    "get_config",
    "EventBus",
    "ModuleRegistry",
    "ModuleBase",
    "PluginBase",
    "PluginSystem",
    "SelfHealingSystem",
    "SelfHealingManager",
]
