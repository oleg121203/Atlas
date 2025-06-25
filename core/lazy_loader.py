"""
Lazy Loader for Atlas

This module provides utilities for lazy loading to prevent circular imports.
"""

from typing import Callable, TypeVar, Generic, Any
import importlib
import sys

T = TypeVar('T')

class LazyLoader(Generic[T]):
    """A class that delays the import of a module or attribute until it is accessed."""
    
    def __init__(self, module_name: str, attribute_name: str = None):
        """Initialize the lazy loader with the module and optional attribute to load.
        
        Args:
            module_name: The name of the module to import.
            attribute_name: The name of the attribute to get from the module (optional).
        """
        self.module_name = module_name
        self.attribute_name = attribute_name
        self._module = None
        self._attribute = None

    def __getattr__(self, name: str) -> Any:
        """Load the module or attribute on first access."""
        if self._module is None:
            try:
                self._module = importlib.import_module(self.module_name)
            except ImportError as e:
                raise ImportError(f"Failed to lazily load module {self.module_name}: {e}")

        if self.attribute_name:
            if self._attribute is None:
                self._attribute = getattr(self._module, self.attribute_name)
            if name == '_attribute':
                return self._attribute
            return getattr(self._attribute, name)
        else:
            return getattr(self._module, name)

    def get(self) -> T:
        """Explicitly get the lazily loaded attribute or module."""
        if self.attribute_name:
            return self.__getattr__('_attribute')
        return self._module

def lazy_import(module_name: str, attribute_name: str = None) -> LazyLoader:
    """Create a lazy loader for the specified module or attribute.
    
    Args:
        module_name: The name of the module to import.
        attribute_name: The name of the attribute to get from the module (optional).
    
    Returns:
        A LazyLoader instance for the specified module or attribute.
    """
    return LazyLoader(module_name, attribute_name)

# Example usage:
# my_module = lazy_import('my_module')
# my_class = lazy_import('my_module', 'MyClass')
# instance = my_class.get()  # Module is imported here
