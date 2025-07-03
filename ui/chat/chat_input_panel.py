"""
Chat input panel with message entry, send button, and voice input.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QMenu,
    QPushButton,
    QWidget,
)

from core.events import CHAT_MESSAGE_SENT
from ui.module_communication import EVENT_BUS, publish_module_event


class ChatInputPanel(QWidget):
    """PySide6 implementation of chat input panel."""

    # Signal emitted when a message is sent
    message_sent = Signal(str)

    def __init__(self, parent=None, on_send_callback=None):
        """Initialize the chat input panel.

        Args:
            parent: Parent widget
            on_send_callback: Callback function for when messages are sent
        """
        super().__init__(parent)
        self.on_send_callback = on_send_callback
        self.event_bus = EVENT_BUS
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        self.setLayout(layout)

        # Voice input button
        self.voice_button = QPushButton("🎤")
        self.voice_button.setFixedSize(35, 35)
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: black;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #b0b0b0;
            }
        """)
        self.voice_button.clicked.connect(self._on_voice_input)
        layout.addWidget(self.voice_button)

        # Message entry field
        self.message_entry = QLineEdit()
        self.message_entry.setPlaceholderText("Type your message here...")
        self.message_entry.setFont(QApplication.font())
        self.message_entry.returnPressed.connect(self._on_send_message)
        layout.addWidget(self.message_entry, 1)  # Give it stretch factor

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(50, 35)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #00A0E0;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077b6;
            }
            QPushButton:pressed {
                background-color: #005577;
            }
        """)
        self.send_button.clicked.connect(self._on_send_message)
        layout.addWidget(self.send_button)

        # Setup context menu
        self.setup_context_menu()

    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Enter sends message (already connected via returnPressed)
        # Note: Shift+Enter and Ctrl+Enter would need QTextEdit for multiline support
        pass

    def setup_context_menu(self):
        """Set up context menu for the message entry."""
        self.message_entry.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.message_entry.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, position):
        """Show context menu at the given position.

        Args:
            position: Position where to show the menu
        """
        menu = QMenu(self)

        # Standard edit actions
        cut_action = menu.addAction("Cut")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.message_entry.cut)
        cut_action.setEnabled(self.message_entry.hasSelectedText())

        copy_action = menu.addAction("Copy")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.message_entry.copy)
        copy_action.setEnabled(self.message_entry.hasSelectedText())

        paste_action = menu.addAction("Paste")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.message_entry.paste)

        menu.addSeparator()

        select_all_action = menu.addAction("Select All")
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.message_entry.selectAll)
        select_all_action.setEnabled(len(self.message_entry.text()) > 0)

        # Show menu at the cursor position
        global_pos = self.message_entry.mapToGlobal(position)
        menu.exec(global_pos)

    def _on_send_message(self):
        """Handle send button click or Enter key press."""
        text = self.message_entry.text().strip()
        if text:
            # Emit signal
            self.message_sent.emit(text)

            # Publish event on the global event bus
            publish_module_event(CHAT_MESSAGE_SENT, {"text": text, "sender": "user"})

            # Call callback if provided
            if self.on_send_callback is not None:
                self.on_send_callback(text)

            # Clear the input field
            self.message_entry.clear()

    def _on_voice_input(self):
        """Handle voice input button click."""
        # TODO: Integrate with voice assistant
        # For now, just show a placeholder message
        self.message_entry.setPlaceholderText("Voice input not implemented yet...")

    def get_text(self):
        """Get the current text in the input field.

        Returns:
            str: Current text in the input field
        """
        return self.message_entry.text()

    def set_text(self, text):
        """Set the text in the input field.

        Args:
            text: Text to set
        """
        self.message_entry.setText(text)

    def clear(self):
        """Clear the input field."""
        self.message_entry.clear()

    def focus_input(self):
        """Set focus to the input field."""
        self.message_entry.setFocus()
