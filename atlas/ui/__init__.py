"""
UI module for the Atlas application.

This module provides the user interface components built with PySide6 that
form the visual interface of the Atlas application.
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Define UI themes
THEMES = {
    "cyberpunk": "cyberpunk.qss",
    "dark": "dark.qss",
    "light": "light.qss",
}

# Default theme
DEFAULT_THEME = "cyberpunk"

# Ensure PySide6 is imported first to avoid conflicts
try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError as e:
    logger.error(f"Failed to import PySide6: {e}")
    logger.error(
        "Atlas requires PySide6 to be installed. Please install it with 'pip install PySide6'"
    )
    QtCore = None
    QtWidgets = None
    QtGui = None


def apply_theme(app: "QtWidgets.QApplication", theme_name: str = DEFAULT_THEME) -> bool:
    """Apply a theme to the application.

    Args:
        app: The QApplication instance
        theme_name: Name of the theme to apply

    Returns:
        bool: True if theme was applied successfully, False otherwise
    """
    if QtWidgets is None:
        logger.error("Cannot apply theme: PySide6 not imported")
        return False

    if not isinstance(app, QtWidgets.QApplication):
        logger.error(f"Invalid application object: {type(app)}")
        return False

    if theme_name not in THEMES:
        logger.warning(
            f"Theme '{theme_name}' not found, using default: {DEFAULT_THEME}"
        )
        theme_name = DEFAULT_THEME

    theme_file = THEMES[theme_name]
    theme_path = os.path.join(os.path.dirname(__file__), "themes", theme_file)

    if not os.path.exists(theme_path):
        logger.error(f"Theme file not found: {theme_path}")
        return False

    try:
        with open(theme_path, "r") as f:
            stylesheet = f.read()
        app.setStyleSheet(stylesheet)
        logger.info(f"Applied theme: {theme_name}")
        return True
    except Exception as e:
        logger.error(f"Error applying theme {theme_name}: {e}")
        return False


def create_module(
    module_name: str, event_bus: Any = None, **kwargs
) -> Optional["QtWidgets.QWidget"]:
    """Create a UI module by name.

    Args:
        module_name: Name of the module to create
        event_bus: Event bus instance to pass to the module
        **kwargs: Additional keyword arguments to pass to the module constructor

    Returns:
        Optional[QtWidgets.QWidget]: The created module widget, or None if creation failed
    """
    if QtWidgets is None:
        logger.error("Cannot create module: PySide6 not imported")
        return None

    try:
        # Import the module dynamically
        module_path = f"ui.{module_name}"
        module_class_name = (
            "".join(word.capitalize() for word in module_name.split("_")) + "Module"
        )

        # Try alternative naming conventions if the first one fails
        alternatives = [
            module_class_name,
            module_name.capitalize() + "Module",
            module_name.capitalize(),
            "".join(word.capitalize() for word in module_name.split("_")),
        ]

        for class_name in alternatives:
            try:
                # Try to import the module
                module = __import__(module_path, fromlist=[class_name])

                if hasattr(module, class_name):
                    # Get the class and instantiate it
                    module_class = getattr(module, class_name)
                    instance = module_class(event_bus=event_bus, **kwargs)
                    logger.info(f"Created UI module: {module_name} ({class_name})")
                    return instance
            except (ImportError, AttributeError):
                continue

        # If we get here, we couldn't find the module class
        logger.error(f"Could not find class for UI module: {module_name}")
        return None
    except Exception as e:
        logger.error(f"Error creating UI module {module_name}: {e}")
        return None


def initialize_ui(app):
    """Initialize the UI components for the application."""
    logger.info("Starting UI initialization")
    try:
        logger.debug("Importing AtlasMainWindow")
        from .main_window import AtlasMainWindow

        logger.debug("AtlasMainWindow imported successfully")

        logger.debug("Creating AtlasMainWindow instance")
        main_window = AtlasMainWindow(app)
        logger.debug("AtlasMainWindow instance created")

        logger.debug("Calling setup_ui on AtlasMainWindow")
        main_window.setup_ui()
        logger.debug("setup_ui completed")

        logger.info("UI initialization completed successfully")
        return main_window
    except Exception as e:
        logger.error(f"Error during UI initialization: {str(e)}", exc_info=True)
        raise


__all__ = ["apply_theme", "create_module", "THEMES", "DEFAULT_THEME"]

# Import main UI components to make them available from the ui package
try:
    from .main_window import AtlasMainWindow

    __all__.append("AtlasMainWindow")
except ImportError as e:
    logger.warning(f"Could not import AtlasMainWindow: {e}")

# Remove unused module imports to fix linting issues
# These modules are imported but not actually used in __all__

logger.info("Starting UI package initialization")
try:
    # Ensure all UI submodules are properly initialized
    try:
        # Dynamically import all submodules
        ui_path = Path(__file__).parent
        ui_modules = [
            p.name
            for p in ui_path.iterdir()
            if p.is_dir() and not p.name.startswith("__")
        ]

        logger.info(f"Discovered UI modules: {', '.join(ui_modules)}")

        # Required UI modules that must be present
        required_modules = ["chat", "tasks", "agents", "plugins", "settings", "stats"]
        missing_modules = [m for m in required_modules if m not in ui_modules]

        if missing_modules:
            logger.warning(f"Missing required UI modules: {', '.join(missing_modules)}")

        # Import each module with detailed logging
        for module in ui_modules:
            try:
                logger.info(f"Attempting to import UI module: {module}")
                __import__(f"ui.{module}")
                logger.debug(f"Imported UI module: {module}")
            except ImportError as e:
                logger.error(f"Failed to import UI module '{module}': {e}")
            except Exception as e:
                logger.error(
                    f"Error initializing UI module '{module}': {e}", exc_info=True
                )
    except Exception as e:
        logger.error(f"Error during UI submodule initialization: {e}", exc_info=True)

    # UI module initialization
    # This file defines the public API for the ui package

    # Import main UI components
    # Temporarily commenting out individual try blocks to isolate syntax error

    # Using a single try block for all imports to avoid syntax issues
    try:
        from atlas.ui.chat.ai_assistant_widget import AIAssistantWidget
        from atlas.ui.input_validation import (
            sanitize_form_data,
            sanitize_ui_input,
            validate_form_data,
            validate_ui_input,
        )
        from atlas.ui.user_management_widget import UserManagementWidget

        from .command_palette import CommandPalette
        from .main_window import AtlasMainWindow
        from .self_improvement_center import SelfImprovementCenter
        from .settings.config_widget import ConfigWidget
    except ImportError as e:
        print(f"UI component import failed: {e}")
        print("Using fallback for UI components.")

        class AtlasMainWindow:
            pass

        class ConfigWidget:
            pass

        class CommandPalette:
            pass

        class SelfImprovementCenter:
            pass

        class InputValidation:
            @staticmethod
            def validate_ui_input(*args, **kwargs):
                pass

            @staticmethod
            def sanitize_ui_input(*args, **kwargs):
                pass

            @staticmethod
            def validate_form_data(*args, **kwargs):
                pass

            @staticmethod
            def sanitize_form_data(*args, **kwargs):
                pass

        validate_ui_input = InputValidation.validate_ui_input
        sanitize_ui_input = InputValidation.sanitize_ui_input
        validate_form_data = InputValidation.validate_form_data
        sanitize_form_data = InputValidation.sanitize_form_data

        class UserManagementWidget:
            pass

        class AIAssistantWidget:
            pass

    from . import context, developer, stats

    __all__ = [
        "AtlasMainWindow",
        "ConfigWidget",
        "validate_ui_input",
        "sanitize_ui_input",
        "validate_form_data",
        "sanitize_form_data",
        "UserManagementWidget",
        "AIAssistantWidget",
        "CommandPalette",
        "SelfImprovementCenter",
        "context",
        "developer",
        "stats",
    ]
    logger.info("UI package initialization completed")
except Exception as e:
    logger.error(f"Error initializing UI package: {str(e)}", exc_info=True)
    raise
