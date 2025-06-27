"""Conflict Resolution Module for Atlas Enterprise Features.

This module handles conflict resolution for simultaneous edits in real-time
collaboration for multi-user workspace implementation (ENT-002).
"""

import json
import os
from datetime import datetime
from typing import Dict, List

import jwt
from flask import Flask, jsonify, make_response, request


class ConflictResolution:
    def __init__(self, app: Flask, data_file: str = "conflict_data.json"):
        self.app = app
        self.data_file = data_file
        self.conflicts: Dict[str, List[Dict]] = {}
        self.secret_key = os.environ.get("JWT_SECRET_KEY", "mysecretkey")
        self.load_data()
        self.setup_routes()

    def load_data(self) -> None:
        """Load conflict data from the JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    self.conflicts = json.load(f)
        except Exception as e:
            print(f"Error loading conflict data: {e}")
            self.conflicts = {}

    def save_data(self) -> None:
        """Save conflict data to the JSON file."""
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.conflicts, f, indent=2)
        except Exception as e:
            print(f"Error saving conflict data: {e}")

    def log_conflict(
        self,
        resource_id: str,
        user_id: str,
        conflicting_content: str,
        base_content: str,
    ) -> Dict:
        """Log a conflict for a resource due to simultaneous edits."""
        if resource_id not in self.conflicts:
            self.conflicts[resource_id] = []

        conflict = {
            "user_id": user_id,
            "conflicting_content": conflicting_content,
            "base_content": base_content,
            "timestamp": datetime.utcnow().isoformat(),
            "resolved": False,
            "resolution": None,
        }
        self.conflicts[resource_id].append(conflict)
        self.save_data()
        return conflict

    def get_conflicts(self, resource_id: str) -> List[Dict]:
        """Get all conflicts for a specific resource."""
        return self.conflicts.get(resource_id, [])

    def resolve_conflict(
        self, resource_id: str, conflict_index: int, resolution: str, resolved_by: str
    ) -> bool:
        """Resolve a specific conflict for a resource."""
        if resource_id not in self.conflicts or conflict_index >= len(
            self.conflicts[resource_id]
        ):
            return False

        conflict = self.conflicts[resource_id][conflict_index]
        conflict["resolved"] = True
        conflict["resolution"] = resolution
        conflict["resolved_by"] = resolved_by
        conflict["resolved_at"] = datetime.utcnow().isoformat()
        self.save_data()
        return True

    def setup_routes(self):
        """Setup Flask routes for conflict resolution."""

        @self.app.route("/api/conflicts/log", methods=["POST"])
        def log_conflict_route():
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                data = request.get_json() if request.is_json else {}
                resource_id = data.get("resource_id")
                conflicting_content = data.get("conflicting_content")
                base_content = data.get("base_content")
                if not resource_id or not conflicting_content or not base_content:
                    return make_response(
                        jsonify({"error": "Missing required fields"}), 400
                    )

                conflict = self.log_conflict(
                    resource_id, decoded["user"], conflicting_content, base_content
                )
                return jsonify(
                    {
                        "message": f"Conflict logged for resource {resource_id}",
                        "conflict": conflict,
                    }
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/conflicts/<resource_id>", methods=["GET"])
        def get_conflicts_route(resource_id):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                jwt.decode(token, self.secret_key, algorithms=["HS256"])
                conflicts = self.get_conflicts(resource_id)
                return jsonify(conflicts)
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route(
            "/api/conflicts/resolve/<resource_id>/<int:conflict_index>", methods=["PUT"]
        )
        def resolve_conflict_route(resource_id, conflict_index):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                data = request.get_json() if request.is_json else {}
                resolution = data.get("resolution")
                if not resolution:
                    return make_response(
                        jsonify({"error": "Missing resolution field"}), 400
                    )

                if self.resolve_conflict(
                    resource_id, conflict_index, resolution, decoded["user"]
                ):
                    return jsonify(
                        {
                            "message": f"Conflict {conflict_index} resolved for resource {resource_id}"
                        }
                    )
                return make_response(
                    jsonify(
                        {
                            "error": f"Conflict {conflict_index} not found for resource {resource_id}"
                        }
                    ),
                    404,
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )
