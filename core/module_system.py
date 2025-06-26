"""
Module System for Atlas Application

This module provides a registry for managing different modules within the Atlas application.
"""


class ModuleRegistry:
    """Registry for managing Atlas modules."""

    def __init__(self):
        self.modules = {}

    def register_module(self, name, module):
        """
        Register a new module.

        Args:
            name (str): Name of the module.
            module: Module instance.
        """
        self.modules[name] = module

    def get_module(self, name):
        """
        Get a registered module by name.

        Args:
            name (str): Name of the module.

        Returns:
            Module instance if found, None otherwise.
        """
        return self.modules.get(name)

    def list_modules(self):
        """
        List all registered modules.

        Returns:
            List of module names.
        """
        return list(self.modules.keys())
