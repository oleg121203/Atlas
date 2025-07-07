"""
Lazy Loader for Atlas

This module provides utilities for lazy loading to prevent circular imports.
"""

import importlib
import logging
from types import ModuleType
from typing import Any, Generic, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar("T")


class LazyLoader(Generic[T]):
    """A class that delays the import of a module or attribute until it is accessed."""

    def __init__(self, module_name: str, attribute_name: str = "") -> None:
        """Initialize the lazy loader with the module and optional attribute to load.

        Args:
            module_name: The name of the module to import.
            attribute_name: The name of the attribute to get from the module (optional).
        """
        self.module_name = module_name
        self.attribute_name = attribute_name
        self._module: ModuleType | None = None
        self._attribute: Any = None
        logger.debug(
            f"Initialized LazyLoader for module {module_name} with attribute {attribute_name}"
        )

    def __getattr__(self, name: str) -> T:
        """Load the module or attribute on first access."""
        logger.debug(f"Accessing attribute {name} on LazyLoader for {self.module_name}")
        if name == "_attribute":
            if self._module is None:
                try:
                    self._module = importlib.import_module(self.module_name)
                    logger.debug(
                        f"Module {self.module_name} loaded during attribute access"
                    )
                except ImportError as e:
                    logger.error(
                        f"Failed to load module during attribute access {self.module_name}: {e}"
                    )
                    raise ImportError(
                        f"Failed to lazily load module {self.module_name}: {e}"
                    ) from e
            if self._attribute is None and self.attribute_name:
                self._attribute = getattr(self._module, self.attribute_name)
                logger.debug(f"Attribute {self.attribute_name} loaded")
            return cast(T, self._attribute)
        else:
            if self._module is None:
                try:
                    self._module = importlib.import_module(self.module_name)
                    logger.debug(
                        f"Module {self.module_name} loaded during direct attribute access"
                    )
                except ImportError as e:
                    logger.error(
                        f"Failed to load module during direct attribute access {self.module_name}: {e}"
                    )
                    raise ImportError(
                        f"Failed to lazily load module {self.module_name}: {e}"
                    ) from e
            if self.attribute_name:
                if self._attribute is None:
                    self._attribute = getattr(self._module, self.attribute_name)
                    logger.debug(
                        f"Attribute {self.attribute_name} loaded during direct access"
                    )
                if name == self.attribute_name:
                    return cast(T, self._attribute)
                return cast(T, getattr(self._attribute, name))
            return cast(T, getattr(self._module, name))

    def get(self) -> T:
        logger.debug(
            f"Getting value for module_name={self.module_name}, attribute_name={self.attribute_name}"
        )
        if self.attribute_name:
            logger.debug(f"Attempting to get attribute {self.attribute_name}")
            return self.__getattr__("_attribute")
        else:
            logger.debug("Loading module if not already loaded")
            if self._module is None:
                try:
                    self._module = importlib.import_module(self.module_name)
                    logger.debug(f"Module {self.module_name} loaded successfully")
                except ImportError as e:
                    logger.error(f"Failed to load module {self.module_name}: {e}")
                    raise ImportError(
                        f"Failed to lazily load module {self.module_name}: {e}"
                    ) from e
            logger.debug(f"Returning module {self._module}")
            return cast(T, self._module)


def lazy_import(module_name: str, attribute_name: str = "") -> LazyLoader:
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
