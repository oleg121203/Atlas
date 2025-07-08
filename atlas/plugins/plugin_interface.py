"""
Plugin interface for Atlas plugins
"""

from abc import ABC, abstractmethod


class PluginBase(ABC):
    """Base class for all plugins"""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin"""
        pass

    @abstractmethod
    def run(self) -> None:
        """Run the plugin's main functionality"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up any resources used by the plugin"""
        pass
