"""
Unit Tests for WebSocket Collaboration in Atlas (ASC-032)
This module tests the WebSocket server and client functionality for real-time task updates.
"""

import unittest
import asyncio
import json
import websockets
import websocket

from threading import Thread
import time

import sys
import os

# Add the collaboration directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../collaboration"))

from websocket_server import start_server
from websocket_client import WebSocketClient

class TestWebSocketCollaboration(unittest.TestCase):
    """Test suite for WebSocket-based real-time collaboration."""

    @classmethod
    def setUpClass(cls):
        """Set up WebSocket server for tests."""
        import socket
        cls.port = 8765
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("localhost", cls.port))
            s.close()
        except OSError:
            print(f"Port {cls.port} is already in use, trying next port...")
            cls.port += 1
            try:
                s.bind(("localhost", cls.port))
                s.close()
            except OSError:
                print(f"Port {cls.port} also in use, skipping server start for testing. Tests may fail if server is not running externally.")
                return
        cls.server_thread = Thread(target=cls.start_server_sync, args=(cls.port,), daemon=True)
        cls.server_thread.start()
        time.sleep(8)  # Increased wait time for server to fully start
        print(f"Test setup complete, server should be running on port {cls.port}")

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        # Server will stop when thread ends if it was started
        if hasattr(cls, 'server_thread') and cls.server_thread:
            # No direct way to stop asyncio server in thread, rely on daemon=True to terminate
            pass

    @classmethod
    def start_server_sync(cls, port):
        """Synchronous wrapper to start the WebSocket server."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        server, _ = loop.run_until_complete(start_server(port=port))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(server.close())
            loop.close()

    def setUp(self):
        """Set up test variables and client connections."""
        self.team_id = "test_team"
        self.received_messages = []
        def message_callback(message):
            self.received_messages.append(message)
        self.client = WebSocketClient(f"ws://localhost:{self.port}/team/{self.team_id}", self.team_id, message_callback)
        # Ensure an event loop is available for the client
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.client.start()
        # Allow time for connection
        loop.run_until_complete(asyncio.sleep(2))

    def tearDown(self):
        """Clean up client connection after each test."""
        self.client.stop()
        # Clean up the event loop
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.close()

    def test_connection_established(self):
        """Test that client can connect to the WebSocket server."""
        self.client = WebSocketClient(f"ws://localhost:{self.port}/team/test_team", "test_team", lambda msg: print(f"Received: {msg}"))
        self.client.start()
        time.sleep(8)  # Increased wait time to ensure client connects and processes initial messages
        self.assertTrue(self.client.running, "WebSocket client failed to connect to server")
        received = hasattr(self.client, "received_connection_confirmation") and self.client.received_connection_confirmation
        self.assertTrue(received, "Did not receive connection confirmation message")

    def test_message_broadcast(self):
        """Test that a message sent to a team is received by connected clients."""
        received_messages = []
        second_client_received = []
        
        def on_message(msg):
            print(f"First client received: {msg}")
            received_messages.append(msg)
        
        def on_message_second(msg):
            print(f"Second client received: {msg}")
            second_client_received.append(msg)
        
        self.client = WebSocketClient(f"ws://localhost:{self.port}/team/test_team", "test_team", on_message)
        self.client.start()
        time.sleep(8)  # Increased wait for first client to connect
        self.assertTrue(self.client.running, "First client failed to connect")
        
        second_client = WebSocketClient(f"ws://localhost:{self.port}/team/test_team", "test_team", on_message_second)
        second_client.start()
        time.sleep(8)  # Increased wait for second client to connect
        self.assertTrue(second_client.running, "Second client failed to connect")
        
        # Simulate sending a message through the server
        test_message = {"type": "task_update", "task_id": "123", "content": "Test update"}
        import redis
        redis_client = redis.Redis(host="localhost", port=6379, db=0)
        redis_client.publish(f"team:{self.team_id}", json.dumps(test_message))
        time.sleep(1)  # Give time for message to propagate
        self.assertGreaterEqual(len(received_messages), 1, "No broadcast message received")
        found_test_message = False
        for msg in received_messages:
            if msg.get("type") == "task_update" and msg.get("task_id") == "123":
                found_test_message = True
                break
        self.assertTrue(found_test_message, "Test broadcast message not received by clients")
        second_client.stop()

if __name__ == "__main__":
    unittest.main()
