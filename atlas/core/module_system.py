"""
Module System for Atlas Application

This module provides a registry for managing different modules within the Atlas application.
"""

from typing import Any, Dict


class ModuleRegistry:
    """Registry for managing Atlas modules."""

    def __init__(self):
        self.modules: Dict[str, Any] = {}

    def register_module(self, name, module):
        """
        Register a new module.

        Args:
            name (str): Name of the module.
            module: Module instance.

        Raises:
            ValueError: If a module with the same name is already registered.
        """
        if name in self.modules:
            raise ValueError(f"Module {name} is already registered")
        self.modules[name] = module

    def get_module(self, name: str) -> Any:
        """Get a registered module by name.

        Args:
            name (str): Name of the module.

        Returns:
            The registered module.

        Raises:
            KeyError: If the module is not found.
        """
        if name not in self.modules:
            raise KeyError(f"Module {name} not found")
        return self.modules[name]
        return self.modules.get(name)

    def list_modules(self):
        """
        List all registered modules.

        Returns:
            List of module names.
        """
        return list(self.modules.keys())
