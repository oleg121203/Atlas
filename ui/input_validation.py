"""
Input validation utilities for the Atlas UI components.

This module provides functions to validate and sanitize user inputs in the UI,
ensuring security and data integrity.
"""

import re
from typing import Optional, Dict, Any

from security.security_utils import validate_input, sanitize_input, get_logger

# Logger for input validation
logger = get_logger("InputValidation")

# Additional UI-specific validation patterns
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

# Input field types
INPUT_TYPES = {
    "email": {
        "max_length": 100,
        "validator": lambda x: validate_input(x, "email")
    },
    "url": {
        "max_length": 200,
        "validator": lambda x: validate_input(x, "url")
    },
    "filepath": {
        "max_length": 255,
        "validator": lambda x: validate_input(x, "filepath")
    },
    "username": {
        "max_length": 20,
        "validator": lambda x: bool(USERNAME_PATTERN.match(x))
    },
    "password": {
        "max_length": 50,
        "validator": lambda x: bool(PASSWORD_PATTERN.match(x))
    },
    "text": {
        "max_length": 1000,
        "validator": lambda x: validate_input(x, "text")
    },
    "alphanumeric": {
        "max_length": 100,
        "validator": lambda x: validate_input(x, "alphanumeric")
    }
}

def validate_ui_input(value: str, input_type: str, field_name: str = "Input") -> tuple[bool, str]:
    """
    Validate UI input based on the specified type.
    
    Args:
        value: Input value to validate
        input_type: Type of input (email, url, filepath, username, password, text, alphanumeric)
        field_name: Name of the input field for error messaging
    
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not value:
        return False, f"{field_name} cannot be empty"
    
    input_config = INPUT_TYPES.get(input_type)
    if not input_config:
        logger.warning("Unknown input type: %s", input_type)
        return False, f"Invalid input type for {field_name}"
    
    max_length = input_config["max_length"]
    if len(value) > max_length:
        return False, f"{field_name} exceeds maximum length of {max_length} characters"
    
    validator = input_config["validator"]
    if not validator(value):
        return False, f"Invalid {field_name} format"
    
    logger.debug("Input validation passed for %s of type %s", field_name, input_type)
    return True, ""

def sanitize_ui_input(value: str) -> str:
    """
    Sanitize UI input to remove potentially dangerous content.
    
    Args:
        value: Input value to sanitize
    
    Returns:
        str: Sanitized input value
    """
    sanitized = sanitize_input(value)
    logger.debug("Input sanitized, original length: %d, sanitized length: %d", len(value), len(sanitized))
    return sanitized

def validate_form_data(form_data: Dict[str, tuple[str, str]]) -> tuple[bool, Dict[str, str]]:
    """
    Validate a form's data based on field types.
    
    Args:
        form_data: Dictionary of field_name: (value, input_type)
    
    Returns:
        tuple[bool, Dict[str, str]]: (is_valid, errors_dict)
    """
    errors = {}
    is_valid = True
    
    for field_name, (value, input_type) in form_data.items():
        valid, error_msg = validate_ui_input(value, input_type, field_name)
        if not valid:
            errors[field_name] = error_msg
            is_valid = False
    
    return is_valid, errors

def sanitize_form_data(form_data: Dict[str, tuple[str, str]]) -> Dict[str, str]:
    """
    Sanitize all inputs in a form's data.
    
    Args:
        form_data: Dictionary of field_name: (value, input_type)
    
    Returns:
        Dict[str, str]: Sanitized form data as field_name: sanitized_value
    """
    sanitized_data = {}
    for field_name, (value, _) in form_data.items():
        sanitized_data[field_name] = sanitize_ui_input(value)
    return sanitized_data
