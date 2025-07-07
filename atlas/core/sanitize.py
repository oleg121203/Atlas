"""Sanitize Module

This module provides functions to sanitize input and output data to prevent security issues
such as XSS (Cross-Site Scripting) and SQL injection by removing or escaping potentially
malicious content.
"""

import re
from html import escape

from bs4 import BeautifulSoup


def sanitize_input(text: str) -> str:
    """
    Sanitize input text by removing dangerous HTML attributes and escaping special characters.

    Args:
        text (str): The input text to sanitize.

    Returns:
        str: The sanitized text with dangerous content removed and HTML special characters escaped.
    """
    if not text:
        return text

    # First, remove any dangerous HTML attributes that could contain JavaScript
    # This includes event handlers (onclick, onmouseover, etc.) and javascript: URLs
    dangerous_attrs = [
        r'on\w+\s*=\s*["\'][^"\']*["\']',  # Event handlers
        r'href\s*=\s*["\']\s*javascript:[^"\']*["\']',  # javascript: URLs in href
        r'src\s*=\s*["\']\s*javascript:[^"\']*["\']',  # javascript: URLs in src
        r'style\s*=\s*["\'][^"\']*(expression\(|javascript:)[^"\']*["\']',  # CSS expressions
    ]

    # Remove dangerous attributes
    for pattern in dangerous_attrs:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Remove any remaining dangerous patterns
    dangerous_patterns = [
        r"javascript\s*:",  # javascript: URLs
        r"data\s*:",  # data: URLs
        r"vbscript\s*:",  # vbscript: URLs
        r"about\s*:",  # about: URLs
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Finally, escape any HTML special characters
    return escape(text)


def sanitize_output(output_str: str) -> str:
    """
    Sanitize output strings for safe rendering.
    This function should be used before rendering output to users.

    Args:
        output_str (str): The output string to sanitize.

    Returns:
        str: The sanitized string.
    """
    if output_str is None:
        return ""
    if not isinstance(output_str, str):
        raise TypeError("Output must be a string")
    sanitized = escape(output_str)
    return sanitized


def sanitize_html(html: str, allowed_tags=None) -> str:
    """
    Sanitize HTML content by removing disallowed tags and dangerous attributes.

    Args:
        html (str): The HTML content to sanitize.
        allowed_tags (list, optional): List of allowed HTML tags. Defaults to a safe set.

    Returns:
        str: The sanitized HTML content.
    """
    if html is None:
        return ""
    if not isinstance(html, str):
        raise TypeError("HTML input must be a string")
    if not html:
        return html
    if allowed_tags is None:
        allowed_tags = ["p", "b", "i", "a", "ul", "li", "br", "strong", "em"]
    result = html
    dangerous_tags = ["script", "iframe", "object", "embed"]
    for tag in dangerous_tags:
        result = re.sub(
            f"(?i)<{tag}[^>]*>.*?</{tag}>", lambda m: escape(m.group(0)), result
        )
        result = re.sub(f"(?i)<{tag}[^>]*>", lambda m: escape(m.group(0)), result)
        result = re.sub(f"(?i)</{tag}>", lambda m: escape(m.group(0)), result)

    def handle_tags(match):
        full_tag = match.group(0)
        tag_name = match.group(1).lower()
        if tag_name.startswith("/"):
            tag_name = tag_name[1:]
        if tag_name in allowed_tags:
            return full_tag
        return ""

    result = re.sub(r"<([^>]+)>", handle_tags, result)
    return result


def strip_all_tags(html: str) -> str:
    """
    Remove all HTML tags from the input string, preserving the text content.

    Args:
        html (str): The HTML content to strip tags from.

    Returns:
        str: The text content with all HTML tags removed.
    """
    if html is None:
        return ""
    if not isinstance(html, str):
        raise TypeError("HTML input must be a string")

    # Use BeautifulSoup for robust HTML parsing and text extraction
    soup = BeautifulSoup(html, "html.parser")
    result = soup.get_text(separator=" ")
    # Normalize multiple spaces to a single space and trim
    result = " ".join(result.split())
    return result


def is_valid_html(html: str) -> bool:
    """
    Basic check for dangerous HTML content.

    Args:
        html (str): The HTML content to validate.

    Returns:
        bool: True if no dangerous content is detected, False otherwise.
    """
    if html is None:
        return True

    # Check for dangerous tags and attributes
    if "<script" in html.lower():
        return False
    if "<iframe" in html.lower():
        return False
    if "javascript:" in html.lower():
        return False
    return all(attr not in html.lower() for attr in ["onload", "onclick", "onerror"])
