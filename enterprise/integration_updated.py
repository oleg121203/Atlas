"""Integration Module for Atlas Enterprise Features.

This module integrates various enterprise features such as user management,
RBAC, workspace sharing, activity tracking, real-time collaboration,
and conflict resolution for a cohesive multi-user workspace implementation.
"""

from typing import Optional, Dict, List
import os
from flask import Flask, request, jsonify, make_response
import jwt

# Import enterprise modules
try:
    from enterprise.user_management import UserManagementSystem as UserManagement
    from enterprise.rbac import RBAC
    from enterprise.workspace_sharing import WorkspaceSharing
    from enterprise.activity_tracking import ActivityTracking
    from enterprise.real_time_collaboration import RealTimeCollaboration
    from enterprise.conflict_resolution import ConflictResolution
except ImportError as e:
    print(f"Import error: {e}")
    raise

class EnterpriseIntegration:
    def __init__(self, app: Flask):
        self.app = app
        self.user_management = UserManagement(app)
        self.rbac = RBAC(app)
        self.workspace_sharing = WorkspaceSharing(app)
        self.activity_tracking = ActivityTracking(app)
        self.real_time_collaboration = RealTimeCollaboration(app)
        self.conflict_resolution = ConflictResolution(app)
        self.secret_key = os.environ.get('JWT_SECRET_KEY', 'mysecretkey')
        self.setup_routes()

    def log_user_activity(self, user_id: str, action: str, resource_type: str, resource_id: str, details: Optional[Dict] = None) -> None:
        """Log user activity across enterprise features."""
        self.activity_tracking.log_activity(user_id, action, resource_type, resource_id, details)

    def check_user_access(self, user_id: str, workspace_id: str, permission: str, resource_type: str, resource_id: str) -> bool:
        """Check if a user has access to a resource based on workspace role and RBAC policies."""
        # Check workspace membership and role
        if not self.workspace_sharing.is_member(workspace_id, user_id):
            return False
        user_role = self.workspace_sharing.get_member_role(workspace_id, user_id)
        if not user_role:
            return False

        # Check RBAC policies for the role
        if not self.rbac.check_permission(user_role, permission):
            return False

        # Check specific resource permissions if applicable
        return self.workspace_sharing.check_resource_access(workspace_id, user_id, resource_type, resource_id)

    def manage_user_role_in_workspace(self, workspace_id: str, user_id: str, role: str, action: str, admin_user: str) -> bool:
        """Manage user roles within a workspace (add, update, remove)."""
        if not self.user_management.user_exists(admin_user):
            return False
        admin_role = self.user_management.get_user_role(admin_user)
        if not admin_role or not self.rbac.check_permission(admin_role, 'manage_users'):
            return False

        if action == 'add':
            if not self.user_management.user_exists(user_id):
                return False
            return self.workspace_sharing.add_member(workspace_id, user_id, role)
        elif action == 'update':
            if not self.workspace_sharing.is_member(workspace_id, user_id):
                return False
            return self.workspace_sharing.update_member_role(workspace_id, user_id, role)
        elif action == 'remove':
            if not self.workspace_sharing.is_member(workspace_id, user_id):
                return False
            return self.workspace_sharing.remove_member(workspace_id, user_id)
        return False

    def setup_routes(self):
        """Setup integrated API routes for enterprise features."""
        @self.app.route('/api/integrated/user/workspace/<workspace_id>/role', methods=['POST'])
        def manage_user_role_in_workspace_route(workspace_id):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                admin_user = decoded.get('user')
                if not admin_user:
                    return make_response(jsonify({'error': 'Invalid token payload'}), 401)

                data = request.get_json() if request.is_json else {}
                user_id = data.get('user_id')
                role = data.get('role')
                action = data.get('action')
                if not user_id or not action or (action in ['add', 'update'] and not role):
                    return make_response(jsonify({'error': 'Missing required fields'}), 400)

                if self.manage_user_role_in_workspace(workspace_id, user_id, role, action, admin_user):
                    return jsonify({'message': f'User {user_id} {action}ed in workspace {workspace_id}'})
                return make_response(jsonify({'error': f'Failed to {action} user {user_id} in workspace {workspace_id}'}), 403)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/integrated/access/<workspace_id>/<resource_type>/<resource_id>', methods=['GET'])
        def check_user_access_route(workspace_id, resource_type, resource_id):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                user_id = decoded.get('user')
                if not user_id:
                    return make_response(jsonify({'error': 'Invalid token payload'}), 401)

                permission = request.args.get('permission', 'read')
                has_access = self.check_user_access(user_id, workspace_id, permission, resource_type, resource_id)
                return jsonify({'has_access': has_access})
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)
