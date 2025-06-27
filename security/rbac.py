"""
Role-Based Access Control (RBAC) for the Atlas application.

This module provides a framework for implementing role-based access control,
allowing fine-grained permissions for different user roles and operations.
"""

import json
import os
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Set

from core.logging import get_logger

logger = get_logger("RBAC")


class Role(Enum):
    """Enum for predefined user roles."""

    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class Permission(Enum):
    """Enum for permissions/operations in the system."""

    # System-wide permissions
    SYSTEM_CONFIG_READ = "system:config:read"
    SYSTEM_CONFIG_WRITE = "system:config:write"
    SYSTEM_SHUTDOWN = "system:shutdown"

    # User management permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Plugin management permissions
    PLUGIN_INSTALL = "plugin:install"
    PLUGIN_UNINSTALL = "plugin:uninstall"
    PLUGIN_ENABLE = "plugin:enable"
    PLUGIN_DISABLE = "plugin:disable"
    PLUGIN_CONFIG_READ = "plugin:config:read"
    PLUGIN_CONFIG_WRITE = "plugin:config:write"

    # Module data permissions
    MODULE_DATA_READ = "module:data:read"
    MODULE_DATA_WRITE = "module:data:write"

    # Agent permissions
    AGENT_CREATE = "agent:create"
    AGENT_CONTROL = "agent:control"
    AGENT_DELETE = "agent:delete"

    # Task permissions
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"

    # Chat permissions
    CHAT_SEND = "chat:send"
    CHAT_READ = "chat:read"
    CHAT_DELETE = "chat:delete"


# Default role permissions mapping
DEFAULT_ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Full system access
        Permission.SYSTEM_CONFIG_READ,
        Permission.SYSTEM_CONFIG_WRITE,
        Permission.SYSTEM_SHUTDOWN,
        # Full user management
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        # Full plugin management
        Permission.PLUGIN_INSTALL,
        Permission.PLUGIN_UNINSTALL,
        Permission.PLUGIN_ENABLE,
        Permission.PLUGIN_DISABLE,
        Permission.PLUGIN_CONFIG_READ,
        Permission.PLUGIN_CONFIG_WRITE,
        # Full module data access
        Permission.MODULE_DATA_READ,
        Permission.MODULE_DATA_WRITE,
        # Full agent control
        Permission.AGENT_CREATE,
        Permission.AGENT_CONTROL,
        Permission.AGENT_DELETE,
        # Full task management
        Permission.TASK_CREATE,
        Permission.TASK_READ,
        Permission.TASK_UPDATE,
        Permission.TASK_DELETE,
        # Full chat access
        Permission.CHAT_SEND,
        Permission.CHAT_READ,
        Permission.CHAT_DELETE,
    },
    Role.MANAGER: {
        # Limited system access
        Permission.SYSTEM_CONFIG_READ,
        # Limited user management
        Permission.USER_READ,
        Permission.USER_UPDATE,
        # Limited plugin management
        Permission.PLUGIN_ENABLE,
        Permission.PLUGIN_DISABLE,
        Permission.PLUGIN_CONFIG_READ,
        Permission.PLUGIN_CONFIG_WRITE,
        # Full module data access
        Permission.MODULE_DATA_READ,
        Permission.MODULE_DATA_WRITE,
        # Limited agent control
        Permission.AGENT_CONTROL,
        # Full task management
        Permission.TASK_CREATE,
        Permission.TASK_READ,
        Permission.TASK_UPDATE,
        Permission.TASK_DELETE,
        # Full chat access
        Permission.CHAT_SEND,
        Permission.CHAT_READ,
        Permission.CHAT_DELETE,
    },
    Role.USER: {
        # No system access
        # Limited user access
        Permission.USER_READ,
        # Limited plugin access
        Permission.PLUGIN_CONFIG_READ,
        # Limited data access
        Permission.MODULE_DATA_READ,
        # Limited agent access
        Permission.AGENT_CONTROL,
        # Limited task access
        Permission.TASK_CREATE,
        Permission.TASK_READ,
        Permission.TASK_UPDATE,
        # Limited chat access
        Permission.CHAT_SEND,
        Permission.CHAT_READ,
    },
    Role.GUEST: {
        # No system access
        # No user management
        # No plugin management
        # Read-only data access
        Permission.MODULE_DATA_READ,
        # No agent access
        # Read-only task access
        Permission.TASK_READ,
        # Read-only chat access
        Permission.CHAT_READ,
    },
}


