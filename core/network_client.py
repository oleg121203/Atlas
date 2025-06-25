"""
Network client for the Atlas application.

This module provides a secure network client for making HTTP requests,
integrating network security utilities to enforce HTTPS and SSL validation.
"""

import requests
from typing import Optional, Dict, Any, Union

from security.network_security import enforce_https_url, validate_ssl_certificate, make_secure_request, configure_secure_session
from core.logging import get_logger

logger = get_logger("NetworkClient")

class NetworkClient:
    """Secure network client for Atlas application."""
    def __init__(self):
        self.session = configure_secure_session()
        logger.info("Network client initialized with secure session")
    
    def validate_url(self, url: str, timeout: int = 10) -> tuple[bool, str]:
        """
        Validate the SSL certificate of a URL before making a request.
        
        Args:
            url: URL to validate
            timeout: Timeout in seconds for validation
        
        Returns:
            tuple[bool, str]: (is_valid, message)
        """
        return validate_ssl_certificate(url, timeout)
    
    def get(self, url: str, timeout: int = 10, validate_ssl: bool = True, **kwargs) -> Optional[requests.Response]:
        """
        Make a secure GET request to the specified URL.
        
        Args:
            url: Target URL
            timeout: Request timeout in seconds
            validate_ssl: Whether to validate SSL certificate before request
            **kwargs: Additional arguments for requests.get()
        
        Returns:
            Optional[requests.Response]: Response if successful, None otherwise
        """
        if validate_ssl:
            is_valid, message = self.validate_url(url, timeout)
            if not is_valid:
                logger.error("SSL validation failed for GET request to %s: %s", url, message)
                return None
        
        return make_secure_request(url, method="GET", timeout=timeout, **kwargs)
    
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, 
             timeout: int = 10, validate_ssl: bool = True, **kwargs) -> Optional[requests.Response]:
        """
        Make a secure POST request to the specified URL.
        
        Args:
            url: Target URL
            data: Form data to send
            json: JSON data to send
            timeout: Request timeout in seconds
            validate_ssl: Whether to validate SSL certificate before request
            **kwargs: Additional arguments for requests.post()
        
        Returns:
            Optional[requests.Response]: Response if successful, None otherwise
        """
        if validate_ssl:
            is_valid, message = self.validate_url(url, timeout)
            if not is_valid:
                logger.error("SSL validation failed for POST request to %s: %s", url, message)
                return None
        
        return make_secure_request(url, method="POST", data=data, json=json, timeout=timeout, **kwargs)
    
    def request(self, method: str, url: str, timeout: int = 10, validate_ssl: bool = True, 
                **kwargs) -> Optional[requests.Response]:
        """
        Make a secure request with the specified method to the URL.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Target URL
            timeout: Request timeout in seconds
            validate_ssl: Whether to validate SSL certificate before request
            **kwargs: Additional arguments for requests.request()
        
        Returns:
            Optional[requests.Response]: Response if successful, None otherwise
        """
        if validate_ssl:
            is_valid, message = self.validate_url(url, timeout)
            if not is_valid:
                logger.error("SSL validation failed for %s request to %s: %s", method, url, message)
                return None
        
        return make_secure_request(url, method=method, timeout=timeout, **kwargs)
    
    def close(self) -> None:
        """Close the session to release resources."""
        self.session.close()
        logger.info("Network client session closed")
