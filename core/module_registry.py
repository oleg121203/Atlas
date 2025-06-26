"""
Module registry for dynamic module loading and lifecycle management in Atlas.

This module provides a system for registering, loading, and managing the lifecycle
of application modules, including dependency resolution.
"""
import logging
from typing import Dict, List, Type, Optional, Set, Any, Callable
from .lazy_loader import lazy_import
import importlib
import pkgutil
import inspect
import os

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
        self.dependencies: Dict[str, List[str]] = {}
        self.lazy_loaders: Dict[str, lazy_import] = {}
        self.state: Dict[str, str] = {}
        logger.info("Module registry initialized")

    def register_module(self, module_name: str, module_class: Type, dependencies: List[str] = None) -> None:
        """Register a module class with optional dependencies."""
        if dependencies is None:
            dependencies = []
        self.modules[module_name] = module_class()
        self.dependencies[module_name] = dependencies
        self.state[module_name] = 'registered'
        logger.info(f"Registered module: {module_name}")

    def load_module(self, module_name: str, *args, **kwargs) -> Optional[ModuleBase]:
        """Load and instantiate a specific module."""
        if module_name not in self.modules:
            logger.error(f"Module not loaded: {module_name}")
            return None

        # Resolve dependencies first
        for dep in self.dependencies.get(module_name, []):
            if dep not in self.modules:
                logger.info(f"Loading dependency {dep} for module {module_name}")
                self.load_module(dep, *args, **kwargs)

        try:
            logger.info(f"Loaded module: {module_name}")
            return self.modules[module_name]
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
            return None

    def get_module(self, module_name: str) -> Optional[ModuleBase]:
        """Get a module instance, loading it if necessary."""
        if module_name in self.lazy_loaders and module_name not in self.modules:
            try:
                module_class = self.lazy_loaders[module_name].get()
                self.modules[module_name] = module_class(module_name)
                logger.info(f"Module lazily loaded: {module_name}")
            except ImportError as e:
                logger.error(f"Failed to lazily load module {module_name}: {e}")
                return None
        return self.modules.get(module_name)

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
                    if inspect.isclass(obj) and hasattr(obj, '__name__'):
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
