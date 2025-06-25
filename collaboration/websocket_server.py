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

import os

# Redis connection for Pub/Sub messaging
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

# Store connected clients by team ID
connected_clients: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}

async def subscribe_to_team(team_id: str, websocket: websockets.WebSocketServerProtocol):
    """Subscribe a WebSocket connection to a specific team's channel."""
    if team_id not in connected_clients:
        connected_clients[team_id] = set()
    connected_clients[team_id].add(websocket)
    print(f"Client subscribed to team {team_id}")
    # Send confirmation of connection
    await websocket.send(json.dumps({"status": "connected", "team_id": team_id}))
    try:
        # Subscribe to Redis pubsub channel for this team
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"team:{team_id}")
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = message['data'].decode()
                for client in connected_clients[team_id]:
                    try:
                        await client.send(data)
                    except websockets.ConnectionClosed:
                        connected_clients[team_id].remove(client)
    except websockets.ConnectionClosed:
        connected_clients[team_id].remove(websocket)
    finally:
        if team_id in connected_clients and websocket in connected_clients[team_id]:
            connected_clients[team_id].remove(websocket)
        await pubsub.unsubscribe(f"team:{team_id}")

async def handle_connection(websocket: websockets.WebSocketServerProtocol, path: str):
    """Handle incoming WebSocket connections and route based on path."""
    print(f"New connection: {path}")
    match = re.match(r"/team/([^/]+)", path)
    if match:
        team_id = match.group(1)
        await subscribe_to_team(team_id, websocket)
    else:
        print(f"Invalid path: {path}")
        await websocket.close(code=1000, reason="Invalid path")

async def start_server(port=8765):
    """Start the WebSocket server for real-time collaboration on a specified port."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("localhost", port))
        s.close()
    except OSError:
        print(f"Port {port} is already in use, trying next port...")
        return await start_server(port + 1)
    
    server = await websockets.serve(
        lambda ws, path: handle_connection(ws, path),
        "localhost",
        port,
        ping_interval=20,
        ping_timeout=60
    )
    print(f"WebSocket server started on ws://localhost:{port}")
    return server, port

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    server, used_port = loop.run_until_complete(start_server())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(server.close())
        loop.close()
