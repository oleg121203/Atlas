"""
Test module for WebSocket latency and conflict resolution in Atlas real-time collaboration.
"""
import unittest
import asyncio
import time
import json
from threading import Thread
from websocket import create_connection, WebSocket

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
        cls.server_thread = Thread(target=cls.server.start, daemon=True)
        cls.server_thread.start()
        time.sleep(1)  # Give server time to start
        cls.logger.info("Test server started")
    
    @classmethod
    def tearDownClass(cls):
        """Shut down WebSocket server."""
        cls.server.stop()
        cls.server_thread.join(timeout=2)
        cls.logger.info("Test server stopped")
    
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
        """Create and connect a WebSocket client."""
        client = WebSocketClient(f'ws://localhost:8765/team/default_team/user/{user_id}')
        client.start()
        self.clients.append(client)
        time.sleep(0.5)  # Give client time to connect
        return client
    
    def test_latency(self):
        """Test message delivery latency between clients."""
        user1 = self.create_client('user1')
        user2 = self.create_client('user2')
        
        start_time = time.time()
        task_data = {'type': 'task_update', 'data': {'id': 'task1', 'status': 'updated'}}
        user1.send_message(json.dumps(task_data))
        
        received = False
        for _ in range(10):  # Wait up to 1 second
            if user2.received_messages:
                end_time = time.time()
                latency = end_time - start_time
                self.logger.info(f"Message received with latency: {latency*1000:.2f}ms")
                self.assertLess(latency, 0.1, "Latency should be less than 100ms")
                received = True
                break
            time.sleep(0.1)
        
        self.assertTrue(received, "Message should be received by second client")
    
    def test_conflict_resolution_timestamp(self):
        """Test conflict resolution based on timestamp."""
        user1 = self.create_client('user3')
        user2 = self.create_client('user4')
        
        # Simulate updates to same task with different timestamps
        task1_update1 = {'type': 'task_update', 'data': {'id': 'task2', 'status': 'update1', 'timestamp': time.time() - 1}}
        task1_update2 = {'type': 'task_update', 'data': {'id': 'task2', 'status': 'update2', 'timestamp': time.time()}}
        
        user1.send_message(json.dumps(task1_update1))
        user2.send_message(json.dumps(task1_update2))
        
        time.sleep(0.5)  # Wait for messages to propagate
        
        # Check which update was applied (should be update2 with later timestamp)
        final_update = None
        for client in self.clients:
            if client.received_messages:
                last_msg = json.loads(client.received_messages[-1])
                if last_msg['data']['id'] == 'task2':
                    final_update = last_msg['data']['status']
                    break
        
        self.assertEqual(final_update, 'update2', "Later timestamp update should take precedence")
    
    def test_conflict_resolution_multiple_updates(self):
        """Test conflict resolution with multiple rapid updates."""
        user1 = self.create_client('user5')
        user2 = self.create_client('user6')
        
        # Send rapid conflicting updates
        for i in range(5):
            update1 = {'type': 'task_update', 'data': {'id': 'task3', 'status': f'update1_{i}', 'timestamp': time.time()}}
            update2 = {'type': 'task_update', 'data': {'id': 'task3', 'status': f'update2_{i}', 'timestamp': time.time() + 0.001}}
            user1.send_message(json.dumps(update1))
            user2.send_message(json.dumps(update2))
            time.sleep(0.05)
        
        time.sleep(1)  # Wait for all messages to process
        
        final_update = None
        for client in self.clients:
            if client.received_messages:
                last_msg = json.loads(client.received_messages[-1])
                if last_msg['data']['id'] == 'task3':
                    final_update = last_msg['data']['status']
                    break
        
        self.assertTrue(final_update.startswith('update2'), "Later updates should take precedence")

if __name__ == '__main__':
    unittest.main()
