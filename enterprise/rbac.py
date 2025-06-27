"""Role-Based Access Control (RBAC) Module for Atlas Enterprise Features.

This module implements role-based access control for multi-user workspace
implementation (ENT-001), defining roles, permissions, and access policies.
"""

import json
import os
from typing import Dict, List, Set

import jwt
from flask import Flask, jsonify, make_response, request


class RBACManager:
    def __init__(self, app: Flask, policy_file: str = "rbac_policies.json"):
        self.app = app
        self.policy_file = policy_file
        self.roles: Dict[str, Dict[str, Set[str]]] = {
            "admin": {
                "permissions": {
                    "read",
                    "write",
                    "delete",
                    "manage_users",
                    "manage_roles",
                }
            },
            "manager": {"permissions": {"read", "write", "manage_tasks"}},
            "user": {"permissions": {"read", "write"}},
            "guest": {"permissions": {"read"}},
        }
        self.policies: Dict[str, Dict[str, List[str]]] = {}
        self.secret_key = os.environ.get("JWT_SECRET_KEY", "mysecretkey")
        self.load_policies()
        self.setup_routes()

    def load_policies(self) -> None:
        """Load RBAC policies from the JSON file."""
        try:
            if os.path.exists(self.policy_file):
                with open(self.policy_file, "r") as f:
                    self.policies = json.load(f)
        except Exception as e:
            print(f"Error loading policies: {e}")
            self.policies = {}

    def save_policies(self) -> None:
        """Save RBAC policies to the JSON file."""
        try:
            with open(self.policy_file, "w") as f:
                json.dump(self.policies, f, indent=2)
        except Exception as e:
            print(f"Error saving policies: {e}")

    def check_permission(self, role: str, permission: str) -> bool:
        """Check if a role has a specific permission."""
        return permission in self.roles.get(role, {}).get("permissions", set())

    def check_policy(self, user_id: str, resource: str, action: str) -> bool:
        """Check if a user has permission for an action on a resource based on policies."""
        user_policies = self.policies.get(user_id, {})
        resource_policies = user_policies.get(resource, [])
        return action in resource_policies

    def add_role(self, role_name: str, permissions: Set[str]) -> bool:
        """Add a new role with specified permissions."""
        if role_name in self.roles:
            return False
        self.roles[role_name] = {"permissions": permissions}
        return True

    def update_role_permissions(self, role_name: str, permissions: Set[str]) -> bool:
        """Update permissions for an existing role."""
        if role_name not in self.roles:
            return False
        self.roles[role_name]["permissions"] = permissions
        return True

    def add_policy(self, user_id: str, resource: str, actions: List[str]) -> None:
        """Add or update a policy for a user on a specific resource."""
        if user_id not in self.policies:
            self.policies[user_id] = {}
        self.policies[user_id][resource] = actions
        self.save_policies()

    def remove_policy(self, user_id: str, resource: str) -> bool:
        """Remove a policy for a user on a specific resource."""
        if user_id in self.policies and resource in self.policies[user_id]:
            del self.policies[user_id][resource]
            if not self.policies[user_id]:
                del self.policies[user_id]
            self.save_policies()
            return True
        return False

    def setup_routes(self):
        """Setup Flask routes for RBAC management."""

        @self.app.route("/api/rbac/roles", methods=["POST"])
        def add_role_route():
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                if decoded["role"] != "admin":
                    return make_response(
                        jsonify({"error": "Insufficient permissions"}), 403
                    )

                data = request.get_json()
                role_name = data.get("role_name")
                permissions = set(data.get("permissions", []))
                if not role_name or not permissions:
                    return make_response(
                        jsonify({"error": "Missing required fields"}), 400
                    )

                if self.add_role(role_name, permissions):
                    return jsonify(
                        {
                            "message": f"Role {role_name} added with permissions {permissions}"
                        }
                    )
                return make_response(
                    jsonify({"error": f"Role {role_name} already exists"}), 409
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/rbac/roles/<role_name>", methods=["PUT"])
        def update_role_route(role_name):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                if decoded["role"] != "admin":
                    return make_response(
                        jsonify({"error": "Insufficient permissions"}), 403
                    )

                data = request.get_json()
                permissions = set(data.get("permissions", []))
                if not permissions:
                    return make_response(
                        jsonify({"error": "Missing permissions field"}), 400
                    )

                if self.update_role_permissions(role_name, permissions):
                    return jsonify(
                        {"message": f"Permissions updated for role {role_name}"}
                    )
                return make_response(
                    jsonify({"error": f"Role {role_name} not found"}), 404
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/rbac/policies", methods=["POST"])
        def add_policy_route():
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                if decoded["role"] not in ["admin", "manager"]:
                    return make_response(
                        jsonify({"error": "Insufficient permissions"}), 403
                    )

                data = request.get_json()
                user_id = data.get("user_id")
                resource = data.get("resource")
                actions = data.get("actions", [])
                if not user_id or not resource or not actions:
                    return make_response(
                        jsonify({"error": "Missing required fields"}), 400
                    )

                self.add_policy(user_id, resource, actions)
                return jsonify(
                    {"message": f"Policy added for user {user_id} on {resource}"}
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/rbac/policies/<user_id>/<resource>", methods=["DELETE"])
        def remove_policy_route(user_id, resource):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                if decoded["role"] not in ["admin", "manager"]:
                    return make_response(
                        jsonify({"error": "Insufficient permissions"}), 403
                    )

                if self.remove_policy(user_id, resource):
                    return jsonify(
                        {"message": f"Policy removed for user {user_id} on {resource}"}
                    )
                return make_response(
                    jsonify(
                        {"error": f"Policy not found for user {user_id} on {resource}"}
                    ),
                    404,
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/rbac/check_permission", methods=["POST"])
        def check_permission_route():
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                data = request.get_json()
                permission = data.get("permission")
                if not permission:
                    return make_response(
                        jsonify({"error": "Missing permission field"}), 400
                    )

                has_permission = self.check_permission(decoded["role"], permission)
                return jsonify({"has_permission": has_permission})
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )
