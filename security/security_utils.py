"""
Security utilities for the Atlas application.

This module provides functions and utilities to enhance the security of the Atlas application,
including credential management, input validation, encryption, and secure communication.
"""

import os
import re
import hashlib
import hmac
import secrets
from typing import Optional, Any, Dict

import base64
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

from core.logging import get_logger
from core.config import get_config

# Logger for security operations
logger = get_logger("Security")

# Regex patterns for input validation
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
URL_PATTERN = re.compile(
    r"^https?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$", re.IGNORECASE)
FILE_PATH_PATTERN = re.compile(r"^[a-zA-Z0-9_/\-\.][a-zA-Z0-9_/\-\. ]*$")

# Salt for key derivation (will be overridden by config if available)
DEFAULT_SALT = b"atlas-default-salt"

class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass


def initialize_security() -> bool:
    """
    Initialize security utilities and check for required dependencies.
    
    Returns:
        bool: True if security system initialized successfully
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        logger.warning("Cryptography library not available. Encryption functionality will be limited.")
        return False
    
    config = get_config()
    security_config = config.get("security", {})
    if not security_config.get("encryption_key"):
        logger.warning("No encryption key configured. Generate one for secure operations.")
        # Generate a new key if not configured (but don't save it)
        if CRYPTOGRAPHY_AVAILABLE:
            key = Fernet.generate_key()
            logger.info("Temporary encryption key generated. Configure a permanent key in settings.")
            # Don't store it, just log that we have a temporary one
            return True
    
    logger.info("Security utilities initialized successfully")
    return True


def get_encryption_key() -> Optional[bytes]:
    """
    Retrieve or derive the encryption key from configuration or environment.
    
    Returns:
        Optional[bytes]: Encryption key if available, None otherwise
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        return None
    
    config = get_config()
    security_config = config.get("security", {})
    key_str = security_config.get("encryption_key")
    if key_str:
        try:
            return base64.urlsafe_b64decode(key_str)
        except Exception as e:
            logger.error("Failed to decode encryption key from config: %s", str(e))
            return None
    
    # Fallback to environment variable
    key_env = os.environ.get("ATLAS_ENCRYPTION_KEY")
    if key_env:
        try:
            return base64.urlsafe_b64decode(key_env)
        except Exception as e:
            logger.error("Failed to decode encryption key from environment: %s", str(e))
            return None
    
    logger.warning("No encryption key available")
    return None


def derive_key(password: str, salt: Optional[bytes] = None) -> bytes:
    """
    Derive a cryptographic key from a password using PBKDF2.
    
    Args:
        password (str): Password to derive key from
        salt (bytes, optional): Salt for key derivation
        
    Returns:
        bytes: Derived key
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        raise SecurityError("Cryptography library not available")
    
    salt = salt or DEFAULT_SALT
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_data(data: str) -> Optional[str]:
    """
    Encrypt sensitive data using Fernet symmetric encryption.
    
    Args:
        data (str): Data to encrypt
        
    Returns:
        Optional[str]: Encrypted data as base64 string, or None if encryption unavailable
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        logger.error("Cannot encrypt data - cryptography library not available")
        return None
    
    key = get_encryption_key()
    if not key:
        logger.error("Cannot encrypt data - no encryption key available")
        return None
    
    try:
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error("Encryption failed: %s", str(e))
        return None


def decrypt_data(encrypted_data: str) -> Optional[str]:
    """
    Decrypt data encrypted with Fernet symmetric encryption.
    
    Args:
        encrypted_data (str): Encrypted data as base64 string
        
    Returns:
        Optional[str]: Decrypted data, or None if decryption fails
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        logger.error("Cannot decrypt data - cryptography library not available")
        return None
    
    key = get_encryption_key()
    if not key:
        logger.error("Cannot decrypt data - no encryption key available")
        return None
    
    try:
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error("Decryption failed: %s", str(e))
        return None


def hash_data(data: str, salt: Optional[str] = None) -> str:
    """
    Create a secure hash of the input data using SHA-256.
    
    Args:
        data (str): Data to hash
        salt (str, optional): Salt for hashing
        
    Returns:
        str: Hexadecimal hash string
    """
    if salt:
        data = data + salt
    return hashlib.sha256(data.encode()).hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        length (int): Length of token in bytes (will be doubled in hex representation)
        
    Returns:
        str: Secure random token as hexadecimal string
    """
    return secrets.token_hex(length)


def validate_input(input_str: str, input_type: str, max_length: int = 1000) -> bool:
    """
    Validate input string based on type and constraints.
    
    Args:
        input_str (str): Input string to validate
        input_type (str): Type of input (email, url, filepath, alphanumeric, etc.)
        max_length (int): Maximum allowed length
        
    Returns:
        bool: True if input is valid
    """
    if not input_str or len(input_str) > max_length:
        logger.warning("Input validation failed: length check failed")
        return False
    
    if input_type == "email":
        return bool(EMAIL_PATTERN.match(input_str))
    elif input_type == "url":
        return bool(URL_PATTERN.match(input_str))
    elif input_type == "filepath":
        return bool(FILE_PATH_PATTERN.match(input_str))
    elif input_type == "alphanumeric":
        return input_str.isalnum()
    elif input_type == "text":
        # Basic text validation - just check for control characters
        return all(ord(char) >= 32 for char in input_str)
    else:
        logger.warning("Unknown input type for validation: %s", input_type)
        return False


def sanitize_input(input_str: str) -> str:
    """
    Sanitize input by removing or escaping potentially dangerous characters.
    
    Args:
        input_str (str): Input string to sanitize
        
    Returns:
        str: Sanitized string
    """
    # Remove control characters
    sanitized = "".join(char for char in input_str if ord(char) >= 32 or char in "\r\n\t")
    # Escape HTML characters if needed (basic escaping)
    sanitized = sanitized.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
    return sanitized


def check_environment_security() -> Dict[str, Any]:
    """
    Check environment for potential security issues.
    
    Returns:
        Dict[str, Any]: Report of security checks
    """
    report = {
        "checks": [],
        "warnings": 0,
        "errors": 0
    }
    
    # Check for encryption key in environment variables (not ideal but common)
    if os.environ.get("ATLAS_ENCRYPTION_KEY"):
        report["checks"].append({
            "name": "Encryption Key in Environment",
            "status": "WARNING",
            "message": "Encryption key found in environment variable. Consider using a secure vault solution."
        })
        report["warnings"] += 1
    
    # Check for other sensitive environment variables
    sensitive_vars = [key for key in os.environ if any(kw in key.lower() for kw in ["password", "secret", "key", "token"])]
    if sensitive_vars:
        report["checks"].append({
            "name": "Sensitive Environment Variables",
            "status": "WARNING",
            "message": f"Found {len(sensitive_vars)} environment variables with sensitive names. Ensure they are secure."
        })
        report["warnings"] += 1
    
    # Check if running in debug mode
    config = get_config()
    if config.get("debug", False):
        report["checks"].append({
            "name": "Debug Mode",
            "status": "WARNING",
            "message": "Application is running in debug mode. Disable in production."
        })
        report["warnings"] += 1
    
    logger.info("Environment security check completed: %d warnings, %d errors", report["warnings"], report["errors"])
    return report


def secure_compare(a: bytes, b: bytes) -> bool:
    """
    Perform a constant-time comparison of two byte strings to prevent timing attacks.
    
    Args:
        a (bytes): First byte string
        b (bytes): Second byte string
        
    Returns:
        bool: True if strings are equal
    """
    return hmac.compare_digest(a, b)
