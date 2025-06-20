#!/usr/bin/env python3
"""
Utility for encrypting/decrypting Atlas security documentation
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_encryption_key():
    """Get encryption key from environment variable"""
    password = os.getenv('ATLAS_CORE_INIT_KEY', 'default_key_placeholder').encode()
    salt = b'atlas_security_docs_salt_2024'
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encrypt_text(text: str) -> str:
    """Encrypt text using the environment key"""
    key = get_encryption_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(text.encode('utf-8'))
    return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

def decrypt_text(encrypted_text: str) -> str:
    """Decrypt text using the environment key"""
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode('utf-8'))
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')
    except Exception:
        return "ACCESS_DENIED: Invalid decryption key"

if __name__ == "__main__":
    # Test the encryption system
    test_text = "This is a test security message"
    encrypted = encrypt_text(test_text)
    print(f"Encrypted: {encrypted}")
    
    decrypted = decrypt_text(encrypted)
    print(f"Decrypted: {decrypted}")
