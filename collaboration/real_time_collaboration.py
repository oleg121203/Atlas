import asyncio
import websockets
import json
import threading
from datetime import datetime

class RealTimeCollaboration:
    """Manages real-time collaboration features for workflows and tasks."""

    def __init__(self, server_uri="ws://localhost:8765"):
        """Initialize the real-time collaboration system.

        Args:
            server_uri (str): The URI of the WebSocket server for collaboration.
        """
        self.server_uri = server_uri
        self.websocket = None
        self.connected = False
        self.clients = set()
        self.message_queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop()
        if self.loop.is_running():
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
            self.thread.start()
        else:
            self.thread = None

    async def connect(self):
        """Connect to the WebSocket server for real-time collaboration."""
        try:
            self.websocket = await websockets.connect(self.server_uri)
            self.connected = True
            print(f"Connected to collaboration server at {self.server_uri}")
            asyncio.create_task(self.listen_for_messages())
        except Exception as e:
            print(f"Failed to connect to collaboration server: {e}")
            self.connected = False

    async def listen_for_messages(self):
        """Listen for incoming messages from the server."""
        while self.connected:
            try:
                message = await self.websocket.recv()
                await self.message_queue.put(message)
                self.handle_message(message)
            except websockets.ConnectionClosed:
                self.connected = False
                print("Connection to collaboration server closed.")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")

    def handle_message(self, message):
        """Handle incoming messages from the collaboration server.

        Args:
            message (str): The message received from the server.
        """
        try:
            data = json.loads(message)
            action = data.get('action')
            payload = data.get('payload', {})

            if action == 'workflow_update':
                print(f"Workflow updated by {payload.get('user')}: {payload.get('workflow_id')}")
                self.on_workflow_update(payload)
            elif action == 'presence_update':
                print(f"Presence update: {payload.get('user')} is {payload.get('status')}")
                self.on_presence_update(payload)
            elif action == 'conflict_notification':
                print(f"Conflict detected in workflow {payload.get('workflow_id')} by {payload.get('user')}")
                self.on_conflict_notification(payload)
            else:
                print(f"Unknown action received: {action}")
        except json.JSONDecodeError:
            print("Error decoding message from server.")
        except Exception as e:
            print(f"Error handling message: {e}")

    def on_workflow_update(self, payload):
        """Callback for workflow updates.

        Args:
            payload (dict): The update data for the workflow.
        """
        # Update local workflow state
        pass

    def on_presence_update(self, payload):
        """Callback for presence updates.

        Args:
            payload (dict): The presence data for users.
        """
        # Update UI or internal state for presence indicators
        pass

    def on_conflict_notification(self, payload):
        """Callback for conflict notifications.

        Args:
            payload (dict): The conflict data.
        """
        # Notify user or attempt conflict resolution
        pass

    async def send_update(self, action, payload):
        """Send an update to the collaboration server.

        Args:
            action (str): The type of update action.
            payload (dict): The data associated with the update.
        """
        if not self.connected or self.websocket is None:
            print("Cannot send update: Not connected to server.")
            return

        message = json.dumps({
            'action': action,
            'payload': payload,
            'timestamp': datetime.utcnow().isoformat()
        })
        try:
            await self.websocket.send(message)
            print(f"Sent update: {action}")
        except Exception as e:
            print(f"Error sending update: {e}")

    def start(self):
        """Start the collaboration client."""
        asyncio.run_coroutine_threadsafe(self.connect(), self.loop)

    def stop(self):
        """Stop the collaboration client."""
        self.connected = False
        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
            self.websocket = None
            print("Disconnected from collaboration server.")
        if self.thread:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join(timeout=2)

if __name__ == "__main__":
    # Example usage
    collab = RealTimeCollaboration()
    collab.start()
    try:
        # Simulate sending an update after connection
        import time
        time.sleep(2)  # Give time for connection
        asyncio.run_coroutine_threadsafe(
            collab.send_update('test_action', {'message': 'Hello, collaboration!'}),
            collab.loop
        )
        time.sleep(10)  # Keep running to listen for messages
    finally:
        collab.stop()
