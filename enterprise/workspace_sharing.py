"""Workspace Sharing Module for Atlas Enterprise Features.

This module handles team workspace sharing and collaboration tools for multi-user
workspace implementation (ENT-001).
"""

from typing import Dict, List, Optional
import json
import os
from flask import Flask, request, jsonify, make_response
import jwt
import datetime

class WorkspaceSharing:
    def __init__(self, app: Flask, data_file: str = 'workspace_data.json'):
        self.app = app
        self.data_file = data_file
        self.workspaces: Dict[str, Dict] = {}
        self.secret_key = os.environ.get('JWT_SECRET_KEY', 'mysecretkey')
        self.load_workspaces()
        self.setup_routes()

    def load_workspaces(self) -> None:
        """Load workspace data from the JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.workspaces = json.load(f)
        except Exception as e:
            print(f"Error loading workspaces: {e}")
            self.workspaces = {}

    def save_workspaces(self) -> None:
        """Save workspace data to the JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.workspaces, f, indent=2)
        except Exception as e:
            print(f"Error saving workspaces: {e}")

    def create_workspace(self, workspace_id: str, name: str, owner_id: str) -> bool:
        """Create a new workspace with the given ID and name, owned by the specified user."""
        if workspace_id in self.workspaces:
            return False
        
        self.workspaces[workspace_id] = {
            'name': name,
            'owner_id': owner_id,
            'members': {owner_id: 'owner'},
            'created_at': datetime.datetime.utcnow().isoformat(),
            'resources': {}
        }
        self.save_workspaces()
        return True

    def add_member(self, workspace_id: str, user_id: str, role: str = 'member') -> bool:
        """Add a member to a workspace with a specific role."""
        if workspace_id not in self.workspaces:
            return False
        
        self.workspaces[workspace_id]['members'][user_id] = role
        self.save_workspaces()
        return True

    def remove_member(self, workspace_id: str, user_id: str) -> bool:
        """Remove a member from a workspace."""
        if workspace_id not in self.workspaces or user_id not in self.workspaces[workspace_id]['members']:
            return False
        
        if self.workspaces[workspace_id]['owner_id'] == user_id:
            return False  # Cannot remove owner
        
        del self.workspaces[workspace_id]['members'][user_id]
        self.save_workspaces()
        return True

    def update_member_role(self, workspace_id: str, user_id: str, new_role: str) -> bool:
        """Update the role of a member in a workspace."""
        if workspace_id not in self.workspaces or user_id not in self.workspaces[workspace_id]['members']:
            return False
        
        if self.workspaces[workspace_id]['owner_id'] == user_id and new_role != 'owner':
            return False  # Cannot change owner's role
        
        self.workspaces[workspace_id]['members'][user_id] = new_role
        self.save_workspaces()
        return True

    def add_resource(self, workspace_id: str, resource_id: str, resource_type: str, permissions: Dict[str, List[str]]) -> bool:
        """Add a resource to a workspace with specific permissions for roles."""
        if workspace_id not in self.workspaces:
            return False
        
        self.workspaces[workspace_id]['resources'][resource_id] = {
            'type': resource_type,
            'permissions': permissions
        }
        self.save_workspaces()
        return True

    def check_access(self, workspace_id: str, user_id: str, resource_id: str, action: str) -> bool:
        """Check if a user has access to perform an action on a resource in a workspace."""
        if workspace_id not in self.workspaces or user_id not in self.workspaces[workspace_id]['members']:
            return False
        
        if resource_id not in self.workspaces[workspace_id]['resources']:
            return False
        
        user_role = self.workspaces[workspace_id]['members'][user_id]
        resource_permissions = self.workspaces[workspace_id]['resources'][resource_id]['permissions']
        return user_role in resource_permissions and action in resource_permissions[user_role]

    def get_workspace(self, workspace_id: str) -> Optional[Dict]:
        """Get workspace details."""
        return self.workspaces.get(workspace_id)

    def get_user_workspaces(self, user_id: str) -> List[Dict]:
        """Get list of workspaces a user is a member of."""
        user_workspaces = []
        for workspace_id, workspace in self.workspaces.items():
            if user_id in workspace['members']:
                user_workspaces.append({
                    'id': workspace_id,
                    'name': workspace['name'],
                    'role': workspace['members'][user_id]
                })
        return user_workspaces

    def setup_routes(self):
        """Setup Flask routes for workspace sharing."""
        @self.app.route('/api/workspaces', methods=['POST'])
        def create_workspace_route():
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                data = request.get_json() if request.is_json else {}
                workspace_id = data.get('workspace_id')
                name = data.get('name')
                if not workspace_id or not name:
                    return make_response(jsonify({'error': 'Missing required fields'}), 400)
                
                if self.create_workspace(workspace_id, name, decoded['user']):
                    return jsonify({'message': f'Workspace {workspace_id} created'})
                return make_response(jsonify({'error': f'Workspace {workspace_id} already exists'}), 409)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/workspaces/<workspace_id>/members', methods=['POST'])
        def add_member_route(workspace_id):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                workspace = self.get_workspace(workspace_id)
                if not workspace:
                    return make_response(jsonify({'error': f'Workspace {workspace_id} not found'}), 404)
                
                if workspace['owner_id'] != decoded['user'] and decoded['role'] not in ['admin', 'manager']:
                    return make_response(jsonify({'error': 'Insufficient permissions'}), 403)
                
                data = request.get_json() if request.is_json else {}
                user_id = data.get('user_id')
                role = data.get('role', 'member')
                if not user_id:
                    return make_response(jsonify({'error': 'Missing user_id field'}), 400)
                
                if self.add_member(workspace_id, user_id, role):
                    return jsonify({'message': f'User {user_id} added to workspace {workspace_id} as {role}'})
                return make_response(jsonify({'error': f'Workspace {workspace_id} not found'}), 404)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/workspaces/<workspace_id>/members/<user_id>', methods=['DELETE'])
        def remove_member_route(workspace_id, user_id):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                workspace = self.get_workspace(workspace_id)
                if not workspace:
                    return make_response(jsonify({'error': f'Workspace {workspace_id} not found'}), 404)
                
                if workspace['owner_id'] != decoded['user'] and decoded['role'] not in ['admin', 'manager']:
                    return make_response(jsonify({'error': 'Insufficient permissions'}), 403)
                
                if self.remove_member(workspace_id, user_id):
                    return jsonify({'message': f'User {user_id} removed from workspace {workspace_id}'})
                return make_response(jsonify({'error': f'User {user_id} not found in workspace {workspace_id} or cannot be removed'}), 404)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/workspaces/<workspace_id>/members/<user_id>/role', methods=['PUT'])
        def update_member_role_route(workspace_id, user_id):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                workspace = self.get_workspace(workspace_id)
                if not workspace:
                    return make_response(jsonify({'error': f'Workspace {workspace_id} not found'}), 404)
                
                if workspace['owner_id'] != decoded['user'] and decoded['role'] not in ['admin', 'manager']:
                    return make_response(jsonify({'error': 'Insufficient permissions'}), 403)
                
                data = request.get_json() if request.is_json else {}
                new_role = data.get('role')
                if not new_role:
                    return make_response(jsonify({'error': 'Missing role field'}), 400)
                
                if self.update_member_role(workspace_id, user_id, new_role):
                    return jsonify({'message': f'Role updated for user {user_id} in workspace {workspace_id} to {new_role}'})
                return make_response(jsonify({'error': f'User {user_id} not found in workspace {workspace_id} or role update not allowed'}), 404)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/workspaces/<workspace_id>/resources', methods=['POST'])
        def add_resource_route(workspace_id):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                workspace = self.get_workspace(workspace_id)
                if not workspace:
                    return make_response(jsonify({'error': f'Workspace {workspace_id} not found'}), 404)
                
                if workspace['owner_id'] != decoded['user'] and decoded['role'] not in ['admin', 'manager']:
                    return make_response(jsonify({'error': 'Insufficient permissions'}), 403)
                
                data = request.get_json() if request.is_json else {}
                resource_id = data.get('resource_id')
                resource_type = data.get('resource_type')
                permissions = data.get('permissions', {})
                if not resource_id or not resource_type or not permissions:
                    return make_response(jsonify({'error': 'Missing required fields'}), 400)
                
                if self.add_resource(workspace_id, resource_id, resource_type, permissions):
                    return jsonify({'message': f'Resource {resource_id} added to workspace {workspace_id}'})
                return make_response(jsonify({'error': f'Workspace {workspace_id} not found'}), 404)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/workspaces/<workspace_id>/access', methods=['POST'])
        def check_access_route(workspace_id):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                data = request.get_json() if request.is_json else {}
                resource_id = data.get('resource_id')
                action = data.get('action')
                if not resource_id or not action:
                    return make_response(jsonify({'error': 'Missing required fields'}), 400)
                
                has_access = self.check_access(workspace_id, decoded['user'], resource_id, action)
                return jsonify({'has_access': has_access})
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/workspaces', methods=['GET'])
        def get_user_workspaces_route():
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                workspaces = self.get_user_workspaces(decoded['user'])
                return jsonify(workspaces)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)

        @self.app.route('/api/workspaces/<workspace_id>', methods=['GET'])
        def get_workspace_route(workspace_id):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return make_response(jsonify({'error': 'Authorization required'}), 401)
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                workspace = self.get_workspace(workspace_id)
                if not workspace:
                    return make_response(jsonify({'error': f'Workspace {workspace_id} not found'}), 404)
                
                if decoded['user'] not in workspace['members'] and decoded['role'] != 'admin':
                    return make_response(jsonify({'error': 'Insufficient permissions'}), 403)
                
                return jsonify(workspace)
            except Exception as e:
                return make_response(jsonify({'error': f'Invalid token: {str(e)}'}), 401)
