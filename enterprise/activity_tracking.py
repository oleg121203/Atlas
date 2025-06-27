"""Activity Tracking Module for Atlas Enterprise Features.

This module handles user activity tracking and audit logs for multi-user
workspace implementation (ENT-001).
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import jwt
from flask import Flask, jsonify, make_response, request


class ActivityTracking:
    def __init__(self, app: Flask, data_file: str = "activity_logs.json"):
        self.app = app
        self.data_file = data_file
        self.activities: List[Dict] = []
        self.secret_key = os.environ.get("JWT_SECRET_KEY", "mysecretkey")
        self.load_activities()
        self.setup_routes()

    def load_activities(self) -> None:
        """Load activity logs from the JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    self.activities = json.load(f)
        except Exception as e:
            print(f"Error loading activities: {e}")
            self.activities = []

    def save_activities(self) -> None:
        """Save activity logs to the JSON file."""
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.activities, f, indent=2)
        except Exception as e:
            print(f"Error saving activities: {e}")

    def log_activity(
        self,
        user_id: str,
        action: str,
        resource_id: str,
        details: Optional[Dict] = None,
    ) -> None:
        """Log a user activity with timestamp."""
        activity = {
            "user_id": user_id,
            "action": action,
            "resource_id": resource_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
        }
        self.activities.append(activity)
        self.save_activities()

    def get_user_activities(self, user_id: str) -> List[Dict]:
        """Get all activities for a specific user."""
        return [
            activity for activity in self.activities if activity["user_id"] == user_id
        ]

    def get_resource_activities(self, resource_id: str) -> List[Dict]:
        """Get all activities for a specific resource."""
        return [
            activity
            for activity in self.activities
            if activity["resource_id"] == resource_id
        ]

    def get_all_activities(self) -> List[Dict]:
        """Get all activities (admin access only)."""
        return self.activities

    def setup_routes(self):
        """Setup Flask routes for activity tracking."""

        @self.app.route("/api/activities/log", methods=["POST"])
        def log_activity_route():
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                data = request.get_json() if request.is_json else {}
                action = data.get("action")
                resource_id = data.get("resource_id")
                details = data.get("details", {})
                if not action or not resource_id:
                    return make_response(
                        jsonify({"error": "Missing required fields"}), 400
                    )

                self.log_activity(decoded["user"], action, resource_id, details)
                return jsonify(
                    {"message": f"Activity logged for user {decoded['user']}"}
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/activities/user", methods=["GET"])
        def get_user_activities_route():
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                activities = self.get_user_activities(decoded["user"])
                return jsonify(activities)
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/activities/resource/<resource_id>", methods=["GET"])
        def get_resource_activities_route(resource_id):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                if decoded["role"] not in ["admin", "manager"]:
                    return make_response(
                        jsonify({"error": "Insufficient permissions"}), 403
                    )
                activities = self.get_resource_activities(resource_id)
                return jsonify(activities)
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/activities/all", methods=["GET"])
        def get_all_activities_route():
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
                activities = self.get_all_activities()
                return jsonify(activities)
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )
