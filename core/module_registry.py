"""
Module registry for dynamic module loading and lifecycle management in Atlas.

This module provides a system for registering, loading, and managing the lifecycle
of application modules, including dependency resolution.
"""
import logging
from typing import Dict, List, Type, Optional, Set

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
    """Manages module registration, loading, and lifecycle."""

    def __init__(self):
        """Initialize the module registry."""
        self.modules: Dict[str, ModuleBase] = {}
        self.module_classes: Dict[str, Type[ModuleBase]] = {}
        self.dependencies: Dict[str, List[str]] = {}

    def register_module(self, module_name: str, module_class: Type[ModuleBase], dependencies: Optional[List[str]] = None) -> None:
        """Register a module class for later instantiation."""
        self.module_classes[module_name] = module_class
        self.dependencies[module_name] = dependencies or []
        logger.info(f"Registered module: {module_name} with dependencies: {self.dependencies[module_name]}")

    def load_module(self, module_name: str, *args, **kwargs) -> Optional[ModuleBase]:
        """Load and instantiate a specific module."""
        if module_name not in self.module_classes:
            logger.error(f"Module not registered: {module_name}")
            return None

        if module_name in self.modules:
            logger.info(f"Module already loaded: {module_name}")
            return self.modules[module_name]

        # Resolve dependencies first
        for dep in self.dependencies.get(module_name, []):
            if dep not in self.modules:
                logger.info(f"Loading dependency {dep} for module {module_name}")
                self.load_module(dep, *args, **kwargs)

        try:
            module_instance = self.module_classes[module_name](module_name, *args, **kwargs)
            self.modules[module_name] = module_instance
            logger.info(f"Loaded module: {module_name}")
            return module_instance
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
            return None

    def initialize_module(self, module_name: str) -> bool:
        """Initialize a loaded module."""
        if module_name not in self.modules:
            logger.error(f"Module not loaded: {module_name}")
            return False

        module = self.modules[module_name]
        if not module.is_initialized:
            # Initialize dependencies first
            for dep in module.get_dependencies():
                if dep in self.modules and not self.modules[dep].is_initialized:
                    logger.info(f"Initializing dependency {dep} for module {module_name}")
                    self.initialize_module(dep)

            try:
                module.initialize()
                logger.info(f"Initialized module: {module_name}")
                return True
            except Exception as e:
                logger.error(f"Error initializing module {module_name}: {e}")
                return False
        return True

    def start_module(self, module_name: str) -> bool:
        """Start a loaded and initialized module."""
        if module_name not in self.modules:
            logger.error(f"Module not loaded: {module_name}")
            return False

        module = self.modules[module_name]
        if not module.is_initialized:
            if not self.initialize_module(module_name):
                return False

        try:
            module.start()
            logger.info(f"Started module: {module_name}")
            return True
        except Exception as e:
            logger.error(f"Error starting module {module_name}: {e}")
            return False

    def stop_module(self, module_name: str) -> bool:
        """Stop a running module."""
        if module_name not in self.modules:
            logger.error(f"Module not loaded: {module_name}")
            return False

        try:
            self.modules[module_name].stop()
            logger.info(f"Stopped module: {module_name}")
            return True
        except Exception as e:
            logger.error(f"Error stopping module {module_name}: {e}")
            return False

    def cleanup_module(self, module_name: str) -> bool:
        """Clean up a module's resources."""
        if module_name not in self.modules:
            logger.error(f"Module not loaded: {module_name}")
            return False

        try:
            self.modules[module_name].cleanup()
            del self.modules[module_name]
            logger.info(f"Cleaned up module: {module_name}")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up module {module_name}: {e}")
            return False

    def get_module(self, module_name: str) -> Optional[ModuleBase]:
        """Get a module instance by name."""
        return self.modules.get(module_name)

    def get_all_modules(self) -> Dict[str, ModuleBase]:
        """Get all loaded modules."""
        return self.modules

    def resolve_dependencies(self, module_name: str) -> List[str]:
        """Resolve the full dependency graph for a module."""
        if module_name not in self.dependencies:
            return []

        visited: Set[str] = set()
        ordered_deps: List[str] = []

        def dfs(current: str) -> None:
            if current in visited:
                return
            visited.add(current)
            for dep in self.dependencies.get(current, []):
                dfs(dep)
            ordered_deps.append(current)

        dfs(module_name)
        return ordered_deps[:-1]  # Exclude the module itself

# Global module registry instance
MODULE_REGISTRY = ModuleRegistry()
