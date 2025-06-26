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
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.client.start()
                # Allow time for connection
                loop.run_until_complete(asyncio.sleep(3))
                if self.client.running:
                    print(f"Client connected successfully on attempt {attempt + 1}")
                    break
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)  # Wait before retrying

    def tearDown(self):
        """Clean up client connection after each test."""
        self.client.stop()
        # Clean up the event loop
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.close()

    def test_connection_established(self):
        """Test that client can connect to the WebSocket server."""
        received_messages = []
        def message_callback(msg):
            print(f"Received: {msg}")
            received_messages.append(msg)
        self.client = WebSocketClient(f"ws://localhost:{self.port}/team/test_team", "test_team", message_callback)
        max_retries = 3
        connected = False
        for attempt in range(max_retries):
            try:
                self.client.start()
                time.sleep(10)  # Increased wait time for connection
                if self.client.running:
                    print(f"Connection established on attempt {attempt + 1}")
                    connected = True
                    break
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)  # Wait before retrying
        self.assertTrue(connected, "WebSocket client failed to connect to server after multiple attempts")
        received = False
        for msg in received_messages:
            if msg.get("status") == "connected" and msg.get("team_id") == "test_team":
                received = True
                break
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
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.client.start()
                time.sleep(10)  # Further increased wait for first client to connect
                if self.client.running:
                    print(f"First client connected on attempt {attempt + 1}")
                    break
            except Exception as e:
                print(f"First client connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
        self.assertTrue(self.client.running, "First client failed to connect after multiple attempts")
        
        second_client = WebSocketClient(f"ws://localhost:{self.port}/team/test_team", "test_team", on_message_second)
        for attempt in range(max_retries):
            try:
                second_client.start()
                time.sleep(10)  # Further increased wait for second client to connect
                if second_client.running:
                    print(f"Second client connected on attempt {attempt + 1}")
                    break
            except Exception as e:
                print(f"Second client connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
        self.assertTrue(second_client.running, "Second client failed to connect after multiple attempts")
        
        # Simulate sending a message through the server
        test_message = {"type": "task_update", "task_id": "123", "content": "Test update"}
        import redis
        try:
            redis_client = redis.Redis(host="localhost", port=6379, db=0)
            redis_client.publish(f"team:{self.team_id}", json.dumps(test_message))
            print("Published test message to Redis")
        except Exception as e:
            print(f"Error publishing to Redis: {e}")
            self.fail("Failed to publish test message to Redis")
        time.sleep(2)  # Increased time for message to propagate
        self.assertGreaterEqual(len(received_messages), 1, "No broadcast message received by first client")
        found_test_message = False
        for msg in received_messages:
            if msg.get("type") == "task_update" and msg.get("task_id") == "123":
                found_test_message = True
                break
        self.assertTrue(found_test_message, "Test broadcast message not received by first client")
        self.assertGreaterEqual(len(second_client_received), 1, "No broadcast message received by second client")
        found_test_message_second = False
        for msg in second_client_received:
            if msg.get("type") == "task_update" and msg.get("task_id") == "123":
                found_test_message_second = True
                break
        self.assertTrue(found_test_message_second, "Test broadcast message not received by second client")
        second_client.stop()

if __name__ == "__main__":
    unittest.main()
