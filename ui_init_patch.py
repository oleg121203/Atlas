"""
Patch file to update import statements in ui/__init__.py for new UI directory structure.
"""

import logging

from ui.agents.user_management_widget import UserManagementWidget

logger = logging.getLogger(__name__)

# Import input validation functions with error handling
try:
    from ui.input_validation import (
        sanitize_form_data,
        sanitize_ui_input,
        validate_form_data,
        validate_ui_input,
    )
except ImportError as e:
    logger.error(f"Input validation functions import failed: {e}")

    class InputValidation:
        @staticmethod
        def validate_ui_input(
            value: str, _input_type: str, field_name: str = "Input"
        ) -> tuple[bool, str]:
            return True, value

        @staticmethod
        def sanitize_ui_input(value: str) -> str:
            """Sanitize input string by escaping HTML characters."""
            if not isinstance(value, str):
                value = str(value)
            html_escape_table = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#x27;",
            }
            return "".join(html_escape_table.get(c, c) for c in value)

        @staticmethod
        def validate_form_data(
            form_data: dict[str, tuple[str, str]],
        ) -> tuple[bool, dict[str, str]]:
            return True, dict(form_data)

        @staticmethod
        def sanitize_form_data(form_data: dict[str, tuple[str, str]]) -> dict[str, str]:
            sanitized = {}
            for key, (_input_type, value) in form_data.items():
                sanitized[key] = InputValidation.sanitize_ui_input(value)
            return sanitized

    # Expose the functions at module level for easier import
    validate_ui_input = InputValidation.validate_ui_input
    sanitize_ui_input = InputValidation.sanitize_ui_input
    validate_form_data = InputValidation.validate_form_data
    sanitize_form_data = InputValidation.sanitize_form_data


# Import UI widgets with error handling
try:
    from ui.user_management_widget import UserManagementWidget
except ImportError as e:
    logger.error(f"UserManagementWidget import failed: {e}")
    UserManagementWidget = None

try:
    from ui.chat.ai_assistant_widget import AIAssistantWidget
except ImportError as e:
    logger.error(f"AIAssistantWidget import failed: {e}")
    AIAssistantWidget = None
