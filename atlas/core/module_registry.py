"""
Module registry for dynamic module loading and lifecycle management in Atlas.

This module provides a system for registering, loading, and managing the lifecycle
of application modules, including dependency resolution.
"""

import inspect
import logging
import os
import pkgutil
from typing import Dict, List, Optional, Type

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
    """
    Registry for managing application modules with dependency resolution.

    This class handles the registration, initialization, and lifecycle management
    of all Atlas modules, ensuring proper dependency ordering and error handling.
    """

    def __init__(self, event_bus=None):
        """Initialize the module registry."""
        self._modules: Dict[str, ModuleBase] = {}
        self._module_classes: Dict[str, Type[ModuleBase]] = {}
        self._dependencies: Dict[str, List[str]] = {}
        self._initialization_order: List[str] = []
        self.event_bus = event_bus

    def register_module(
        self, module_class: Type[ModuleBase], name: Optional[str] = None
    ) -> None:
        """
        Register a module class.

        Args:
            module_class: The module class to register
            name: Optional name for the module (defaults to class name)
        """
        module_name = name or module_class.__name__
        self._module_classes[module_name] = module_class

        # Get dependencies if the module implements the method
        if hasattr(module_class, "get_dependencies"):
            dummy_instance = module_class(module_name)
            self._dependencies[module_name] = dummy_instance.get_dependencies()
        else:
            self._dependencies[module_name] = []

        logger.info(f"Registered module: {module_name}")

        if self.event_bus:
            self.event_bus.publish("module_registered", module_name=module_name)

    def initialize_module(self, name: str) -> bool:
        """
        Initialize a specific module and its dependencies.

        Args:
            name: Name of the module to initialize

        Returns:
            bool: True if initialization was successful
        """
        if name in self._modules:
            logger.warning(f"Module {name} is already initialized")
            return True

        if name not in self._module_classes:
            logger.error(f"Module {name} is not registered")
            return False

        try:
            # Initialize dependencies first
            for dep_name in self._dependencies.get(name, []):
                if not self.initialize_module(dep_name):
                    logger.error(
                        f"Failed to initialize dependency {dep_name} for module {name}"
                    )
                    return False

            # Create and initialize the module
            module_class = self._module_classes[name]
            module_instance = module_class(name)
            module_instance.initialize()

            self._modules[name] = module_instance
            logger.info(f"Successfully initialized module: {name}")

            if self.event_bus:
                self.event_bus.publish("module_initialized", module_name=name)

            return True

        except Exception as e:
            logger.error(f"Failed to initialize module {name}: {e}")
            if self.event_bus:
                self.event_bus.publish("module_error", module_name=name, error=str(e))
            return False

    def start_module(self, name: str) -> bool:
        """
        Start a module.

        Args:
            name: Name of the module to start

        Returns:
            bool: True if start was successful
        """
        if name not in self._modules:
            logger.error(f"Module {name} is not initialized")
            return False

        try:
            self._modules[name].start()
            logger.info(f"Started module: {name}")

            if self.event_bus:
                self.event_bus.publish("module_started", module_name=name)

            return True

        except Exception as e:
            logger.error(f"Failed to start module {name}: {e}")
            if self.event_bus:
                self.event_bus.publish("module_error", module_name=name, error=str(e))
            return False

    def stop_module(self, name: str) -> bool:
        """
        Stop a module.

        Args:
            name: Name of the module to stop

        Returns:
            bool: True if stop was successful
        """
        if name not in self._modules:
            logger.warning(f"Module {name} is not running")
            return True

        try:
            self._modules[name].stop()
            logger.info(f"Stopped module: {name}")

            if self.event_bus:
                self.event_bus.publish("module_stopped", module_name=name)

            return True

        except Exception as e:
            logger.error(f"Failed to stop module {name}: {e}")
            if self.event_bus:
                self.event_bus.publish("module_error", module_name=name, error=str(e))
            return False

    def restart_module(self, name: str) -> bool:
        """
        Restart a module.

        Args:
            name: Name of the module to restart

        Returns:
            bool: True if restart was successful
        """
        if name in self._modules:
            if not self.stop_module(name):
                return False
            # Remove from registry to allow reinitialization
            del self._modules[name]

        return self.initialize_module(name) and self.start_module(name)

    def get_module(self, name: str) -> Optional[ModuleBase]:
        """Get a module instance by name."""
        return self._modules.get(name)

    def list_modules(self) -> List[str]:
        """Get a list of all registered module names."""
        return list(self._module_classes.keys())

    def list_active_modules(self) -> List[str]:
        """Get a list of all initialized module names."""
        return list(self._modules.keys())

    def shutdown_all(self) -> None:
        """Shutdown all modules in reverse dependency order."""
        logger.info("Shutting down all modules...")

        # Stop modules in reverse order
        for name in reversed(list(self._modules.keys())):
            self.stop_module(name)

        # Cleanup modules
        for module in self._modules.values():
            try:
                module.cleanup()
            except Exception as e:
                logger.error(f"Error during cleanup of module {module.name}: {e}")

        self._modules.clear()
        logger.info("All modules shutdown complete")


# Auto-discovery functions for modules
def discover_modules(package_path: str) -> List[Type[ModuleBase]]:
    """
    Discover all module classes in a package.

    Args:
        package_path: Path to the package to scan

    Returns:
        List of discovered module classes
    """
    discovered_modules = []

    if not os.path.exists(package_path):
        logger.warning(f"Package path does not exist: {package_path}")
        return discovered_modules

    for importer, modname, _ in pkgutil.iter_modules([package_path]):
        try:
            module = importer.find_module(modname).load_module(modname)

            # Look for ModuleBase subclasses
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, ModuleBase)
                    and obj != ModuleBase
                    and obj.__module__ == module.__name__
                ):
                    discovered_modules.append(obj)
                    logger.info(f"Discovered module: {obj.__name__} in {modname}")

        except Exception as e:
            logger.error(f"Error loading module {modname}: {e}")

    return discovered_modules


def auto_register_modules(registry: ModuleRegistry, package_path: str) -> None:
    """
    Automatically discover and register modules from a package.

    Args:
        registry: The module registry to register modules with
        package_path: Path to the package to scan
    """
    modules = discover_modules(package_path)
    for module_class in modules:
        registry.register_module(module_class)
