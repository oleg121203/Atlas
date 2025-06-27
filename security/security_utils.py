"""
Security utilities for the Atlas application.

This module provides functions and utilities to enhance the security of the Atlas application,
including credential management, input validation, encryption, and secure communication.
"""

import base64
import hashlib
import hmac
import os
import re
import secrets
from typing import Optional, Union

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

from core.logging import get_logger

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
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)
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
        logger.warning(
            "Cryptography library not available. Encryption functionality will be limited."
        )
        return False

    config = get_config_data()
    security_config = config.get("security", {})
    if not security_config.get("encryption_key"):
        logger.warning(
            "No encryption key configured. Generate one for secure operations."
        )
        # Generate a new key if not configured (but don't save it)
        if CRYPTOGRAPHY_AVAILABLE:
            Fernet.generate_key()
            logger.info(
                "Temporary encryption key generated. Configure a permanent key in settings."
            )
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

    config = get_config_data()
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


def encrypt_data(data: str, key=None) -> Optional[str]:
    """
    Encrypt sensitive data using Fernet symmetric encryption.

    Args:
        data (str): Data to encrypt
        key (bytes): Encryption key

    Returns:
        Optional[str]: Encrypted data as base64 string, or None if encryption unavailable
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        logger.error("Cannot encrypt data - cryptography library not available")
        return None

    if key is None:
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


def decrypt_data(encrypted_data: str, key=None) -> Optional[str]:
    """
    Decrypt data encrypted with Fernet symmetric encryption.

    Args:
        encrypted_data (str): Encrypted data as base64 string
        key (bytes): Encryption key

    Returns:
        Optional[str]: Decrypted data, or None if decryption fails
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        logger.error("Cannot decrypt data - cryptography library not available")
        return None

    if key is None:
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
    sanitized = "".join(
        char for char in input_str if ord(char) >= 32 or char in "\r\n\t"
    )
    # Escape HTML characters if needed (basic escaping)
    sanitized = (
        sanitized.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
    )
    return sanitized


def check_environment_security() -> bool:
    """
    Check if the environment meets basic security requirements.

    Returns:
        bool: True if environment passes security checks, False otherwise
    """
    # Check if running in debug mode
    if os.getenv("DEBUG", "false").lower() == "true":
        print(
            "WARNING: Application is running in DEBUG mode - not suitable for production"
        )
        return False

    # Check for presence of required security variables
    required_vars = ["ATLAS_API_KEY", "ATLAS_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(
            f"WARNING: Missing required security environment variables: {', '.join(missing_vars)}"
        )
        return False

    # Additional security checks can be added here
    return True


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


def constant_time_compare(a: Union[str, bytes], b: Union[str, bytes]) -> bool:
    """Perform a constant-time comparison of two strings or bytes.

    Args:
        a (Union[str, bytes]): First value to compare
        b (Union[str, bytes]): Second value to compare

    Returns:
        bool: True if the values are equal, False otherwise
    """
    # Convert strings to bytes if necessary
    if isinstance(a, str):
        a = a.encode("utf-8")
    if isinstance(b, str):
        b = b.encode("utf-8")

    return hmac.compare_digest(a, b)


def generate_secure_random_string(length: int = 32) -> str:
    """Generate a cryptographically secure random string.

    Args:
        length (int): Length of the random string (default: 32)

    Returns:
        str: Secure random string
    """
    return os.urandom(length).hex()


def secure_hash(data: Union[str, bytes], salt: Optional[bytes] = None) -> bytes:
    """Hash data using SHA-256 with an optional salt.

    Args:
        data (Union[str, bytes]): Data to hash
        salt (Optional[bytes]): Optional salt for additional security

    Returns:
        bytes: Hashed data
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    if salt is None:
        salt = os.urandom(16)

    hasher = hashlib.sha256()
    hasher.update(salt + data)
    return hasher.digest()


def hash_sensitive_data(data: Union[str, bytes], salt: Optional[bytes] = None) -> bytes:
    """Hash sensitive data using SHA-256 with an optional salt.

    Args:
        data (Union[str, bytes]): Data to hash
        salt (Optional[bytes]): Optional salt for additional security

    Returns:
        bytes: Hashed data
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    if salt is None:
        salt = os.urandom(16)

    hasher = hashlib.sha256()
    hasher.update(salt + data)
    return hasher.digest()