class RBACManager:
    """Manages Role-Based Access Control for the Atlas application."""

    def __init__(self, config_path: Optional[str] = None):
        self.role_permissions: Dict[Role, Set[Permission]] = (
            DEFAULT_ROLE_PERMISSIONS.copy()
        )
        self.user_roles: Dict[str, Role] = {}
        self.config_path = config_path or self._get_default_config_path()
        self.load_config()
        logger.info("RBAC Manager initialized")

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        home_dir = str(Path.home())
        return os.path.join(home_dir, ".atlas", "rbac_config.json")

    def load_config(self) -> None:
        """Load RBAC configuration from file."""
        if not os.path.exists(self.config_path):
            logger.info(
                "No RBAC config file found at %s, using default permissions",
                self.config_path,
            )
            return

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)

            # Load custom role permissions if available
            custom_permissions = config.get("role_permissions", {})
            for role_str, perms in custom_permissions.items():
                try:
                    role = Role(role_str)
                    self.role_permissions[role] = {
                        Permission(p)
                        for p in perms
                        if p in Permission.__members__.values()
                    }
                    logger.info("Loaded custom permissions for role: %s", role_str)
                except ValueError:
                    logger.warning("Invalid role in config: %s", role_str)

            # Load user roles
            user_roles = config.get("user_roles", {})
            for username, role_str in user_roles.items():
                try:
                    self.user_roles[username] = Role(role_str)
                    logger.info("Loaded role for user %s: %s", username, role_str)
                except ValueError:
                    logger.warning("Invalid role for user %s: %s", username, role_str)

            logger.info("RBAC configuration loaded from %s", self.config_path)
        except Exception as e:
            logger.error("Failed to load RBAC config: %s", str(e))

    def save_config(self) -> None:
        """Save RBAC configuration to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            # Prepare configuration
            config = {
                "role_permissions": {
                    role.value: [perm.value for perm in perms]
                    for role, perms in self.role_permissions.items()
                },
                "user_roles": {
                    username: role.value for username, role in self.user_roles.items()
                },
            }

            # Write to file with secure permissions
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)

            # Set secure file permissions (read/write for owner only)
            os.chmod(self.config_path, 0o600)
            logger.info("RBAC configuration saved to %s", self.config_path)
        except Exception as e:
            logger.error("Failed to save RBAC config: %s", str(e))

    def assign_user_role(self, username: str, role: Role) -> None:
        """
        Assign a role to a user.

        Args:
            username: Username to assign the role to
            role: Role to assign
        """
        self.user_roles[username] = role
        logger.info("Assigned role %s to user %s", role.value, username)
        self.save_config()

    def remove_user_role(self, username: str) -> None:
        """
        Remove a user's role assignment, effectively revoking all permissions.

        Args:
            username: Username to remove role from
        """
        if username in self.user_roles:
            del self.user_roles[username]
            logger.info("Removed role assignment for user %s", username)
            self.save_config()
        else:
            logger.warning("No role assignment found for user %s", username)

    def get_user_role(self, username: str) -> Optional[Role]:
        """
        Get the role assigned to a user.

        Args:
            username: Username to check

        Returns:
            Optional[Role]: The user's role if assigned, None otherwise
        """
        return self.user_roles.get(username)

    def check_permission(self, username: str, permission: Permission) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            username: Username to check
            permission: Permission to verify

        Returns:
            bool: True if user has the permission, False otherwise
        """
        role = self.get_user_role(username)
        if role is None:
            logger.warning(
                "No role assigned to user %s, denying permission %s",
                username,
                permission.value,
            )
            return False

        has_permission = permission in self.role_permissions[role]
        if not has_permission:
            logger.warning(
                "Permission %s denied for user %s with role %s",
                permission.value,
                username,
                role.value,
            )
        return has_permission

    def get_user_permissions(self, username: str) -> Set[Permission]:
        """
        Get all permissions for a user based on their role.

        Args:
            username: Username to check

        Returns:
            Set[Permission]: Set of permissions the user has
        """
        role = self.get_user_role(username)
        if role is None:
            logger.warning(
                "No role assigned to user %s, no permissions available", username
            )
            return set()
        return self.role_permissions[role]

    def add_role_permission(self, role: Role, permission: Permission) -> None:
        """
        Add a permission to a role.

        Args:
            role: Role to modify
            permission: Permission to add
        """
        self.role_permissions[role].add(permission)
        logger.info("Added permission %s to role %s", permission.value, role.value)
        self.save_config()

    def remove_role_permission(self, role: Role, permission: Permission) -> None:
        """
        Remove a permission from a role.

        Args:
            role: Role to modify
            permission: Permission to remove
        """
        if permission in self.role_permissions[role]:
            self.role_permissions[role].remove(permission)
            logger.info(
                "Removed permission %s from role %s", permission.value, role.value
            )
            self.save_config()
        else:
            logger.warning(
                "Permission %s not found for role %s", permission.value, role.value
            )

    def enforce_permission(
        self,
        username: str,
        permission: Permission,
        operation_description: str = "Operation",
    ) -> None:
        """
        Enforce a permission check for a user, raising an exception if not allowed.

        Args:
            username: Username to check
            permission: Required permission
            operation_description: Description of the operation for error message

        Raises:
            PermissionError: If the user does not have the required permission
        """
        if not self.check_permission(username, permission):
            role = self.get_user_role(username)
            error_msg = (
                f"{operation_description} not allowed for user {username} "
                f"with role {role.value if role else 'None'}. "
                f"Required permission: {permission.value}"
            )
            logger.error(error_msg)
            raise PermissionError(error_msg)
        logger.debug(
            "Permission %s granted for user %s for %s",
            permission.value,
            username,
            operation_description,
        )


# Global RBAC manager instance
def get_rbac_manager(config_path: Optional[str] = None) -> RBACManager:
    """
    Get the global RBAC manager instance (singleton).

    Args:
        config_path: Optional path to RBAC configuration file

    Returns:
        RBACManager: The global RBAC manager instance
    """
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager(config_path)
    return _rbac_manager


_rbac_manager: Optional[RBACManager] = None
