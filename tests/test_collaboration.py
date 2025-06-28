"""
Tests for the CollaborationManager class in integration/websocket_integration.py
"""

from unittest.mock import MagicMock, patch

import pytest

from integration.websocket_integration import CollaborationManager


# Mock WebSocketClient for testing
class MockWebSocketClient:
    def __init__(self, server_url, team_id, callback):
        self.server_url = server_url
        self.team_id = team_id
        self.callback = callback
        self.connected = False

    def start(self):
        self.connected = True
        return True

    def stop(self):
        self.connected = False
        return True

    def is_connected(self):
        return self.connected

    # Method to simulate receiving a message
    def simulate_message(self, message):
        if self.callback:
            self.callback(message)


@pytest.fixture
def mock_websocket_client():
    """Create a patch for WebSocketClient."""
    with patch(
        "integration.websocket_integration.WebSocketClient", MockWebSocketClient
    ) as mock_client:
        yield mock_client


@pytest.fixture
def collab_manager(mock_websocket_client):
    """Create a CollaborationManager instance with mocked WebSocketClient."""
    return CollaborationManager("ws://test-server.com", "test-user", "test-team")


def test_initialization(collab_manager):
    """Test that the collaboration manager initializes correctly."""
    assert collab_manager.user_id == "test-user"
    assert collab_manager.team_id == "test-team"
    assert collab_manager.server_url == "ws://test-server.com"
    assert collab_manager.task_update_callback is None


def test_set_task_update_callback(collab_manager):
    """Test setting the task update callback."""
    callback = MagicMock()
    collab_manager.set_task_update_callback(callback)
    assert collab_manager.task_update_callback == callback


def test_start_and_stop(collab_manager):
    """Test starting and stopping the WebSocket client."""
    # Start
    collab_manager.start()
    assert collab_manager.client.connected is True

    # Stop
    collab_manager.stop()
    assert collab_manager.client.connected is False


def test_handle_update_task_update(collab_manager):
    """Test handling a task update message."""
    # Setup a mock callback
    mock_callback = MagicMock()
    collab_manager.set_task_update_callback(mock_callback)

    # Create a test message
    task_data = {"id": "task-123", "title": "Test Task", "completed": False}
    message = {"type": "task_update", "data": task_data}

    # Trigger the message handler
    collab_manager.handle_update(message)

    # Check that callback was called with correct data
    mock_callback.assert_called_once_with(task_data)


def test_handle_update_unknown_type(collab_manager):
    """Test handling a message with unknown type."""
    # Setup a mock callback
    mock_callback = MagicMock()
    collab_manager.set_task_update_callback(mock_callback)

    # Create a test message with unknown type
    message = {"type": "unknown_type", "data": {"some": "data"}}

    # Trigger the message handler
    collab_manager.handle_update(message)

    # Check that callback was not called
    mock_callback.assert_not_called()


def test_handle_update_exception(collab_manager):
    """Test handling an exception during update processing."""

    # Setup a callback that raises an exception
    def failing_callback(data):
        raise ValueError("Test exception")

    collab_manager.set_task_update_callback(failing_callback)

    # Create a test message
    message = {"type": "task_update", "data": {"id": "task-123"}}

    # Trigger the message handler (should not raise exception)
    collab_manager.handle_update(message)

    # If we get here without exception, the test passes
    assert True


def test_send_task_update(collab_manager):
    """Test sending a task update."""
    # Mock the handle_update method to check if it's called
    original_handle_update = collab_manager.handle_update
    collab_manager.handle_update = MagicMock()

    # Send a task update
    task_data = {"id": "task-123", "title": "Updated Task"}
    collab_manager.send_task_update(task_data)

    # Check that handle_update was called with correct data
    expected_message = {"type": "task_update", "data": task_data}
    collab_manager.handle_update.assert_called_once_with(expected_message)

    # Restore original method
    collab_manager.handle_update = original_handle_update
