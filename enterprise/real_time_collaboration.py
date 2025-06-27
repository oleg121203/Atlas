"""Real-Time Collaboration Module for Atlas Enterprise Features.

This module handles real-time collaboration features like chat, collaborative editing,
and shared task management for multi-user workspace implementation (ENT-002).
"""

import json
import os
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional

import jwt
import websockets
from flask import Flask, jsonify, make_response, request


class RealTimeCollaboration:
    def __init__(self, app: Flask, data_file: str = "collaboration_data.json"):
        self.app = app
        self.data_file = data_file
        self.chats: Dict[str, List[Dict]] = {}
        self.documents: Dict[str, Dict] = {}
        self.tasks: Dict[str, Dict] = {}
        self.secret_key = os.environ.get("JWT_SECRET_KEY", "mysecretkey")
        self.lock = Lock()
        self.load_data()
        self.setup_routes()
        self.websocket_connections: Dict[
            str, List[websockets.WebSocketServerProtocol]
        ] = {}

    def load_data(self) -> None:
        """Load collaboration data from the JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.chats = data.get("chats", {})
                    self.documents = data.get("documents", {})
                    self.tasks = data.get("tasks", {})
        except Exception as e:
            print(f"Error loading collaboration data: {e}")
            self.chats = {}
            self.documents = {}
            self.tasks = {}

    def save_data(self) -> None:
        """Save collaboration data to the JSON file."""
        try:
            with open(self.data_file, "w") as f:
                json.dump(
                    {
                        "chats": self.chats,
                        "documents": self.documents,
                        "tasks": self.tasks,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            print(f"Error saving collaboration data: {e}")

    def send_chat_message(self, workspace_id: str, user_id: str, message: str) -> Dict:
        """Send a chat message in a workspace."""
        if workspace_id not in self.chats:
            self.chats[workspace_id] = []

        chat_message = {
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.chats[workspace_id].append(chat_message)
        self.save_data()
        return chat_message

    def get_chat_history(self, workspace_id: str) -> List[Dict]:
        """Get chat history for a workspace."""
        return self.chats.get(workspace_id, [])

    def update_document(
        self, document_id: str, content: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Update document content and maintain version history."""
        with self.lock:
            if document_id not in self.documents:
                self.documents[document_id] = {
                    "id": document_id,
                    "content": content,
                    "last_updated_by": user_id,
                    "last_updated_at": datetime.utcnow().isoformat(),
                    "history": [],
                }
            else:
                old_content = self.documents[document_id]["content"]
                old_user = self.documents[document_id]["last_updated_by"]
                old_timestamp = self.documents[document_id]["last_updated_at"]
                self.documents[document_id]["content"] = content
                self.documents[document_id]["last_updated_by"] = user_id
                self.documents[document_id]["last_updated_at"] = (
                    datetime.utcnow().isoformat()
                )
                self.documents[document_id]["history"].insert(
                    0,
                    {
                        "content": old_content,
                        "updated_by": old_user,
                        "updated_at": old_timestamp,
                    },
                )
                if (
                    len(self.documents[document_id]["history"]) > 10
                ):  # Limit history to last 10 updates
                    self.documents[document_id]["history"] = self.documents[
                        document_id
                    ]["history"][:10]
            self.save_data()
            return self.documents.get(document_id)

    def get_document(self, document_id: str) -> Optional[Dict]:
        """Get a collaborative document."""
        return self.documents.get(document_id)

    def create_task(
        self,
        workspace_id: str,
        task_id: str,
        title: str,
        description: str,
        assigned_to: List[str],
        created_by: str,
    ) -> bool:
        """Create a shared task in a workspace."""
        if workspace_id not in self.tasks:
            self.tasks[workspace_id] = {}

        if task_id in self.tasks[workspace_id]:
            return False

        self.tasks[workspace_id][task_id] = {
            "title": title,
            "description": description,
            "assigned_to": assigned_to,
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat(),
            "status": "open",
            "updates": [],
        }
        self.save_data()
        return True

    def update_task_status(
        self, workspace_id: str, task_id: str, status: str, updated_by: str
    ) -> bool:
        """Update the status of a shared task."""
        if workspace_id not in self.tasks or task_id not in self.tasks[workspace_id]:
            return False

        self.tasks[workspace_id][task_id]["status"] = status
        self.tasks[workspace_id][task_id]["updates"].append(
            {
                "status": status,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow().isoformat(),
            }
        )
        self.save_data()
        return True

    def get_tasks(self, workspace_id: str) -> Dict:
        """Get all tasks in a workspace."""
        return self.tasks.get(workspace_id, {})

    async def handle_websocket(
        self, websocket: websockets.WebSocketServerProtocol, path: str
    ):
        """Handle WebSocket connections for real-time updates."""
        workspace_id = path.strip("/")
        if workspace_id not in self.websocket_connections:
            self.websocket_connections[workspace_id] = []
        self.websocket_connections[workspace_id].append(websocket)

        try:
            async for message in websocket:
                data = json.loads(message)
                action = data.get("action")
                if action == "chat":
                    user_id = data.get("user_id")
                    chat_message = data.get("message")
                    sent_message = self.send_chat_message(
                        workspace_id, user_id, chat_message
                    )
                    await self.broadcast_to_workspace(
                        workspace_id,
                        json.dumps({"type": "chat", "message": sent_message}),
                    )
                elif action == "document_update":
                    document_id = data.get("document_id")
                    content = data.get("content")
                    user_id = data.get("user_id")
                    updated_doc = self.update_document(document_id, content, user_id)
                    if updated_doc:
                        await self.broadcast_to_workspace(
                            workspace_id,
                            json.dumps(
                                {
                                    "type": "document_update",
                                    "document_id": document_id,
                                    "content": updated_doc["content"],
                                    "last_updated_by": updated_doc["last_updated_by"],
                                    "last_updated_at": updated_doc["last_updated_at"],
                                }
                            ),
                        )
                elif action == "task_update":
                    task_id = data.get("task_id")
                    status = data.get("status")
                    user_id = data.get("user_id")
                    if self.update_task_status(workspace_id, task_id, status, user_id):
                        await self.broadcast_to_workspace(
                            workspace_id,
                            json.dumps(
                                {
                                    "type": "task_update",
                                    "task_id": task_id,
                                    "status": status,
                                    "updated_by": user_id,
                                    "updated_at": datetime.utcnow().isoformat(),
                                }
                            ),
                        )
        except websockets.exceptions.ConnectionClosed:
            self.websocket_connections[workspace_id].remove(websocket)
            if not self.websocket_connections[workspace_id]:
                del self.websocket_connections[workspace_id]

    async def broadcast_to_workspace(self, workspace_id: str, message: str):
        """Broadcast a message to all connected clients in a workspace."""
        if workspace_id in self.websocket_connections:
            for connection in self.websocket_connections[workspace_id]:
                await connection.send(message)

    def setup_routes(self):
        """Setup Flask routes for real-time collaboration."""

        @self.app.route("/api/collaboration/chat/<workspace_id>", methods=["POST"])
        def send_chat_message_route(workspace_id):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                data = request.get_json() if request.is_json else {}
                message = data.get("message")
                if not message:
                    return make_response(
                        jsonify({"error": "Missing message field"}), 400
                    )

                chat_message = self.send_chat_message(
                    workspace_id, decoded["user"], message
                )
                return jsonify(chat_message)
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/collaboration/chat/<workspace_id>", methods=["GET"])
        def get_chat_history_route(workspace_id):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                jwt.decode(token, self.secret_key, algorithms=["HS256"])
                chat_history = self.get_chat_history(workspace_id)
                return jsonify(chat_history)
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/collaboration/document/<document_id>", methods=["PUT"])
        def update_document_route(document_id):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                data = request.get_json() if request.is_json else {}
                content = data.get("content")
                if not content:
                    return make_response(
                        jsonify({"error": "Missing content field"}), 400
                    )

                updated_doc = self.update_document(
                    document_id, content, decoded["user"]
                )
                if updated_doc:
                    return jsonify(
                        {
                            "message": f"Document {document_id} updated",
                            "document": updated_doc,
                        }
                    )
                return make_response(
                    jsonify({"error": f"Document {document_id} not found"}), 404
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/collaboration/document/<document_id>", methods=["GET"])
        def get_document_route(document_id):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                jwt.decode(token, self.secret_key, algorithms=["HS256"])
                document = self.get_document(document_id)
                if document:
                    return jsonify(document)
                return make_response(
                    jsonify({"error": f"Document {document_id} not found"}), 404
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/collaboration/task/<workspace_id>", methods=["POST"])
        def create_task_route(workspace_id):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                data = request.get_json() if request.is_json else {}
                task_id = data.get("task_id")
                title = data.get("title")
                description = data.get("description", "")
                assigned_to = data.get("assigned_to", [])
                if not task_id or not title:
                    return make_response(
                        jsonify({"error": "Missing required fields"}), 400
                    )

                if self.create_task(
                    workspace_id,
                    task_id,
                    title,
                    description,
                    assigned_to,
                    decoded["user"],
                ):
                    return jsonify(
                        {
                            "message": f"Task {task_id} created in workspace {workspace_id}"
                        }
                    )
                return make_response(
                    jsonify(
                        {
                            "error": f"Task {task_id} already exists in workspace {workspace_id}"
                        }
                    ),
                    409,
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route(
            "/api/collaboration/task/<workspace_id>/<task_id>/status", methods=["PUT"]
        )
        def update_task_status_route(workspace_id, task_id):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                data = request.get_json() if request.is_json else {}
                status = data.get("status")
                if not status:
                    return make_response(
                        jsonify({"error": "Missing status field"}), 400
                    )

                if self.update_task_status(
                    workspace_id, task_id, status, decoded["user"]
                ):
                    return jsonify(
                        {"message": f"Task {task_id} status updated to {status}"}
                    )
                return make_response(
                    jsonify(
                        {
                            "error": f"Task {task_id} not found in workspace {workspace_id}"
                        }
                    ),
                    404,
                )
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )

        @self.app.route("/api/collaboration/tasks/<workspace_id>", methods=["GET"])
        def get_tasks_route(workspace_id):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                return make_response(jsonify({"error": "Authorization required"}), 401)

            try:
                token = auth_header.split("Bearer ")[1]
                jwt.decode(token, self.secret_key, algorithms=["HS256"])
                tasks = self.get_tasks(workspace_id)
                return jsonify(tasks)
            except Exception as e:
                return make_response(
                    jsonify({"error": f"Invalid token: {str(e)}"}), 401
                )
