import asyncio
import websockets
import json
from datetime import datetime

class CollaborationServer:
    """Manages the WebSocket server for real-time collaboration."""

    def __init__(self, host="localhost", port=8765):
        """Initialize the collaboration server.

        Args:
            host (str): The host address for the server.
            port (int): The port number for the server.
        """
        self.host = host
        self.port = port
        self.clients = set()
        self.server = None

    async def handle_connection(self, websocket, path):
        """Handle a new WebSocket connection.

        Args:
            websocket: The WebSocket connection object.
            path: The path of the connection.
        """
        print(f"New client connected: {websocket.remote_address}")
        self.clients.add(websocket)
        try:
            await self.broadcast({
                'action': 'presence_update',
                'payload': {'user': f"User-{websocket.remote_address[1]}", 'status': 'online'}
            })
            async for message in websocket:
                await self.handle_message(message, websocket)
        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected: {websocket.remote_address}")
            self.clients.remove(websocket)
            await self.broadcast({
                'action': 'presence_update',
                'payload': {'user': f"User-{websocket.remote_address[1]}", 'status': 'offline'}
            })
        except Exception as e:
            print(f"Error handling connection: {e}")

    async def handle_message(self, message, websocket):
        """Handle incoming messages from clients.

        Args:
            message (str): The message received from the client.
            websocket: The WebSocket connection object of the sender.
        """
        try:
            data = json.loads(message)
            action = data.get('action')
            payload = data.get('payload', {})
            timestamp = data.get('timestamp', datetime.utcnow().isoformat())

            print(f"Received {action} from {websocket.remote_address}")

            # Broadcast the message to all other clients
            response = {
                'action': action,
                'payload': payload,
                'timestamp': timestamp
            }
            await self.broadcast(response, exclude=websocket)

            # Check for conflicts (simplified example)
            if action == 'workflow_update':
                # Simulate conflict detection logic
                if self.check_for_conflict(payload):
                    await websocket.send(json.dumps({
                        'action': 'conflict_notification',
                        'payload': {'workflow_id': payload.get('workflow_id'), 'user': 'server', 'message': 'Conflict detected'}
                    })) 
        except json.JSONDecodeError:
            print(f"Invalid JSON received from {websocket.remote_address}")
        except Exception as e:
            print(f"Error processing message from {websocket.remote_address}: {e}")

    async def broadcast(self, message, exclude=None):
        """Broadcast a message to all connected clients except the excluded one.

        Args:
            message (dict): The message to broadcast.
            exclude: The WebSocket connection to exclude from the broadcast.
        """
        if not self.clients:
            return

        message_str = json.dumps(message)
        tasks = []
        for client in self.clients:
            if client != exclude and client.open:
                tasks.append(client.send(message_str))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def check_for_conflict(self, payload):
        """Check if an update causes a conflict (simplified logic).

        Args:
            payload (dict): The update payload to check for conflicts.

        Returns:
            bool: True if a conflict is detected, False otherwise.
        """
        # Simplified conflict detection logic
        # In a real system, this would check timestamps, versions, or edit history
        return False

    async def start(self):
        """Start the WebSocket server."""
        print(f"Starting collaboration server on {self.host}:{self.port}...")
        self.server = await websockets.serve(
            self.handle_connection,
            self.host,
            self.port
        )
        print(f"Collaboration server started on ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            print("Collaboration server stopped.")

if __name__ == "__main__":
    server = CollaborationServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        server.stop()
        print("Server terminated by user.")
