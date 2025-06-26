"""
WebSocket Server for Real-Time Collaboration in Atlas (ASC-032)
This module implements a WebSocket server to enable real-time task updates for team collaboration.
"""

import asyncio
import json
import websockets
from typing import Dict, Set, Any
import redis
import re
import logging
import time
import threading

import os

# Redis connection for Pub/Sub messaging
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

# Store connected clients by team ID
connected_clients: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}

class WebSocketServer:
    def __init__(self, host: str = 'localhost', port: int = 8765):
        """Initialize WebSocket server with conflict resolution storage."""
        self.host = host
        self.port = port
        self.server = None
        self.clients = {}  # team_id -> {client_id -> websocket}
        self.task_timestamps = {}  # task_id -> latest_timestamp for conflict resolution
        self.task_history = {}  # client_id -> {task_id -> task_data}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def handle_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """
        Handle a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection object
            path: Connection path containing team and user info
        """
        try:
            # Extract team_id and user_id from path
            parts = path.strip('/').split('/')
            if len(parts) >= 4 and parts[0] == 'team' and parts[2] == 'user':
                team_id = parts[1]
                user_id = parts[3]
            else:
                team_id = 'default'
                user_id = 'unknown'
                self.logger.warning(f"Invalid path format: {path}, using default team")
            
            client_id = f"{team_id}:{user_id}"
            self.logger.info(f"New connection: {client_id}")
            
            # Register client
            if team_id not in self.clients:
                self.clients[team_id] = {}
            self.clients[team_id][client_id] = websocket
            
            # Send connection confirmation
            await websocket.send(json.dumps({
                'type': 'connection',
                'status': 'connected',
                'client_id': client_id,
                'team_id': team_id
            }))
            
            # Store for conflict resolution
            self.task_history[client_id] = {}
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    self.logger.debug(f"Received message from {client_id}: {data}")
                    
                    # Handle different message types
                    msg_type = data.get('type')
                    if msg_type == 'task_update':
                        task_data = data.get('data', {})
                        task_id = task_data.get('id')
                        timestamp = task_data.get('timestamp', time.time())
                        
                        # Conflict resolution based on timestamp
                        should_broadcast = True
                        if task_id in self.task_timestamps:
                            if timestamp <= self.task_timestamps[task_id]:
                                self.logger.info(f"Discarding outdated update for task {task_id} from {client_id}")
                                should_broadcast = False
                        
                        if should_broadcast:
                            self.task_timestamps[task_id] = timestamp
                            await self.broadcast_to_team(team_id, client_id, data)
                            self.task_history[client_id][task_id] = task_data
                    else:
                        # Broadcast other message types
                        await self.broadcast_to_team(team_id, client_id, data)
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON from {client_id}: {message}")
                except Exception as e:
                    self.logger.error(f"Error processing message from {client_id}: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(f"Connection error for {client_id}: {e}", exc_info=True)
        finally:
            if team_id in self.clients and client_id in self.clients[team_id]:
                del self.clients[team_id][client_id]
                if not self.clients[team_id]:
                    del self.clients[team_id]
                self.logger.info(f"Disconnected: {client_id}")

    async def broadcast_to_team(self, team_id: str, sender_id: str, message: dict):
        """
        Broadcast message to all team members except sender.
        
        Args:
            team_id: Team identifier
            sender_id: ID of sending client
            message: Message to broadcast
        """
        try:
            if team_id in self.clients:
                self.logger.debug(f"Broadcasting to team {team_id} from {sender_id}: {message}")
                for client_id, client_ws in list(self.clients[team_id].items()):
                    if client_id != sender_id:
                        try:
                            await client_ws.send(json.dumps(message))
                        except Exception as e:
                            self.logger.error(f"Error sending to {client_id}: {e}")
        except Exception as e:
            self.logger.error(f"Broadcast error for team {team_id}: {e}", exc_info=True)

            def start(self):
        """Synchronous method to start the WebSocket server for testing compatibility."""
        def run_server():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._server_task = self._loop.run_until_complete(self.start_server())
            try:
                self._loop.run_forever()
            except Exception as e:
                self.logger.error(f"Server loop error: {e}")

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        time.sleep(1)  # Give server time to start

            def stop(self):
        """Stop the WebSocket server."""
        if hasattr(self, '_loop') and self._loop and not self._loop.is_closed():
            if hasattr(self, 'server') and self.server:
                self._loop.call_soon_threadsafe(self.server.close)
            self._loop.call_soon_threadsafe(self._loop.stop)

    async def start_server(self):
        """Start the WebSocket server for real-time collaboration on a specified port."""
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("localhost", self.port))
            s.close()
        except OSError:
            print(f"Port {self.port} is already in use, trying next port...")
            self.port += 1
            return await self.start_server()
        
        self.server = await websockets.serve(
            self.handle_connection,
            "localhost",
            self.port,
            ping_interval=20,
            ping_timeout=60
        )
        print(f"WebSocket server started on ws://localhost:{self.port}")
        return self.server, self.port

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = WebSocketServer()
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    server_loop, used_port = loop.run_until_complete(server.start_server())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(server_loop.close())
        loop.close()
