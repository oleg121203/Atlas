"""
UI module for the Atlas application.

This module provides components and utilities for the user interface,
including input validation and UI-specific functionality.
"""

from .main_window import MainWindow
from .config_widget import ConfigWidget
from ui.input_validation import (
    validate_ui_input,
    sanitize_ui_input,
    validate_form_data,
    sanitize_form_data
)

from ui.user_management_widget import UserManagementWidget
from ui.ai_assistant_widget import AIAssistantWidget

__all__ = [
    "MainWindow",
    "ConfigWidget",
    "validate_ui_input",
    "sanitize_ui_input",
    "validate_form_data",
    "sanitize_form_data",
    "UserManagementWidget",
    "AIAssistantWidget"
]