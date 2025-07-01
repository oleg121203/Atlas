"""
UI module for the Atlas application.

This module provides components and utilities for the user interface,
including input validation and UI-specific functionality.
"""

# UI module initialization
# This file defines the public API for the ui package

# Import main UI components
try:
    from .main_window import MainWindow
except ImportError as e:
    print(f"MainWindow import failed: {e}")
    print("Using fallback for MainWindow.")

    class MainWindow:
        pass


try:
    from .config_widget import ConfigWidget
except ImportError as e:
    print(f"ConfigWidget import failed: {e}")
    print("Using fallback for ConfigWidget.")

    class ConfigWidget:
        pass


try:
    from .command_palette import CommandPalette
except ImportError as e:
    print(f"CommandPalette import failed: {e}")
    print("Using fallback for CommandPalette.")

    class CommandPalette:
        pass


try:
    from .self_improvement_center import SelfImprovementCenter
except ImportError as e:
    print(f"SelfImprovementCenter import failed: {e}")
    print("Using fallback for SelfImprovementCenter.")

    class SelfImprovementCenter:
        pass


try:
    from ui.input_validation import (
        sanitize_form_data,
        sanitize_ui_input,
        validate_form_data,
        validate_ui_input,
    )
except ImportError as e:
    print(f"input_validation import failed: {e}")
    print("Using fallback for input_validation.")

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

try:
    from ui.user_management_widget import UserManagementWidget
except ImportError as e:
    print(f"UserManagementWidget import failed: {e}")
    print("Using fallback for UserManagementWidget.")

    class UserManagementWidget:
        pass


try:
    from ui.chat.ai_assistant_widget import AIAssistantWidget
except ImportError as e:
    print(f"AIAssistantWidget import failed: {e}")
    print("Using fallback for AIAssistantWidget.")

    class AIAssistantWidget:
        pass


__all__ = [
    "MainWindow",
    "ConfigWidget",
    "validate_ui_input",
    "sanitize_ui_input",
    "validate_form_data",
    "sanitize_form_data",
    "UserManagementWidget",
    "AIAssistantWidget",
    "CommandPalette",
    "SelfImprovementCenter",
]
