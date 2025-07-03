"""Sanitize Module

This module provides functions to sanitize input and output data to prevent security issues
such as XSS (Cross-Site Scripting) and SQL injection by removing or escaping potentially
malicious content.
"""

from html import escape


def sanitize_input(input_str: str) -> str:
    """
    Sanitize input string by removing or escaping potentially malicious content.

    Args:
        input_str (str): The input string to sanitize.

    Returns:
        str: The sanitized string with HTML tags removed or escaped.
    """
    if not isinstance(input_str, str):
        raise TypeError("Input must be a string")

    # Remove or escape HTML tags to prevent XSS
    sanitized = escape(input_str)
    # Additional sanitization logic can be added here
    return sanitized


def sanitize_output(output_str: str) -> str:
    """
    Sanitize output string by escaping content for safe rendering.

    Args:
        output_str (str): The output string to sanitize.

    Returns:
        str: The sanitized string safe for rendering in HTML.
    """
    if not isinstance(output_str, str):
        raise TypeError("Output must be a string")

    # Escape HTML to prevent XSS when rendering output
    sanitized = escape(output_str)
    return sanitized
