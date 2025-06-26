import unittest
import json
from unittest.mock import patch, MagicMock

from real_time_collaboration import RealTimeCollaboration

class TestRealTimeCollaboration(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        self.collab = RealTimeCollaboration(server_uri="ws://testserver:8765")
        # Do not start event loop or thread to avoid async issues

    def tearDown(self):
        """Clean up after each test."""
        self.collab.connected = False
        self.collab.websocket = None

    @patch('websockets.connect')
    def test_connect_initialization(self, mock_connect):
        """Test initialization and connection attempt without actual async execution."""
        mock_ws = MagicMock()
        mock_connect.return_value = mock_ws
        
        # Just test that connect method can be called without error
        # and that it sets up the connection attempt correctly
        with patch('asyncio.run_coroutine_threadsafe') as mock_async:
            self.collab.start()
            mock_async.assert_called()

        self.assertFalse(self.collab.connected)  # Connection not completed in test

    def test_handle_message_workflow_update(self):
        """Test handling of workflow update messages."""
        message = json.dumps({
            'action': 'workflow_update',
            'payload': {'user': 'test_user', 'workflow_id': 'wf123'}
        })
        with patch.object(self.collab, 'on_workflow_update') as mock_update:
            self.collab.handle_message(message)
            mock_update.assert_called_with({'user': 'test_user', 'workflow_id': 'wf123'})

    def test_send_update_success(self):
        """Test sending an update successfully without actual async execution."""
        self.collab.connected = True
        self.collab.websocket = MagicMock()
        # Mock the send method as a regular MagicMock since we don't need to await it in test
        self.collab.websocket.send = MagicMock(return_value=None)
        # Call send_update and verify the json payload that would be sent
        action = 'test_action'
        payload = {'data': 'test'}
        expected_payload = json.dumps({'action': action, 'payload': payload})
        self.collab.send_update(action, payload)
        self.collab.websocket.send.assert_called_once_with(expected_payload)

if __name__ == '__main__':
    unittest.main()
