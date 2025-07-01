"""
Module registry for dynamic module loading and lifecycle management in Atlas.

This module provides a system for registering, loading, and managing the lifecycle
of application modules, including dependency resolution.
"""

import importlib
import inspect
import logging
import os
import pkgutil
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class ModuleBase:
    """Base class for all Atlas modules."""

    def __init__(self, name: str):
        """Initialize the module with a name."""
        self.name = name
        self.is_initialized = False

    def initialize(self) -> None:
        """Initialize the module. Override in subclasses."""
        logger.info(f"Initializing module: {self.name}")
        self.is_initialized = True

    def start(self) -> None:
        """Start the module operations. Override in subclasses."""
        logger.info(f"Starting module: {self.name}")

    def stop(self) -> None:
        """Stop the module operations. Override in subclasses."""
        logger.info(f"Stopping module: {self.name}")
        self.is_initialized = False

    def cleanup(self) -> None:
        """Clean up module resources. Override in subclasses."""
        logger.info(f"Cleaning up module: {self.name}")

    def get_dependencies(self) -> List[str]:
        """Return a list of module names this module depends on."""
        return []


class ModuleRegistry:
    """Stub for module registry."""

    def __init__(self):
        pass


# Global module registry instance
MODULE_REGISTRY = ModuleRegistry()

# Registry to store all loaded modules
MODULES: Dict[str, Type[Any]] = {}


def load_all_modules(package_name: str, base_path: Optional[str] = None) -> None:
    """Dynamically load all modules in the specified package.

    Args:
        package_name (str): Name of the package to load modules from
        base_path (Optional[str]): Optional base path for loading modules
    """
    if base_path is None:
        # Get the path of the package
        package = importlib.import_module(package_name)
        base_path = os.path.dirname(package.__file__)

    # Iterate through all modules in the package
    for _, module_name, is_pkg in pkgutil.walk_packages([base_path]):
        full_module_name = f"{package_name}.{module_name}"
        try:
            if is_pkg:
                # If it's a package, recurse into it
                load_all_modules(full_module_name, os.path.join(base_path, module_name))
            else:
                # Import the module
                module = importlib.import_module(full_module_name)
                # Find all classes in the module and register them if they have a name
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, "__name__"):
                        MODULES[f"{full_module_name}.{name}"] = obj
                        print(f"Registered module: {full_module_name}.{name}")
        except Exception as e:
            print(f"Error loading module {full_module_name}: {e}")


def initialize_module(module_class: Type[Any], *args, **kwargs) -> Any:
    """Initialize a module with the given arguments.

    Args:
        module_class (Type[Any]): The class of the module to initialize
        *args: Positional arguments to pass to the module constructor
        **kwargs: Keyword arguments to pass to the module constructor

    Returns:
        Any: Initialized module instance
    """
    return module_class(*args, **kwargs)


def get_module(module_name: str) -> Optional[Type[Any]]:
    """Retrieve a module class by its fully qualified name.

    Args:
        module_name (str): Fully qualified name of the module (e.g., 'package.module.ClassName')

    Returns:
        Optional[Type[Any]]: The module class if found, None otherwise
    """
    return MODULES.get(module_name)


def register_module(module_name: str, module_class: Type[Any]) -> None:
    """Register a module class with a given name.

    Args:
        module_name (str): Name to register the module under
        module_class (Type[Any]): The module class to register
    """
    MODULES[module_name] = module_class
    print(f"Manually registered module: {module_name}")
