"""
Workflow Security Module

This module implements security features for workflow automation,
including access control, encryption, and audit logging.
"""

import hashlib
import hmac
import json
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AccessControl:
    """Manages role-based access control for workflow operations."""

    def __init__(self, roles_config: Optional[Dict[str, Dict[str, Any]]] = None):
        """Initialize access control with role permissions.

        Args:
            roles_config (Optional[Dict[str, Dict[str, Any]]]): Configuration of roles and their permissions.
        """
        self.roles = roles_config or {
            "admin": {
                "can_start": True,
                "can_stop": True,
                "can_edit": True,
                "can_view": True,
            },
            "editor": {
                "can_start": True,
                "can_stop": False,
                "can_edit": True,
                "can_view": True,
            },
            "viewer": {
                "can_start": False,
                "can_stop": False,
                "can_edit": False,
                "can_view": True,
            },
        }
        self.user_roles: Dict[str, str] = {}
        logger.info("Access control initialized with default roles")

    def assign_role(self, user_id: str, role: str) -> None:
        """Assign a role to a user.

        Args:
            user_id (str): Unique identifier for the user.
            role (str): Role to assign (e.g., 'admin', 'editor', 'viewer').
        """
        if role not in self.roles:
            raise ValueError(f"Unknown role: {role}")
        self.user_roles[user_id] = role
        logger.info(f"Assigned role {role} to user {user_id}")

    def check_permission(self, user_id: str, action: str) -> bool:
        """Check if a user has permission to perform an action.

        Args:
            user_id (str): Unique identifier for the user.
            action (str): Action to check permission for (e.g., 'can_start', 'can_edit').

        Returns:
            bool: True if user has permission, False otherwise.
        """
        if user_id not in self.user_roles:
            logger.warning(f"User {user_id} not found in access control list")
            return False

        role = self.user_roles[user_id]
        permission = self.roles[role].get(action, False)
        logger.info(
            f"Checked permission for user {user_id} (role: {role}) on action {action}: {permission}"
        )
        return permission

    def add_role(self, role_name: str, permissions: Dict[str, bool]) -> None:
        """Add a new role with specified permissions.

        Args:
            role_name (str): Name of the new role.
            permissions (Dict[str, bool]): Permissions for the new role.
        """
        if role_name in self.roles:
            raise ValueError(f"Role {role_name} already exists")
        self.roles[role_name] = permissions
        logger.info(f"Added new role {role_name} with permissions {permissions}")

    def update_role_permissions(
        self, role_name: str, permissions: Dict[str, bool]
    ) -> None:
        """Update permissions for an existing role.

        Args:
            role_name (str): Name of the role to update.
            permissions (Dict[str, bool]): New permissions for the role.
        """
        if role_name not in self.roles:
            raise ValueError(f"Role {role_name} does not exist")
        self.roles[role_name] = permissions
        logger.info(f"Updated permissions for role {role_name} to {permissions}")


class EncryptionManager:
    """Manages encryption and decryption of sensitive workflow data."""

    def __init__(self, key: Optional[bytes] = None):
        """Initialize encryption manager with a key.

        Args:
            key (Optional[bytes]): Encryption key, if None, a new key is generated.
        """
        self.key = key or secrets.token_bytes(32)  # 256-bit key for AES
        logger.info("Encryption manager initialized")

    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data using AES.

        Args:
            data (str): Data to encrypt.

        Returns:
            bytes: Encrypted data with nonce.
        """
        try:
            import base64

            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

            # Derive a Fernet key from the provided key
            salt = b"static_salt"  # In production, use a random salt per encryption
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.key))
            f = Fernet(key)

            encrypted = f.encrypt(data.encode())
            logger.info("Data encrypted successfully")
            return encrypted
        except ImportError:
            logger.warning(
                "Cryptography library not available, using placeholder encryption"
            )
            return f"encrypted_{data}".encode()

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data encrypted with AES.

        Args:
            encrypted_data (bytes): Encrypted data to decrypt.

        Returns:
            str: Decrypted data.
        """
        try:
            import base64

            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

            # Derive a Fernet key from the provided key
            salt = b"static_salt"  # Must match the salt used in encrypt_data
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.key))
            f = Fernet(key)

            decrypted = f.decrypt(encrypted_data).decode()
            logger.info("Data decrypted successfully")
            return decrypted
        except ImportError:
            logger.warning(
                "Cryptography library not available, using placeholder decryption"
            )
            return encrypted_data.decode().replace("encrypted_", "")

    def hash_sensitive_data(self, data: str) -> str:
        """Create a secure hash of sensitive data.

        Args:
            data (str): Sensitive data to hash.

        Returns:
            str: Hexadecimal representation of the hash.
        """
        return hashlib.sha256(data.encode()).hexdigest()

    def generate_hmac(self, data: str) -> str:
        """Generate an HMAC for data integrity verification.

        Args:
            data (str): Data to generate HMAC for.

        Returns:
            str: Hexadecimal representation of the HMAC.
        """
        return hmac.new(self.key, data.encode(), hashlib.sha256).hexdigest()

    def verify_hmac(self, data: str, hmac_signature: str) -> bool:
        """Verify the HMAC of data for integrity.

        Args:
            data (str): Data to verify.
            hmac_signature (str): HMAC signature to check against.

        Returns:
            bool: True if HMAC is valid, False otherwise.
        """
        computed_hmac = hmac.new(self.key, data.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed_hmac, hmac_signature)


