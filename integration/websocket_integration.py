"""
Integration Module for WebSocket in Atlas Main App (ASC-032)
This module integrates WebSocket client functionality into the Atlas application for real-time collaboration.
"""

import os
import sys
from typing import Any, Dict

# Add the collaboration directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../collaboration"))

from websocket_client import WebSocketClient


class CollaborationManager:
    """Manages real-time collaboration features in Atlas using WebSocket."""

    def __init__(self, server_url: str, user_id: str, team_id: str):
        self.user_id = user_id
        self.team_id = team_id
        self.server_url = server_url
        self.client = WebSocketClient(server_url, team_id, self.handle_update)
        self.task_update_callback = None

    def set_task_update_callback(self, callback: callable):
        """Set callback for task updates to update UI or data."""
        self.task_update_callback = callback

    def start(self):
        """Start the WebSocket connection for real-time updates."""
        print(f"Starting collaboration for user {self.user_id} in team {self.team_id}")
        self.client.start()

    def stop(self):
        """Stop the WebSocket connection."""
        print(f"Stopping collaboration for user {self.user_id}")
        self.client.stop()

    def handle_update(self, message: Dict[str, Any]):
        """
        Handle incoming WebSocket updates and trigger UI updates.

        Args:
            message: Received WebSocket message
        """
        try:
            message_type = message.get("type")
            if message_type == "task_update":
                task_data = message.get("data", {})
                print(
                    f"Processing task update for task {task_data.get('id', 'unknown')}"
                )
                if self.task_update_callback:
                    self.task_update_callback(task_data)
            else:
                print(f"Unhandled message type: {message_type}")
        except Exception as e:
            print(f"Error handling WebSocket update: {e}")

    def send_task_update(self, task_data: Dict[str, Any]):
        """Send task update to team members via WebSocket (placeholder for server integration)."""
        # In a full implementation, this would send data to Redis or directly via WebSocket
        print(f"Sending task update to team {self.team_id}: {task_data}")
        # For now, simulate local update
        self.handle_update({"type": "task_update", "data": task_data})


# Example integration in Atlas main app
def integrate_collaboration(app_instance):
    """Integrate collaboration manager into the Atlas application."""
    # Placeholder user and team IDs (would come from user login)
    user_id = "user_123"
    team_id = "team_456"
    server_url = "ws://localhost:8765"

    collab_manager = CollaborationManager(server_url, user_id, team_id)

    # Set callback to update UI or task store
    def update_task_ui(data):
        print(f"Updating UI with task data: {data}")
        # app_instance.update_task(data)  # Update task store or UI

    collab_manager.set_task_update_callback(update_task_ui)
    collab_manager.start()
    return collab_manager


if __name__ == "__main__":
    manager = integrate_collaboration(None)
    # Simulate a task update
    manager.send_task_update(
        {"id": "task_789", "title": "Test Task", "completed": False}
    )
    import asyncio

    asyncio.run(asyncio.sleep(10))  # Run for a bit to see updates
    manager.stop()
