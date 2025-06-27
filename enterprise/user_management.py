"""User Management Module for Atlas Enterprise Features.

This module handles user creation, authentication, and management for multi-user
workspace implementation (ENT-001).
"""

import datetime
import hashlib
import json
import os
from typing import Dict, List, Optional

import jwt  # Corrected import statement
from flask import Flask, jsonify, make_response, request


class UserManager:
    def __init__(self, app: Flask, data_file: str = "user_data.json"):
        self.app = app
        self.data_file = data_file
        self.secret_key = os.environ.get("JWT_SECRET_KEY", "mysecretkey")
        self.users: Dict[str, dict] = {}
        self.load_users()
        self.setup_routes()

    def load_users(self) -> None:
        """Load user data from the JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    self.users = json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = {}

    def save_users(self) -> None:
        """Save user data to the JSON file."""
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")

    def hash_password(self, password: str) -> str:
        """Hash the password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(
        self, username: str, password: str, email: str, role: str = "user"
    ) -> bool:
        """Create a new user with the given credentials and role."""
        if username in self.users:
            return False

        self.users[username] = {
            "password": self.hash_password(password),
            "email": email,
            "role": role,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "last_login": None,
        }
        self.save_users()
        return True

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token if successful."""
        if username not in self.users:
            return None

        stored_password = self.users[username]["password"]
        if self.hash_password(password) == stored_password:
            self.users[username]["last_login"] = datetime.datetime.utcnow().isoformat()
            self.save_users()
            token = jwt.encode(
                {
                    "user": username,
                    "role": self.users[username]["role"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                },
                self.secret_key,
                algorithm="HS256",
            )
            return token
        return None

    def get_user(self, username: str) -> Optional[dict]:
        """Get user information."""
        return self.users.get(username)

    def update_user_role(self, username: str, new_role: str) -> bool:
        """Update the role of a user."""
        if username in self.users:
            self.users[username]["role"] = new_role
            self.save_users()
            return True
        return False

    def delete_user(self, username: str) -> bool:
        """Delete a user from the system."""
        if username in self.users:
            del self.users[username]
            self.save_users()
            return True
        return False

    def get_all_users(self) -> List[dict]:
        """Return list of all users with non-sensitive data."""
        return [
            {k: v for k, v in user.items() if k != "password"}
            for user in self.users.values()
        ]

    def list_users(self) -> List[dict]:
        """Return list of all users with non-sensitive data."""
        return [
            {k: v for k, v in user.items() if k != "password"}
            for user in self.users.values()
        ]

    def update_role(self, username: str, new_role: str) -> bool:
        """Update the role of a user."""
        if username in self.users:
            self.users[username]["role"] = new_role
            self.save_users()
            return True
        return False

    def setup_routes(self):
        """Setup Flask routes for user management."""

        @self.app.route("/api/users/register", methods=["POST"])
        def register_user():
            data = request.get_json() if request.is_json else {}
            username = data.get("username")
            password = data.get("password")
            email = data.get("email")
            role = data.get("role", "user")

            if not username or not password or not email:
                return make_response(jsonify({"error": "Missing required fields"}), 400)

            if username in self.users:
                return make_response(jsonify({"error": "Username already exists"}), 409)

            if self.create_user(username, password, email, role):
                return jsonify({"message": f"User {username} registered successfully"})
            return make_response(jsonify({"error": "Failed to register user"}), 500)

        @self.app.route("/api/users/login", methods=["POST"])
        def login_user():
            data = request.get_json() if request.is_json else {}
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(
                    jsonify({"error": "Missing username or password"}), 400
                )

            token = self.authenticate_user(username, password)
            if token:
                return jsonify({"token": token})
            return make_response(jsonify({"error": "Invalid credentials"}), 401)

        @self.app.route("/api/users", methods=["GET"])
        def get_users():
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                if decoded["role"] != "admin":
                    return make_response(
                        jsonify({"error": "Insufficient permissions"}), 403
                    )
                users = self.list_users()
                return jsonify(users)
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/users/<username>/role", methods=["PUT"])
        def update_user_role(username):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                if decoded["role"] != "admin":
                    return make_response(
                        jsonify({"error": "Insufficient permissions"}), 403
                    )

                data = request.get_json() if request.is_json else {}
                new_role = data.get("role")
                if not new_role:
                    return make_response(jsonify({"error": "Missing role field"}), 400)

                if self.update_role(username, new_role):
                    return jsonify(
                        {"message": f"Role updated for user {username} to {new_role}"}
                    )
                return make_response(
                    jsonify({"error": f"User {username} not found"}), 404
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/users/<username>", methods=["DELETE"])
        def delete_user_route(username):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                if decoded["role"] != "admin":
                    return make_response(
                        jsonify({"error": "Insufficient permissions"}), 403
                    )

                if self.delete_user(username):
                    return jsonify({"message": f"User {username} deleted successfully"})
                return make_response(
                    jsonify({"error": f"User {username} not found"}), 404
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )
