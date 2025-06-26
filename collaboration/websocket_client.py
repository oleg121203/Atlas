"""
WebSocket Client for Real-Time Collaboration in Atlas (ASC-032)
This module implements a WebSocket client to receive real-time task updates in the Atlas app.
"""

import asyncio
import json
import websockets
import threading
import time
import logging

from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class WebSocketClient:
    """WebSocket client for receiving real-time updates in Atlas."""

    def __init__(self, server_url: str, team_id: str, on_message_callback: Callable[[Dict[str, Any]], None]):
        self.server_url = f"{server_url}/{team_id}"
        self.team_id = team_id
        self.on_message_callback = on_message_callback
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.connected = False
        self.received_messages = []
        logger.info(f"WebSocketClient initialized for team {team_id}")

    async def connect(self, max_attempts=5):
        """
        Connect to the WebSocket server.
        
        Args:
            max_attempts (int): Maximum number of connection attempts before giving up.
        """
        attempt = 0
        while attempt < max_attempts:
            try:
                self.ws = await websockets.connect(self.server_url)
                logger.info(f"Connected to WebSocket server at {self.server_url}")
                self.connected = True
                # Start background tasks for receiving messages and handling reconnection
                asyncio.create_task(self.receive_messages())
                asyncio.create_task(self.handle_reconnection())
                return
            except Exception as e:
                attempt += 1
                logger.error(f"Connection attempt {attempt}/{max_attempts} failed: {e}")
                if attempt == max_attempts:
                    logger.error(f"Failed to connect to WebSocket server after {max_attempts} attempts")
                    raise
                await asyncio.sleep(2 * attempt)  # Exponential backoff

    def is_connected(self):
        """Check if client is connected."""
        return self.connected

    async def receive_messages(self):
        """Receive messages from the WebSocket server."""
        while self.connected:
            try:
                message = await self.ws.recv()
                try:
                    data = json.loads(message)
                    self.received_messages.append(data)
                    self.on_message_callback(data)
                except json.JSONDecodeError:
                    print(f"Error decoding message: {message}")
            except websockets.ConnectionClosed:
                self.connected = False
                logger.error("WebSocket connection closed unexpectedly")
                await self.handle_reconnection()

    async def handle_reconnection(self):
        """Handle reconnection to the WebSocket server."""
        while True:
            await asyncio.sleep(2)  # Wait before attempting to reconnect
            try:
                await self.connect()
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {e}")

    async def send_message(self, message):
        """Send a message through the WebSocket connection."""
        if not self.ws or self.ws.closed:
            logger.error("Cannot send message: WebSocket is not connected")
            return False
        try:
            await self.ws.send(message)
            logger.debug(f"Sent message: {message}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def send_message_sync(self, message):
        """Synchronous wrapper for sending messages."""
        def send_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.send_message(message))
            except Exception as e:
                logger.error(f"Error in sync send: {e}")
            finally:
                loop.close()
        threading.Thread(target=send_async, daemon=True).start()

    def start(self):
        """
        Start the WebSocket client connection.
        Use a separate thread to run asyncio operations to avoid event loop conflicts.
        """
        if self.running:
            return
        self.running = True
        def run_async_connect():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.connect())
            except Exception as e:
                logger.error(f"Error in async connect: {e}")
            finally:
                loop.close()
        threading.Thread(target=run_async_connect, daemon=True).start()

    def stop(self):
        """Stop the WebSocket client connection."""
        self.running = False
        if self.ws:
            def close_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.ws.close())
                except Exception as e:
                    logger.error(f"Error closing WebSocket: {e}")
                finally:
                    loop.close()
            threading.Thread(target=close_async, daemon=True).start()

# Example usage in Atlas app
def example_callback(data: Dict[str, Any]):
    """Example callback to process incoming WebSocket messages."""
    print(f"Received update: {data}")
    # Update UI or task data based on the message

if __name__ == "__main__":
    client = WebSocketClient("ws://localhost:8765", "test_team", example_callback)
    client.start()
    asyncio.run(asyncio.sleep(60))  # Keep running for testing
    client.stop()
