"""Integration Module for Atlas Enterprise Features.

This module handles the integration of various enterprise features for a cohesive
multi-user workspace experience (ENT-002).
"""

from flask import Flask

from enterprise.activity_tracking import ActivityTracking
from enterprise.rbac import RBAC
from enterprise.user_management.user_management_system import (
    UserManagementSystem as UserManagement,
)
from enterprise.workspace_sharing import WorkspaceSharing


class EnterpriseIntegration:
    def __init__(self, app: Flask):
        self.app = app
        self.user_management = UserManagement(app)
        self.rbac = RBAC(app)
        self.workspace_sharing = WorkspaceSharing(app)
        self.activity_tracking = ActivityTracking(app)
        self.setup_routes()

    def setup_routes(self):
        """Setup integrated routes if needed for enterprise features."""
        # Integration endpoints can be added here if cross-module functionality is required
        pass

    def log_user_activity(
        self, user_id: str, action: str, resource_id: str, details: dict = None
    ):
        """Log activity through the activity tracking module."""
        self.activity_tracking.log_activity(user_id, action, resource_id, details)

    def check_user_access(
        self, user_id: str, workspace_id: str, resource_id: str, action: str
    ) -> bool:
        """Check if a user has access to a resource through workspace sharing and RBAC."""
        workspace_access = self.workspace_sharing.check_access(
            workspace_id, user_id, resource_id, action
        )
        if not workspace_access:
            return False
        user_role = self.user_management.get_user_role(user_id)
        return self.rbac.check_permission(user_role, action)

    def add_user_to_workspace(
        self, workspace_id: str, user_id: str, role: str = "member"
    ) -> bool:
        """Add a user to a workspace with a specific role."""
        return self.workspace_sharing.add_member(workspace_id, user_id, role)

    def update_user_workspace_role(
        self, workspace_id: str, user_id: str, new_role: str
    ) -> bool:
        """Update the role of a user in a workspace."""
        return self.workspace_sharing.update_member_role(
            workspace_id, user_id, new_role
        )
