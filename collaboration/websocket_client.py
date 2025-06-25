"""
WebSocket Client for Real-Time Collaboration in Atlas (ASC-032)
This module implements a WebSocket client to receive real-time task updates in the Atlas app.
"""

import asyncio
import json
import websocket
import threading
import time

from typing import Dict, Any, Optional

class WebSocketClient:
    """WebSocket client for receiving real-time updates in Atlas."""

    def __init__(self, server_url: str, team_id: str, on_message_callback: callable):
        self.server_url = f"{server_url}/{team_id}"
        self.team_id = team_id
        self.on_message_callback = on_message_callback
        self.ws: Optional[websocket.WebSocketApp] = None
        self.running = False

    def on_open(self, ws: websocket.WebSocketApp):
        """Callback when WebSocket connection is opened."""
        print(f"Connected to WebSocket server for team {self.team_id}")
        # Small delay to ensure any initial messages are processed
        time.sleep(0.5)
        self.running = True

    def on_message(self, ws: websocket.WebSocketApp, message: str):
        """Callback when a message is received from the WebSocket server."""
        try:
            data = json.loads(message)
            self.on_message_callback(data)
        except json.JSONDecodeError:
            print(f"Error decoding message: {message}")

    def on_error(self, ws: websocket.WebSocketApp, error: Exception):
        """Callback when an error occurs in WebSocket connection."""
        print(f"WebSocket error: {error}")
        self.running = False
        threading.Thread(target=self.delayed_reconnect, daemon=True).start()

    def on_close(self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str):
        """Callback when WebSocket connection is closed."""
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.running = False
        threading.Thread(target=self.delayed_reconnect, daemon=True).start()

    def delayed_reconnect(self):
        """Handle reconnection with a delay in a separate thread."""
        if not self.running:
            print("Attempting to reconnect to WebSocket server...")
            time.sleep(5)  # Wait before retrying
            self.start()

    def start(self):
        """Start the WebSocket client connection."""
        if self.ws and self.running:
            return
        self.ws = websocket.WebSocketApp(
            self.server_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        # Run WebSocket in a separate thread to avoid blocking
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def stop(self):
        """Stop the WebSocket client connection."""
        self.running = False
        if self.ws:
            self.ws.close()

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
