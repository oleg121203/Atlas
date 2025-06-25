import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.chat_module import ChatModule
import logging

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def qapp():
    """Qt application fixture."""
    return QApplication([])

class TestChatModule:
    """Test cases for ChatModule UI components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.chat_module = ChatModule()
        
        # Mock dependencies
        self.mock_agent_manager = MagicMock()
        self.chat_module.agent_manager = self.mock_agent_manager
        
        # Initialize UI
        self.chat_module.init_ui()

    def test_message_sending(self, qapp):
        """Test sending messages."""
        # Enter message
        self.chat_module.input_field.setText("Test message")
        
        # Simulate Enter key press
        self.chat_module.input_field.keyPressEvent(
            MagicMock(key=Qt.Key.Key_Enter)
        )
        
        # Verify message was sent
        self.mock_agent_manager.send_message.assert_called_once_with(
            "Test message"
        )
        
        # Verify message appears in chat
        assert self.chat_module.chat_view.count() > 0
        last_message = self.chat_module.chat_view.item(self.chat_module.chat_view.count() - 1)
        assert "Test message" in last_message.text()

    def test_message_receiving(self, qapp):
        """Test receiving messages."""
        # Mock incoming message
        message = {
            "role": "assistant",
            "content": "Test response",
            "timestamp": "2025-06-25 02:22:42"
        }
        
        # Simulate message received
        self.chat_module.on_message_received(message)
        
        # Verify message appears in chat
        assert self.chat_module.chat_view.count() > 0
        last_message = self.chat_module.chat_view.item(self.chat_module.chat_view.count() - 1)
        assert "Test response" in last_message.text()

    def test_message_formatting(self, qapp):
        """Test message formatting with emojis and markdown."""
        # Test emoji
        emoji_message = "😊"
        self.chat_module.input_field.setText(emoji_message)
        self.chat_module.input_field.keyPressEvent(
            MagicMock(key=Qt.Key.Key_Enter)
        )
        
        # Verify emoji is displayed correctly
        last_message = self.chat_module.chat_view.item(self.chat_module.chat_view.count() - 1)
        assert emoji_message in last_message.text()
        
        # Test markdown
        markdown_message = "**bold** _italic_ [link](https://example.com)"
        self.chat_module.input_field.setText(markdown_message)
        self.chat_module.input_field.keyPressEvent(
            MagicMock(key=Qt.Key.Key_Enter)
        )
        
        # Verify markdown is rendered
        last_message = self.chat_module.chat_view.item(self.chat_module.chat_view.count() - 1)
        assert "bold" in last_message.text()
        assert "italic" in last_message.text()
        assert "example.com" in last_message.text()

    def test_message_history(self, qapp):
        """Test message history management."""
        # Send multiple messages
        for i in range(5):
            message = f"Test message {i}"
            self.chat_module.input_field.setText(message)
            self.chat_module.input_field.keyPressEvent(
                MagicMock(key=Qt.Key.Key_Enter)
            )
        
        # Verify history is maintained
        assert self.chat_module.chat_view.count() == 5
        
        # Test scrolling
        self.chat_module.chat_view.scrollToBottom()
        assert self.chat_module.chat_view.verticalScrollBar().value() == self.chat_module.chat_view.verticalScrollBar().maximum()

    def test_drag_and_drop(self, qapp):
        """Test drag and drop functionality."""
        # Mock drag event
        drag_event = MagicMock()
        drag_event.mimeData.return_value.text.return_value = "Dragged text"
        
        # Simulate drop event
        self.chat_module.chat_view.dropEvent(drag_event)
        
        # Verify text was added to chat
        last_message = self.chat_module.chat_view.item(self.chat_module.chat_view.count() - 1)
        assert "Dragged text" in last_message.text()

    def test_context_menu(self, qapp):
        """Test context menu functionality."""
        # Add message to test
        self.chat_module.input_field.setText("Test message")
        self.chat_module.input_field.keyPressEvent(
            MagicMock(key=Qt.Key.Key_Enter)
        )
        
        # Simulate right click
        pos = self.chat_module.chat_view.visualItemRect(
            self.chat_module.chat_view.item(0)
        ).center()
        context_event = MagicMock()
        context_event.pos.return_value = pos
        
        # Show context menu
        self.chat_module.chat_view.contextMenuEvent(context_event)
        
        # Verify menu items
        menu = self.chat_module.chat_view.findChild(QMenu)
        assert menu is not None
        actions = menu.actions()
        assert any(action.text() == "Copy" for action in actions)
        assert any(action.text() == "Delete" for action in actions)

    def test_search_functionality(self, qapp):
        """Test search functionality."""
        # Add messages to search
        for i in range(5):
            message = f"Test message {i}"
            self.chat_module.input_field.setText(message)
            self.chat_module.input_field.keyPressEvent(
                MagicMock(key=Qt.Key.Key_Enter)
            )
        
        # Search for message
        self.chat_module.search_field.setText("message 2")
        self.chat_module.on_search()
        
        # Verify search results
        visible_items = [
            i for i in range(self.chat_module.chat_view.count())
            if not self.chat_module.chat_view.item(i).isHidden()
        ]
        assert len(visible_items) == 1
        assert "message 2" in self.chat_module.chat_view.item(visible_items[0]).text()

    def test_theme_changes(self, qapp):
        """Test theme changes in chat module."""
        # Test dark theme
        self.chat_module.set_theme("dark")
        assert self.chat_module.chat_view.styleSheet().startswith("background-color: #1e1e1e")
        
        # Test light theme
        self.chat_module.set_theme("light")
        assert self.chat_module.chat_view.styleSheet().startswith("background-color: #ffffff")

    def test_error_handling(self, qapp):
        """Test error handling in chat module."""
        # Test sending empty message
        self.chat_module.input_field.setText("")
        self.chat_module.input_field.keyPressEvent(
            MagicMock(key=Qt.Key.Key_Enter)
        )
        
        # Verify error message
        assert self.chat_module.error_label.text() == "Message cannot be empty"
        
        # Test sending invalid message
        self.mock_agent_manager.send_message.side_effect = Exception("Test error")
        self.chat_module.input_field.setText("Invalid message")
        self.chat_module.input_field.keyPressEvent(
            MagicMock(key=Qt.Key.Key_Enter)
        )
        
        # Verify error message
        assert "Error sending message" in self.chat_module.error_label.text()
