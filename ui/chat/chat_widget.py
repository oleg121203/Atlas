"""
Chat widget for the Atlas application.

This module provides the UI component for chat functionality, including
message input with validation and sanitization.
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.events import CONTEXT_UPDATED
from core.logging import get_logger
from ui.input_validation import sanitize_ui_input, validate_ui_input

logger = get_logger("ChatWidget")


class ChatWidget(QWidget):
    """Chat interface widget for Atlas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.event_bus.subscribe(CONTEXT_UPDATED, self._on_context_updated)
        logger.info("Chat widget initialized")

    def init_ui(self) -> None:
        """Initialize UI components for the chat widget."""
        layout = QVBoxLayout(self)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)

        layout.addLayout(input_layout)

    def send_message(self) -> None:
        """Handle sending a message with validation and sanitization."""
        message = self.message_input.text().strip()
        if not message:
            return

        # Validate input
        is_valid, error_msg = validate_ui_input(message, "text", "Message")
        if not is_valid:
            logger.warning("Invalid message input: %s", error_msg)
            self.chat_display.append(f"Error: {error_msg}")
            return

        # Sanitize input
        sanitized_message = sanitize_ui_input(message)
        logger.debug(
            "Message sanitized, original: %s, sanitized: %s", message, sanitized_message
        )

        # Display the sanitized message
        self.chat_display.append(f"You: {sanitized_message}")
        self.message_input.clear()

        # TODO: Implement actual message sending logic
        logger.info("Message sent: %s", sanitized_message)

    def receive_message(self, message: str) -> None:
        """
        Display a received message.

        Args:
            message: Message text to display
        """
        sanitized_message = sanitize_ui_input(message)
        self.chat_display.append(f"Other: {sanitized_message}")
        logger.info("Message received: %s", sanitized_message)

    def _on_context_updated(self, data):
        self.refresh_context()
