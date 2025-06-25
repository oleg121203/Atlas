# Security Modules Usage Guide for Atlas

This guide provides detailed instructions on how to use the security modules implemented in the Atlas application. These modules are designed to enhance security by providing utilities for credential management, input validation, network security, role-based access control, and data encryption.

## Table of Contents

- [Credential Manager](#credential-manager)
- [Input Validation and Sanitization](#input-validation-and-sanitization)
- [Network Security](#network-security)
- [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
- [Data Encryption](#data-encryption)

## Credential Manager

The `CredentialManager` class in `security.credential_manager` provides a secure way to store and retrieve sensitive credentials like API keys and passwords.

### Initialization

```python
from security.credential_manager import CredentialManager

# Initialize the credential manager
credential_mgr = CredentialManager(master_key_env_var="ATLAS_MASTER_KEY")
```

### Storing Credentials

```python
# Store a credential with a unique identifier
credential_mgr.store_credential(
    credential_id="openai_api_key",
    credential_value="sk-your-api-key",
    description="API key for OpenAI services"
)
```

### Retrieving Credentials

```python
# Retrieve a credential by its ID
api_key = credential_mgr.retrieve_credential("openai_api_key")
if api_key:
    print("Retrieved API key successfully")
else:
    print("Failed to retrieve API key or key not found")
```

### Listing and Removing Credentials

```python
# List all stored credential IDs and descriptions
credentials = credential_mgr.list_credentials()
for cred_id, desc in credentials.items():
    print(f"ID: {cred_id}, Description: {desc}")

# Remove a credential
credential_mgr.remove_credential("openai_api_key")
print("Credential removed")
```

**Security Notes**:
- The master key is loaded from an environment variable for security.
- Credentials are encrypted using the master key before storage.
- Always use secure channels to load or update the master key.

## Input Validation and Sanitization

The `ui.input_validation` module provides utilities to validate and sanitize user inputs, preventing injection attacks and ensuring data integrity.

### Validating Single Inputs

```python
from ui.input_validation import validate_ui_input

# Validate a username
username = "john_doe123"
is_valid, error_msg = validate_ui_input(username, "username", "Username")
if not is_valid:
    print(f"Validation error: {error_msg}")
else:
    print("Username is valid")
```

**Supported Input Types**:
- `email`: Validates email addresses.
- `url`: Validates URLs.
- `filepath`: Validates file paths.
- `username`: Validates usernames (alphanumeric with underscores).
- `password`: Validates password complexity.
- `text`: Validates general text input.
- `alphanumeric`: Validates alphanumeric strings.

### Sanitizing Inputs

```python
from ui.input_validation import sanitize_ui_input

# Sanitize user input to prevent injection
user_input = "<script>alert('hack')</script>"
sanitized_input = sanitize_ui_input(user_input)
print(f"Sanitized input: {sanitized_input}")  # Outputs escaped or cleaned content
```

### Validating Form Data

```python
from ui.input_validation import validate_form_data

# Validate a form with multiple fields
form_data = {
    "email": "john@example.com",
    "username": "john_doe123",
    "password": "SecurePass123!"
}
field_types = {
    "email": "email",
    "username": "username",
    "password": "password"
}
is_valid, errors = validate_form_data(form_data, field_types)
if not is_valid:
    for field, error in errors.items():
        print(f"Error in {field}: {error}")
else:
    print("Form data is valid")
```

**Security Notes**:
- Validation prevents malformed or malicious inputs from being processed.
- Sanitization escapes or removes dangerous content to prevent XSS or injection attacks.
- Always validate and sanitize inputs at the UI level before processing.

## Network Security

The `security.network_security` module provides functions to ensure secure network communications, enforcing HTTPS and validating SSL certificates.

### Enforcing HTTPS

```python
from security.network_security import enforce_https_url

# Ensure a URL uses HTTPS
url = "http://example.com/api"
secure_url = enforce_https_url(url)
print(f"Secure URL: {secure_url}")  # Outputs: https://example.com/api
```

### Making Secure Requests

```python
from security.network_security import make_secure_request

# Make a secure HTTP request with SSL validation
response = make_secure_request("https://api.example.com/data")
if response:
    print("Secure request successful")
    print(response.json())
else:
    print("Secure request failed")
```

### Using NetworkClient (Recommended)

```python
from core.network_client import NetworkClient

# Initialize the network client (done in AtlasApplication)
network_client = NetworkClient()

# Make a secure GET request
response = network_client.get("https://api.example.com/data")
if response:
    print("Data retrieved securely")
    print(response.json())

# Make a secure POST request with data
payload = {"key": "value"}
response = network_client.post("https://api.example.com/submit", json=payload)
if response:
    print("Data posted securely")

# Close the client when done (handled by AtlasApplication shutdown)
network_client.close()
```

**Security Notes**:
- Always use `NetworkClient` for network operations as it integrates all security measures.
- HTTPS enforcement prevents data from being sent over unencrypted connections.
- SSL certificate validation ensures you're communicating with the intended server.

## Role-Based Access Control (RBAC)

The `security.rbac` module implements role-based access control to restrict access to operations based on user roles.

### Initializing RBAC Manager

```python
from security.rbac import get_rbac_manager

# Get the global RBAC manager (initialized in AtlasApplication)
rbac = get_rbac_manager()
```

### Assigning Roles to Users

```python
from security.rbac import Role

# Assign a role to a user
rbac.assign_user_role("johndoe", Role.USER)
print(f"Assigned USER role to johndoe")

# Remove a user's role
rbac.remove_user_role("johndoe")
print(f"Removed role from johndoe")
```

### Checking Permissions

```python
from security.rbac import Permission

# Check if a user has a specific permission
can_create_task = rbac.check_permission("johndoe", Permission.TASK_CREATE)
if can_create_task:
    print("User can create tasks")
else:
    print("User cannot create tasks")

# Get all permissions for a user
permissions = rbac.get_user_permissions("johndoe")
for perm in permissions:
    print(f"Permission: {perm.value}")
```

### Enforcing Permissions

```python
# Enforce a permission check (raises PermissionError if not allowed)
try:
    rbac.enforce_permission("johndoe", Permission.TASK_CREATE, "Create Task Operation")
    print("Permission granted, proceeding with task creation")
    # Proceed with the operation
except PermissionError as e:
    print(f"Permission denied: {e}")
```

**Using in UI Components**:
- The `UserManagementWidget` in `ui.user_management_widget` provides a graphical interface to manage users and roles.
- Permission checks are integrated into `MainWindow` for easy enforcement across UI operations.

**Security Notes**:
- RBAC ensures the principle of least privilege, limiting users to only what they need to do.
- Use `enforce_permission` for critical operations to ensure security compliance.
- Configuration is persisted automatically, ensuring role assignments are retained across sessions.

## Data Encryption

The `security.security_utils` module provides functions for encrypting and decrypting sensitive data at rest.

### Encrypting Data

```python
from security.security_utils import encrypt_data

# Encrypt sensitive data
sensitive_data = "my-secret-information"
encrypted_data = encrypt_data(sensitive_data)
print(f"Encrypted data: {encrypted_data}")
```

### Decrypting Data

```python
from security.security_utils import decrypt_data

# Decrypt encrypted data
try:
    decrypted_data = decrypt_data(encrypted_data)
    print(f"Decrypted data: {decrypted_data}")  # Outputs: my-secret-information
except Exception as e:
    print(f"Decryption failed: {e}")
```

### Key Derivation

```python
from security.security_utils import derive_key

# Derive an encryption key from a passphrase
passphrase = "my-secure-passphrase"
salt = b"optional-fixed-salt"  # Optional, can be None for random salt
key, used_salt = derive_key(passphrase, salt)
print(f"Derived key: {key.hex()}")
print(f"Salt used: {used_salt.hex()}")
```

**Security Notes**:
- Encryption keys are derived from environment variables (`ATLAS_ENCRYPTION_KEY`) for security.
- Use encryption for storing sensitive data in files or databases.
- Ensure keys are managed securely and not exposed in logs or version control.

By following this usage guide, developers and integrators can effectively utilize the security modules in Atlas to protect the application and its users from potential threats. Always refer to the latest documentation and adhere to security best practices outlined in `security_best_practices.md`.
