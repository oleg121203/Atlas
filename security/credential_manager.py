"""
Credential Manager for secure storage and retrieval of sensitive information.

This module provides a secure way to store and retrieve credentials using encryption.
Credentials are stored in a JSON file in the user's home directory, encrypted with a key
derived from a master password or system-specific information.
"""

import os
import json
import base64
from typing import Optional, Dict, Any
from pathlib import Path

from security.security_utils import encrypt_data, decrypt_data, derive_key, get_logger

# Logger for credential operations
logger = get_logger("CredentialManager")

# Credential storage location
CREDENTIAL_DIR = os.path.join(Path.home(), ".atlas", "credentials")
CREDENTIAL_FILE = os.path.join(CREDENTIAL_DIR, "credentials.json")

# Master key environment variable
MASTER_KEY_ENV = "ATLAS_MASTER_KEY"

class CredentialManager:
    """Manages secure storage and retrieval of credentials."""
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize the Credential Manager.
        
        Args:
            master_key: Optional master key for encryption. If not provided, 
                       will use environment variable or default derivation.
        """
        self._credentials: Dict[str, Any] = {}
        self._master_key = master_key or os.environ.get(MASTER_KEY_ENV)
        self._loaded = False
        logger.info("Credential Manager initialized")
    
    def _ensure_directory(self) -> None:
        """Ensure the credential storage directory exists with proper permissions."""
        os.makedirs(CREDENTIAL_DIR, mode=0o700, exist_ok=True)
    
    def _get_encryption_key(self) -> bytes:
        """
        Derive an encryption key for credential storage.
        
        Returns:
            bytes: Derived encryption key
        """
        if self._master_key:
            return derive_key(self._master_key)
        else:
            # Use a system-specific derivation if no master key provided
            system_info = f"{os.getpid()}-{os.uname().nodename}"
            return derive_key(system_info)
    
    def load_credentials(self) -> bool:
        """
        Load credentials from storage.
        
        Returns:
            bool: True if credentials loaded successfully
        """
        if self._loaded:
            return True
        
        try:
            if os.path.exists(CREDENTIAL_FILE):
                with open(CREDENTIAL_FILE, "r") as f:
                    encrypted_data = json.load(f)
                
                decrypted_data = {}
                for key, encrypted_value in encrypted_data.items():
                    decrypted_value = decrypt_data(encrypted_value)
                    if decrypted_value:
                        decrypted_data[key] = decrypted_value
                    else:
                        logger.warning("Failed to decrypt credential: %s", key)
                
                self._credentials = decrypted_data
                self._loaded = True
                logger.info("Credentials loaded from storage")
                return True
            else:
                logger.info("No credential file found, starting with empty credentials")
                self._credentials = {}
                self._loaded = True
                return True
        except Exception as e:
            logger.error("Error loading credentials: %s", str(e))
            self._credentials = {}
            self._loaded = False
            return False
    
    def save_credentials(self) -> bool:
        """
        Save credentials to storage.
        
        Returns:
            bool: True if credentials saved successfully
        """
        try:
            self._ensure_directory()
            encrypted_data = {}
            for key, value in self._credentials.items():
                encrypted_value = encrypt_data(value)
                if encrypted_value:
                    encrypted_data[key] = encrypted_value
                else:
                    logger.warning("Failed to encrypt credential: %s", key)
                    encrypted_data[key] = value  # Fallback to unencrypted (not ideal)
            
            with open(CREDENTIAL_FILE, "w") as f:
                json.dump(encrypted_data, f, indent=2)
            
            # Set proper permissions
            os.chmod(CREDENTIAL_FILE, 0o600)
            logger.info("Credentials saved to storage")
            return True
        except Exception as e:
            logger.error("Error saving credentials: %s", str(e))
            return False
    
    def get_credential(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a credential by key.
        
        Args:
            key: Credential key to retrieve
            default: Default value if credential not found
        
        Returns:
            Optional[str]: Credential value or default if not found
        """
        if not self._loaded:
            self.load_credentials()
        
        return self._credentials.get(key, default)
    
    def set_credential(self, key: str, value: str) -> bool:
        """
        Store a credential.
        
        Args:
            key: Credential key
            value: Credential value
        
        Returns:
            bool: True if credential set successfully
        """
        if not self._loaded:
            self.load_credentials()
        
        self._credentials[key] = value
        logger.info("Credential set for key: %s", key)
        return self.save_credentials()
    
    def delete_credential(self, key: str) -> bool:
        """
        Delete a credential from storage.
        
        Args:
            key: Credential key to delete
        
        Returns:
            bool: True if credential deleted successfully
        """
        if not self._loaded:
            self.load_credentials()
        
        if key in self._credentials:
            del self._credentials[key]
            logger.info("Credential deleted for key: %s", key)
            return self.save_credentials()
        return True
    
    def list_credentials(self) -> list:
        """
        List all credential keys (not values for security).
        
        Returns:
            list: List of credential keys
        """
        if not self._loaded:
            self.load_credentials()
        
        return list(self._credentials.keys())


def get_credential_manager(master_key: Optional[str] = None) -> CredentialManager:
    """
    Get a CredentialManager instance.
    
    Args:
        master_key: Optional master key for encryption
    
    Returns:
        CredentialManager: Credential manager instance
    """
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = CredentialManager(master_key)
    return _credential_manager

# Global credential manager instance
_credential_manager = None
