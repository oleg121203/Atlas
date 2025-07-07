"""
Core package for Atlas application.

This package contains the central application logic, configuration,
event handling, plugin system, and module registry.
"""

# Core components
from atlas.core.application import AtlasApplication
from atlas.core.config import Config, ConfigManager, get_config
from atlas.core.event_bus import EventBus
from atlas.core.module_registry import ModuleBase, ModuleRegistry
from atlas.core.plugin_system import PluginBase, PluginSystem
from atlas.core.self_healing import SelfHealingManager, SelfHealingSystem

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
