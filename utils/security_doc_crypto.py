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

def encrypt_file(input_path: str, output_path: str):
    """Encrypts a file and saves the result to another file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    encrypted_content = encrypt_text(content)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(encrypted_content)

def decrypt_file(input_path: str, output_path: str):
    """Decrypts a file and saves the result."""
    with open(input_path, 'r', encoding='utf-8') as f:
        encrypted_content = f.read()
    decrypted_content = decrypt_text(encrypted_content)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decrypted_content)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Encrypt or decrypt text/files for Atlas.")
    parser.add_argument('action', choices=['encrypt', 'decrypt', 'encrypt_file', 'decrypt_file', 'test'])
    parser.add_argument('data', nargs='?', default=None, help="Text to process or input file path")
    parser.add_argument('--output', help="Output file path for file operations")

    args = parser.parse_args()

    if args.action == 'encrypt':
        if not args.data:
            print("Error: Text to encrypt is required.")
        else:
            print(encrypt_text(args.data))
    elif args.action == 'decrypt':
        if not args.data:
            print("Error: Text to decrypt is required.")
        else:
            print(decrypt_text(args.data))
    elif args.action == 'encrypt_file':
        if not args.data or not args.output:
            print("Error: --data (input file) and --output are required for file encryption.")
        else:
            encrypt_file(args.data, args.output)
            print(f"File '{args.data}' encrypted to '{args.output}'")
    elif args.action == 'decrypt_file':
        if not args.data or not args.output:
            print("Error: --data (input file) and --output are required for file decryption.")
        else:
            decrypt_file(args.data, args.output)
            print(f"File '{args.data}' decrypted to '{args.output}'")
    elif args.action == 'test':
        # Test the encryption system
        test_text = "This is a test security message"
        encrypted = encrypt_text(test_text)
        print(f"Encrypted: {encrypted}")
        
        decrypted = decrypt_text(encrypted)
        print(f"Decrypted: {decrypted}")
