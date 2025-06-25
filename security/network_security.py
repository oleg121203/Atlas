"""
Network security utilities for the Atlas application.

This module provides functions to enforce secure network communications,
including HTTPS enforcement and SSL certificate validation.
"""

import ssl
import urllib.request
import requests
from typing import Optional, Dict, Any

from core.logging import get_logger

logger = get_logger("NetworkSecurity")

# Default SSL context for secure connections
default_ssl_context = ssl.create_default_context()

def enforce_https_url(url: str) -> str:
    """
    Enforce HTTPS for a given URL by converting HTTP to HTTPS if necessary.
    
    Args:
        url: The input URL to check and potentially modify
    
    Returns:
        str: The URL with HTTPS enforced if possible
    """
    if url.startswith("http://"):
        logger.warning("Insecure HTTP URL detected: %s, converting to HTTPS", url)
        return url.replace("http://", "https://", 1)
    elif not url.startswith("https://"):
        logger.warning("URL without protocol or non-HTTPS detected: %s, prepending HTTPS", url)
        return "https://" + url
    return url

def validate_ssl_certificate(url: str, timeout: int = 10) -> tuple[bool, str]:
    """
    Validate the SSL certificate of a given URL.
    
    Args:
        url: The URL to validate the SSL certificate for
        timeout: Timeout in seconds for the connection attempt
    
    Returns:
        tuple[bool, str]: (is_valid, error_message or success message)
    """
    try:
        # Ensure URL uses HTTPS
        secure_url = enforce_https_url(url)
        
        # Attempt to connect with default SSL context
        urllib.request.urlopen(secure_url, context=default_ssl_context, timeout=timeout)
        logger.info("SSL certificate validation successful for: %s", secure_url)
        return True, f"SSL certificate is valid for {secure_url}"
    except ssl.SSLCertVerificationError as e:
        logger.error("SSL certificate validation failed for %s: %s", url, str(e))
        return False, f"SSL certificate verification failed: {str(e)}"
    except Exception as e:
        logger.error("Error during SSL validation for %s: %s", url, str(e))
        return False, f"Error during SSL validation: {str(e)}"

def make_secure_request(url: str, method: str = "GET", timeout: int = 10, **kwargs) -> Optional[requests.Response]:
    """
    Make a secure HTTP request with SSL verification and HTTPS enforcement.
    
    Args:
        url: The URL to make the request to
        method: HTTP method to use (GET, POST, etc.)
        timeout: Timeout in seconds for the request
        **kwargs: Additional arguments to pass to requests.request()
    
    Returns:
        Optional[requests.Response]: Response object if successful, None if failed
    """
    try:
        # Enforce HTTPS
        secure_url = enforce_https_url(url)
        
        # Ensure SSL verification is enabled
        kwargs.setdefault("verify", True)
        
        # Make the request
        logger.debug("Making secure %s request to: %s", method, secure_url)
        response = requests.request(method, secure_url, timeout=timeout, **kwargs)
        
        logger.info("Secure request successful to: %s, Status code: %d", secure_url, response.status_code)
        return response
    except requests.exceptions.SSLError as e:
        logger.error("SSL error during request to %s: %s", url, str(e))
        return None
    except requests.exceptions.RequestException as e:
        logger.error("Request error to %s: %s", url, str(e))
        return None

def configure_secure_session() -> requests.Session:
    """
    Configure a requests Session with secure settings.
    
    Returns:
        requests.Session: Configured session with SSL verification enabled
    """
    session = requests.Session()
    session.verify = True
    logger.debug("Configured secure requests session with SSL verification")
    return session
