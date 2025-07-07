"""
Atlas AI Assistant - Unified AI Platform

A modular, extensible AI assistant platform with advanced capabilities
for task automation, intelligent analysis, and user interaction.
"""

__version__ = "0.3.0"
__author__ = "Atlas Development Team"

# Core module imports
from atlas.core.application import AtlasApplication
from atlas.core.config import Config
from atlas.core.event_bus import EventBus

__all__ = [
    "AtlasApplication",
    "Config",
    "EventBus",
]
