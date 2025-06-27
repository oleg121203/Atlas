"""Startup Time Optimization for Atlas (ASC-025)

This module implements strategies to reduce the startup time of the Atlas application as part of ASC-025. Techniques include lazy loading of modules and dependencies.
"""

import importlib
import logging
from typing import Any

try:
    from PySide6.QtCore import Qt
except ImportError:
    # Fallback for testing environments where Qt might not be available
    class QtFallback:
        AlignCenter = 0x0004
        TextSingleLine = 0x0100
        black = 0x000000

    Qt = QtFallback()

# Setup logging
logger = logging.getLogger(__name__)


class LazyLoader:
    """Handles lazy loading of heavy modules and dependencies to reduce startup time."""

    def __init__(self):
        self._lazy_modules = {}
        self._loaded_modules = {}
        logger.info("LazyLoader initialized for startup optimization")

    def register_module(self, module_name: str, import_path: str):
        """Register a module to be lazily loaded.

        Args:
            module_name (str): Alias or name for the module.
            import_path (str): Full import path (e.g., 'core.ai_context').
        """
        self._lazy_modules[module_name] = import_path
        logger.info(
            f"Registered module {module_name} for lazy loading from {import_path}"
        )

    def get_module(self, module_name: str) -> Any:
        """Get a module, loading it only if not already loaded.

        Args:
            module_name (str): Name of the registered module.

        Returns:
            Any: The loaded module.

        Raises:
            KeyError: If module_name is not registered.
            ImportError: If the module cannot be imported.
        """
        if module_name not in self._lazy_modules:
            raise KeyError(f"Module {module_name} not registered for lazy loading")

        if module_name not in self._loaded_modules:
            import_path = self._lazy_modules[module_name]
            try:
                self._loaded_modules[module_name] = importlib.import_module(import_path)
                logger.info(f"Lazily loaded module {module_name} from {import_path}")
            except ImportError as e:
                logger.error(f"Failed to lazily load module {module_name}: {e}")
                raise
        return self._loaded_modules[module_name]

    def preload_module(self, module_name: str):
        """Preload a module in advance if needed.

        Args:
            module_name (str): Name of the registered module.
        """
        if (
            module_name in self._lazy_modules
            and module_name not in self._loaded_modules
        ):
            self.get_module(module_name)
            logger.info(f"Preloaded module {module_name}")


def optimize_startup():
    """Optimize startup by setting up lazy loading for heavy modules."""
    lazy_loader = LazyLoader()

    # Register heavy modules for lazy loading
    lazy_loader.register_module("ai_context", "core.ai_context")
    lazy_loader.register_module("cloud_sync", "core.cloud_sync")
    lazy_loader.register_module("plugins", "plugins.manager")

    logger.info("Startup optimization applied with lazy loading for heavy modules")
    return lazy_loader


class SplashScreenManager:
    """Manages a splash screen to improve perceived startup time."""

    def __init__(self):
        self._splash = None
        logger.info("SplashScreenManager initialized")

    def show_splash(self):
        """Show the splash screen during startup."""
        from PySide6.QtGui import QPixmap
        from PySide6.QtWidgets import QSplashScreen

        # Placeholder for splash screen image
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.white)
        self._splash = QSplashScreen(pixmap)
        self._splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self._splash.show()
        logger.info("Splash screen shown")

    def update_progress(self, progress: int, message: str = ""):
        """Update the splash screen with progress information.

        Args:
            progress (int): Progress percentage (0-100).
            message (str): Optional message to display.
        """
        if self._splash:
            self._splash.showMessage(
                f"Loading... {progress}% {message}",
                Qt.AlignCenter | Qt.TextSingleLine,
                Qt.black,
            )
            logger.info(f"Splash screen updated: {progress}% - {message}")

    def close_splash(self):
        """Close the splash screen once startup is complete."""
        if self._splash:
            self._splash.close()
            self._splash = None
            logger.info("Splash screen closed")
