"""
Main chat panel that combines chat history and input components.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ChatPanel(QWidget):
    """PySide6 implementation of the main chat panel."""

    def __init__(self, parent=None, chat_history_view=None, chat_input_panel=None):
        """Initialize the chat panel.

        Args:
            parent: Parent widget
            chat_history_view: Widget for displaying chat history
            chat_input_panel: Widget for chat input (will be created if None)
        """
        super().__init__(parent)
        self.chat_history_view = chat_history_view
        self.chat_input_panel = chat_input_panel
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Add chat history view if provided
        if self.chat_history_view is not None:
            layout.addWidget(
                self.chat_history_view, 1
            )  # Give it stretch factor of 1        # Add or create chat input panel
        if self.chat_input_panel is None:
            # Import here to avoid circular imports
            from ui.chat_input_panel import ChatInputPanel

            self.chat_input_panel = ChatInputPanel(self, self._on_send_message)

        if self.chat_input_panel is not None:
            layout.addWidget(self.chat_input_panel)

    def create_simple_input_panel(self):
        """Create a simple input panel with text field and send button."""
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(5, 5, 5, 5)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your message here...")

        send_button = QPushButton("Send")
        send_button.setFixedWidth(80)

        input_layout.addWidget(self.text_input)
        input_layout.addWidget(send_button)

        # Connect signals
        send_button.clicked.connect(self._send_message)
        self.text_input.returnPressed.connect(self._send_message)

        self.chat_input_panel = input_widget

    def _send_message(self):
        """Send the message from the input field."""
        if hasattr(self, "text_input"):
            text = self.text_input.text().strip()
            if text:
                self._on_send_message(text)
                self.text_input.clear()

    def _on_send_message(self, text):
        """Handle message sending from input panel.

        Args:
            text: The message text to send
        """
        # Add user message to chat history
        if self.chat_history_view is not None and hasattr(
            self.chat_history_view, "add_message"
        ):
            self.chat_history_view.add_message("user", text)

    def set_chat_history_view(self, chat_history_view):
        """Set the chat history view widget.

        Args:
            chat_history_view: Widget for displaying chat history
        """
        layout = self.layout()
        if layout is not None and self.chat_history_view is not None:
            layout.removeWidget(self.chat_history_view)
            self.chat_history_view.setParent(None)

        self.chat_history_view = chat_history_view
        if layout is not None and chat_history_view is not None:
            # Just rebuild the layout when changing components
            self.setup_ui()

    def set_chat_input_panel(self, chat_input_panel):
        """Set the chat input panel widget.

        Args:
            chat_input_panel: Widget for chat input
        """
        layout = self.layout()
        if layout is not None and self.chat_input_panel is not None:
            layout.removeWidget(self.chat_input_panel)
            self.chat_input_panel.setParent(None)

        self.chat_input_panel = chat_input_panel
        if layout is not None and chat_input_panel is not None:
            layout.addWidget(chat_input_panel)