def check_environment_security_new() -> bool:
    """Check if the environment meets basic security requirements.

    Returns:
        bool: True if environment passes security checks, False otherwise
    """
    # Check if running in debug mode
    if os.getenv("DEBUG", "false").lower() == "true":
        print(
            "WARNING: Application is running in DEBUG mode - not suitable for production"
        )
        return False

    # Check for presence of required security variables
    required_vars = ["ATLAS_API_KEY", "ATLAS_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(
            f"WARNING: Missing required security environment variables: {', '.join(missing_vars)}"
        )
        return False

    # Additional security checks can be added here
    return True


# Removed circular import
# from core.config import get_config

# Use a placeholder or alternative method if config is needed
CONFIG = None


def get_config_data():
    global CONFIG
    if CONFIG is None:
        # Placeholder for actual config loading
        CONFIG = {"encryption_key": "placeholder_key"}
    return CONFIG


def secure_hash_new(data: Union[str, bytes], salt: Optional[bytes] = None) -> bytes:
    """Hash data using SHA-256 with an optional salt.

    Args:
        data (Union[str, bytes]): Data to hash
        salt (Optional[bytes]): Optional salt for additional security

    Returns:
        bytes: Hashed data
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    if salt is None:
        salt = os.urandom(16)

    hasher = hashlib.sha256()
    hasher.update(salt + data)
    return hasher.digest()


def generate_secure_token_new(length: int = 32) -> str:
    """Generate a cryptographically secure random token.

    Args:
        length (int): Length of the token in bytes (default: 32)

    Returns:
        str: Hex-encoded secure token
    """
    return secrets.token_hex(length)


def encrypt_data_new(data: Union[str, bytes], key: bytes) -> bytes:
    """Encrypt data using a provided key (placeholder for real encryption).

    Args:
        data (Union[str, bytes]): Data to encrypt
        key (bytes): Encryption key

    Returns:
        bytes: Encrypted data
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    # Placeholder for actual encryption logic
    print("Encrypting data (placeholder implementation)")
    return data  # In a real implementation, this would be proper encryption


def decrypt_data_new(encrypted_data: bytes, key: bytes) -> bytes:
    """Decrypt data using a provided key (placeholder for real decryption).

    Args:
        encrypted_data (bytes): Data to decrypt
        key (bytes): Decryption key

    Returns:
        bytes: Decrypted data
    """
    # Placeholder for actual decryption logic
    print("Decrypting data (placeholder implementation)")
    return encrypted_data  # In a real implementation, this would be proper decryption


def check_password_strength(password: str) -> bool:
    """Check if a password meets minimum strength requirements.

    Args:
        password (str): Password to check

    Returns:
        bool: True if password meets strength requirements, False otherwise
    """
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    return any(c.isdigit() for c in password)


def sanitize_input_new(input_str: str) -> str:
    """Sanitize user input to prevent injection attacks.

    Args:
        input_str (str): Input string to sanitize

    Returns:
        str: Sanitized input string
    """
    # Basic sanitization - in a real implementation, this would be more comprehensive
    return (
        input_str.replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def constant_time_compare_new(a: Union[str, bytes], b: Union[str, bytes]) -> bool:
    """Perform a constant-time comparison of two strings or bytes.

    Args:
        a (Union[str, bytes]): First value to compare
        b (Union[str, bytes]): Second value to compare

    Returns:
        bool: True if the values are equal, False otherwise
    """
    # Convert strings to bytes if necessary
    if isinstance(a, str):
        a = a.encode("utf-8")
    if isinstance(b, str):
        b = b.encode("utf-8")

    return hmac.compare_digest(a, b)

    # Прибрано дублікат функції check_environment_security_new
    if os.getenv("DEBUG", "false").lower() == "true":
        print(
            "WARNING: Application is running in DEBUG mode - not suitable for production"
        )
        return False

    # Check for presence of required security variables
    required_vars = ["ATLAS_API_KEY", "ATLAS_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(
            f"WARNING: Missing required security environment variables: {', '.join(missing_vars)}"
        )
        return False

    # Additional security checks can be added here
    return True