class AuditLogger:
    """Handles logging of security-relevant events for auditing purposes."""

    def __init__(self, log_file: str = "audit_log.json"):
        """Initialize audit logger with a log file path.

        Args:
            log_file (str): Path to the audit log file.
        """
        self.log_file = log_file
        self.logs: List[Dict[str, Any]] = []
        self.load_logs()
        logger.info(f"Audit logger initialized with log file {log_file}")

    def load_logs(self) -> None:
        """Load existing audit logs from file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    self.logs = json.load(f)
                logger.info(f"Loaded existing audit logs from {self.log_file}")
            except Exception as e:
                logger.error(
                    f"Failed to load audit logs from {self.log_file}: {str(e)}"
                )
                self.logs = []

    def save_logs(self) -> None:
        """Save audit logs to file."""
        try:
            with open(self.log_file, "w") as f:
                json.dump(self.logs, f, indent=2)
            logger.info(f"Saved audit logs to {self.log_file}")
        except Exception as e:
            logger.error(f"Failed to save audit logs to {self.log_file}: {str(e)}")

    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any]) -> None:
        """Log a security-relevant event.

        Args:
            event_type (str): Type of event (e.g., 'workflow_start', 'access_denied').
            user_id (str): ID of the user associated with the event.
            details (Dict[str, Any]): Additional details about the event.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details,
        }
        self.logs.append(event)
        logger.info(f"Logged event {event_type} for user {user_id}")
        self.save_logs()

    def get_logs(
        self, event_type: Optional[str] = None, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs filtered by event type or user ID.

        Args:
            event_type (Optional[str]): Filter by event type.
            user_id (Optional[str]): Filter by user ID.

        Returns:
            List[Dict[str, Any]]: Filtered list of log entries.
        """
        filtered_logs = self.logs
        if event_type:
            filtered_logs = [
                log for log in filtered_logs if log["event_type"] == event_type
            ]
        if user_id:
            filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]
        logger.info(
            f"Retrieved {len(filtered_logs)} logs with filters event_type={event_type}, user_id={user_id}"
        )
        return filtered_logs

    def clear_old_logs(self, days_old: int) -> None:
        """Clear logs older than a specified number of days.

        Args:
            days_old (int): Age threshold for logs to be cleared (in days).
        """
        threshold = datetime.now() - timedelta(days=days_old)
        initial_count = len(self.logs)
        self.logs = [
            log
            for log in self.logs
            if datetime.fromisoformat(log["timestamp"]) >= threshold
        ]
        logger.info(
            f"Cleared {initial_count - len(self.logs)} old logs older than {days_old} days"
        )
        self.save_logs()


class WorkflowSecurity:
    """Integrates security features for workflow operations."""

    def __init__(
        self,
        access_control: Optional[AccessControl] = None,
        encryption: Optional[EncryptionManager] = None,
        audit_logger: Optional[AuditLogger] = None,
    ):
        """Initialize workflow security with components.

        Args:
            access_control (Optional[AccessControl]): Access control instance.
            encryption (Optional[EncryptionManager]): Encryption manager instance.
            audit_logger (Optional[AuditLogger]): Audit logger instance.
        """
        self.access_control = access_control or AccessControl()
        self.encryption = encryption or EncryptionManager()
        self.audit_logger = audit_logger or AuditLogger()
        logger.info("Workflow security initialized")

    def secure_workflow_action(
        self,
        user_id: str,
        action: str,
        action_func: callable,
        sensitive_data: Optional[str] = None,
    ) -> Any:
        """Execute a workflow action with security checks and logging.

        Args:
            user_id (str): ID of the user performing the action.
            action (str): Action being performed (for access control).
            action_func (callable): The workflow action function to execute.
            sensitive_data (Optional[str]): Sensitive data to encrypt, if any.

        Returns:
            Any: Result of the action function.
        """
        if not self.access_control.check_permission(user_id, action):
            self.audit_logger.log_event(
                f"access_denied_{action}",
                user_id,
                {"reason": "Insufficient permissions"},
            )
            raise PermissionError(
                f"User {user_id} does not have permission to perform {action}"
            )

        self.audit_logger.log_event(
            f"action_{action}_start", user_id, {"details": f"Starting {action}"}
        )

        if sensitive_data:
            self.encryption.encrypt_data(sensitive_data)
            self.audit_logger.log_event(
                "data_encrypted", user_id, {"data_length": len(sensitive_data)}
            )
        else:
            pass

        try:
            result = action_func()
            self.audit_logger.log_event(
                f"action_{action}_success", user_id, {"result": str(result)[:100]}
            )
            return result
        except Exception as e:
            self.audit_logger.log_event(
                f"action_{action}_failed", user_id, {"error": str(e)}
            )
            raise
