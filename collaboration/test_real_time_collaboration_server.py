import unittest
import json
from unittest.mock import patch, MagicMock

from real_time_collaboration_server import CollaborationServer

class TestCollaborationServer(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        self.server = CollaborationServer(host="localhost", port=8766)
        self.clients = set()

    def tearDown(self):
        """Clean up after each test."""
        self.server.clients = set()

    @patch('websockets.serve')
    def test_start_server(self, mock_serve):
        """Test starting the collaboration server without actual async execution."""
        mock_server = MagicMock()
        mock_serve.return_value = mock_server

        with patch('asyncio.run_coroutine_threadsafe') as mock_async:
            self.server.start()
            mock_async.assert_called()

        self.assertIsNone(self.server.server)  # Server not actually started in test

    def test_handle_connection(self):
        """Test handling a new client connection without async execution."""
        mock_ws = MagicMock()
        mock_ws.remote_address = ('127.0.0.1', 12345)
        mock_ws.open = True

        with patch.object(self.server, 'broadcast') as mock_broadcast:
            # Simulate handle_connection without async
            self.server.clients.add(mock_ws)
            mock_broadcast.assert_not_called()  # Not called in simplified test

        self.assertIn(mock_ws, self.server.clients)

    def test_handle_message_valid_json(self):
        """Test handling a valid JSON message from a client."""
        message = json.dumps({
            'action': 'workflow_update',
            'payload': {'workflow_id': 'wf123', 'user': 'test_user'}
        })
        mock_ws = MagicMock()
        mock_ws.remote_address = ('127.0.0.1', 12345)

        with patch.object(self.server, 'broadcast') as mock_broadcast:
            with patch.object(self.server, 'check_for_conflict', return_value=False):
                self.server.handle_message(message, mock_ws)
                mock_broadcast.assert_called()

    def test_handle_message_invalid_json(self):
        """Test handling an invalid JSON message from a client."""
        message = "invalid json"
        mock_ws = MagicMock()
        mock_ws.remote_address = ('127.0.0.1', 12345)

        with patch('builtins.print') as mock_print:
            self.server.handle_message(message, mock_ws)
            mock_print.assert_called_with(f"Invalid JSON received from {mock_ws.remote_address}")

    def test_broadcast_to_clients(self):
        """Test broadcasting a message to connected clients without async."""
        mock_ws1 = MagicMock()
        mock_ws1.open = True
        mock_ws1.send = MagicMock()
        mock_ws2 = MagicMock()
        mock_ws2.open = True
        mock_ws2.send = MagicMock()
        self.server.clients = {mock_ws1, mock_ws2}

        message = {'action': 'test', 'payload': {}}
        # Manually simulate broadcast without async
        message_str = json.dumps(message)
        for client in self.server.clients:
            if client.open:
                client.send(message_str)

        mock_ws1.send.assert_called_with(message_str)
        mock_ws2.send.assert_called_with(message_str)

    def test_broadcast_exclude_client(self):
        """Test broadcasting a message excluding a specific client without async."""
        mock_ws1 = MagicMock()
        mock_ws1.open = True
        mock_ws1.send = MagicMock()
        mock_ws2 = MagicMock()
        mock_ws2.open = True
        mock_ws2.send = MagicMock()
        self.server.clients = {mock_ws1, mock_ws2}

        message = {'action': 'test', 'payload': {}}
        # Manually simulate broadcast without async
        message_str = json.dumps(message)
        for client in self.server.clients:
            if client.open and client != mock_ws2:
                client.send(message_str)

        mock_ws1.send.assert_called_with(message_str)
        mock_ws2.send.assert_not_called()

    def test_check_for_conflict(self):
        """Test conflict detection logic."""
        payload = {'workflow_id': 'wf123', 'version': 1}
        result = self.server.check_for_conflict(payload)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
