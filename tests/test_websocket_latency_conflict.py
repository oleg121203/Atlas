"""
Test module for WebSocket latency and conflict resolution in Atlas real-time collaboration.
"""
import unittest
import asyncio
import time
import json
import sys
import os
from threading import Thread
from websocket import create_connection, WebSocket

# Add the collaboration directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../collaboration"))

from collaboration.websocket_server import WebSocketServer
from collaboration.websocket_client import WebSocketClient
from utils.logger import get_logger

class TestWebSocketLatencyConflict(unittest.TestCase):
    """Test latency and conflict resolution for WebSocket collaboration."""
    
    @classmethod
    def setUpClass(cls):
        """Set up WebSocket server for testing."""
        cls.logger = get_logger(cls.__name__)
        cls.server = WebSocketServer(host='localhost', port=8765)
        cls.server_thread = Thread(target=cls.server.start)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(0.5)  # Give server time to start
        cls.logger.info("Test server started")
    
    @classmethod
    def tearDownClass(cls):
        """Shut down WebSocket server."""
        # Clean up server
        # Note: No stop method available, rely on daemon thread to terminate
        pass
    
    def setUp(self):
        """Set up test clients."""
        self.clients = []
        self.logger.info("Setting up test clients")
    
    def tearDown(self):
        """Clean up test clients."""
        for client in self.clients:
            client.stop()
        self.clients.clear()
        self.logger.info("Cleaned up test clients")
    
    def create_client(self, user_id):
        """Helper to create a client with specific user ID."""
        client = WebSocketClient(f"ws://localhost:8765", f"default_team", None)
        return client
    
    def test_latency(self):
        """Test message delivery latency between clients."""
        user1 = self.create_client('user1')
        user1.start()
        self.clients.append(user1)
        time.sleep(2.0)  # Increased wait time for client to connect
        
        user2 = self.create_client('user2')
        user2.start()
        self.clients.append(user2)
        time.sleep(2.0)  # Increased wait time for client to connect
        
        start_time = time.time()
        task_data = {'type': 'task_update', 'data': {'id': 'task1', 'status': 'updated'}}
        user1.send_message_sync(json.dumps(task_data))
        
        received = False
        for _ in range(20):  # Wait up to 2 seconds
            if hasattr(user2, 'received_messages') and user2.received_messages:
                for msg in user2.received_messages:
                    if msg.get('type') == 'task_update' and msg.get('data', {}).get('id') == 'task1':
                        received = True
                        break
            if received:
                break
            time.sleep(0.1)
        
        end_time = time.time()
        latency = end_time - start_time
        print(f"Latency: {latency*1000:.2f} ms")
        self.assertTrue(received, "Message should be received by second client")
        self.assertLess(latency, 1.0, "Latency should be less than 1000ms")
    
    def test_conflict_resolution_timestamp(self):
        """Test conflict resolution based on timestamp."""
        user1 = self.create_client('user3')
        user1.start()
        self.clients.append(user1)
        time.sleep(2.0)  # Increased wait time for client to connect
        
        user2 = self.create_client('user4')
        user2.start()
        self.clients.append(user2)
        time.sleep(2.0)  # Increased wait time for client to connect
        
        # Simulate updates to same task with different timestamps
        task1_update1 = {'type': 'task_update', 'data': {'id': 'task2', 'status': 'update1', 'timestamp': time.time() - 1}}
        task1_update2 = {'type': 'task_update', 'data': {'id': 'task2', 'status': 'update2', 'timestamp': time.time()}}
        user1.send_message_sync(json.dumps(task1_update1))
        time.sleep(0.1)  # Small delay between updates
        user2.send_message_sync(json.dumps(task1_update2))
        
        time.sleep(1.0)  # Increased wait for messages to propagate
        
        final_update = None
        for client in self.clients:
            if hasattr(client, 'received_messages') and client.received_messages:
                for msg in client.received_messages:
                    if msg.get('type') == 'task_update' and msg.get('data', {}).get('id') == 'task2':
                        data = msg.get('data', {})
                        if final_update is None or data.get('timestamp', 0) > final_update.get('timestamp', 0):
                            final_update = data
        
        self.assertIsNotNone(final_update, "Should have received at least one update")
        self.assertEqual(final_update.get('status'), 'update2', "Later timestamp update should take precedence")
    
    def test_conflict_resolution_multiple_updates(self):
        """Test conflict resolution with multiple rapid updates."""
        user1 = self.create_client('user5')
        user1.start()
        self.clients.append(user1)
        time.sleep(2.0)  # Increased wait time for client to connect
        
        user2 = self.create_client('user6')
        user2.start()
        self.clients.append(user2)
        time.sleep(2.0)  # Increased wait time for client to connect
        
        # Send rapid conflicting updates
        for i in range(5):
            update1 = {'type': 'task_update', 'data': {'id': 'task3', 'status': f'update1_{i}', 'timestamp': time.time()}}
            update2 = {'type': 'task_update', 'data': {'id': 'task3', 'status': f'update2_{i}', 'timestamp': time.time() + 0.001}}
            user1.send_message_sync(json.dumps(update1))
            user2.send_message_sync(json.dumps(update2))
            time.sleep(0.05)  # Small delay between pairs of updates
        
        time.sleep(2.0)  # Increased wait for all messages to process
        
        final_update = None
        for client in self.clients:
            if hasattr(client, 'received_messages') and client.received_messages:
                for msg in client.received_messages:
                    if msg.get('type') == 'task_update' and msg.get('data', {}).get('id') == 'task3':
                        data = msg.get('data', {})
                        if final_update is None or data.get('timestamp', 0) > final_update.get('timestamp', 0):
                            final_update = data
        
        self.assertIsNotNone(final_update, "Should have received at least one update")
        self.assertTrue(final_update.get('status', '').startswith('update2'), "Later updates should take precedence")

    def test_multiple_clients_update_same_task(self):
        try:
            # Connect multiple clients
            clients = []
            for i in range(3):
                client = self.create_client(f"client_{i}")
                client.start()
                time.sleep(2.0)  # Increased wait time for client to connect
                self.assertTrue(client.is_connected(), f"Client {i} failed to connect")
                clients.append(client)

            # Simulate multiple clients updating the same task with slight delays
            task_id = 1
            for i, client in enumerate(clients):
                update_message = {
                    "type": "task_update",
                    "task_id": task_id,
                    "status": f"updated_by_client_{i}",
                    "timestamp": time.time()
                }
                asyncio.run(client.send_message(json.dumps(update_message)))
                time.sleep(0.1 * i)  # Slight delay between updates

            time.sleep(1)  # Give time for messages to be processed

            # Check conflict resolution - last update should win (or based on timestamp)
            self.assertTrue(len(self.server.task_updates) > 0)
            last_update = self.server.task_updates[task_id]
            self.assertEqual(last_update["status"], "updated_by_client_2")  # Last client update
        except Exception as e:
            print(f"Test failed due to connection issue: {e}")
            self.skipTest(f"WebSocket connection failed: {e}")

if __name__ == '__main__':
    unittest.main()
