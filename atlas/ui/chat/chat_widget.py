"""
Chat widget for the Atlas application.

This module provides the UI component for chat functionality, including
message input with validation and sanitization.
"""

import datetime
import os

from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from sentry_config import (
    capture_exception,
    capture_message,
    set_context,
    start_transaction,
)

from atlas.core.events import CHAT_MESSAGE_SENT, CONTEXT_UPDATED
from atlas.core.logging import get_logger
from atlas.ui.input_validation import sanitize_ui_input, validate_ui_input
from atlas.ui.module_communication import EVENT_BUS, publish_module_event

logger = get_logger("ChatWidget")


class ChatWidget(QWidget):
    """Chat interface widget for Atlas."""

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.event_bus = EVENT_BUS
        self.init_ui()

        # Enable drop events
        self.setAcceptDrops(True)

        # Set up event subscriptions
        self.event_bus.subscribe(CONTEXT_UPDATED, self._on_context_updated)
        self.event_bus.subscribe(CHAT_MESSAGE_SENT, self._on_chat_message)

        # Set context for Sentry to track widget initialization
        set_context("chat_widget", {"initialized": True, "parent": str(parent)})
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

        # Add Clear button
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_chat)
        input_layout.addWidget(clear_button)

        # Add Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_chat_history)
        input_layout.addWidget(save_button)

        layout.addLayout(input_layout)

    def send_message(self) -> None:
        """Handle sending a message with validation and sanitization."""
        # Start a performance transaction for monitoring
        transaction = start_transaction(name="chat.send_message", op="ui.action")
        try:
            message = self.message_input.text().strip()
            if not message:
                if transaction:
                    transaction.finish()
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
                "Message sanitized, original: %s, sanitized: %s",
                message,
                sanitized_message,
            )

            # Display the sanitized message with formatting
            formatted_message = self._format_message(sanitized_message, "You")
            self.chat_display.append(formatted_message)
            self.message_input.clear()

            # Publish event so other components (e.g. AI reply handler) can react
            publish_module_event(
                CHAT_MESSAGE_SENT, {"text": sanitized_message, "sender": "user"}
            )

            logger.info("Message sent: %s", sanitized_message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.chat_display.append("Error: Failed to send message. Please try again.")
            # Add context and report to Sentry
            set_context(
                "chat_widget",
                {
                    "action": "send_message",
                    "message_length": len(message) if "message" in locals() else 0,
                },
            )
            capture_exception(e, extra_data={"context": "Failed to send message"})
        finally:
            # Always finish the transaction
            if transaction:
                transaction.finish()

    def receive_message(self, message: str) -> None:
        """
        Display a received message.

        Args:
            message: Message text to display
        """
        # Start a performance transaction for monitoring
        transaction = start_transaction(name="chat.receive_message", op="ui.action")
        try:
            try:
                sanitized_message = sanitize_ui_input(message)
                self.chat_display.append(f"Other: {sanitized_message}")
                logger.info("Message received: %s", sanitized_message)
            except Exception as e:
                error_msg = f"Error receiving message: {str(e)}"
                logger.error(error_msg)
                self.chat_display.append(
                    "Error: An unexpected error occurred while displaying a message"
                )
                capture_exception(e, {"message": message})
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            self.chat_display.append("Error: Failed to display incoming message.")
            # Add context and report to Sentry
            set_context(
                "chat_widget",
                {
                    "action": "receive_message",
                    "message_length": len(message) if message else 0,
                },
            )
            capture_exception(
                e, extra_data={"context": "Failed to process incoming message"}
            )
        finally:
            # Always finish the transaction
            if transaction:
                transaction.finish()

    def _on_chat_message(self, data):
        """Handle incoming chat message events from other components."""
        try:
            sender = data.get("sender", "other")
            if sender == "user":
                # Already displayed locally
                return

            text = data.get("text", "")
            if not text:
                return

            # Check for special message types
            msg_type = data.get("type", "standard")

            if msg_type == "system":
                self.system_message(text)
            else:
                # For regular messages, use the sender name provided or default
                sender_name = data.get("sender_name", sender.capitalize())
                self.receive_message(text, sender_name)

        except Exception as e:
            logger.error(f"Error processing chat message event: {e}")
            # Add context and report to Sentry
            set_context(
                "chat_widget", {"action": "_on_chat_message", "data": str(data)}
            )
            capture_exception(
                e, extra_data={"context": "Failed to add message to chat log"}
            )

    def refresh_context(self):
        """Refresh context information displayed in the chat widget."""
        try:
            # Get the current context from the application or relevant service
            current_context = (
                self.app.get_current_context()
                if hasattr(self.app, "get_current_context")
                else {}
            )

            # If there's context information available, display it
            if current_context:
                context_summary = f"Current context: {len(current_context)} items"
                logger.debug(f"Refreshing chat context: {context_summary}")

                # You could display a context summary at the top of the chat
                # or update a status bar with context information
                # For now, we'll just log it
            else:
                logger.debug("No context available to refresh")

        except Exception as e:
            logger.error(f"Error refreshing context: {e}")
            # Add context and report to Sentry
            set_context("chat_widget", {"action": "refresh_context"})
            capture_exception(e)

    def _on_context_updated(self, data):
        """Handle context update events."""
        try:
            logger.debug(f"Context updated event received with data: {data}")
            try:
                self.refresh_context()
                capture_message(
                    "Context updated successfully",
                    level="info",
                    extra_data={"context": "User action"},
                )
            except Exception as e:
                error_msg = f"Error handling context update: {str(e)}"
                logger.error(error_msg)
                capture_exception(e, {"data": str(data)})
            # Update status to show context was refreshed
            self.update_status("Context Updated", "#00ff00")  # Green for success
        except Exception as e:
            logger.error(f"Error handling context update: {e}")
            # Add context and report to Sentry
            set_context(
                "chat_widget", {"action": "_on_context_updated", "data": str(data)}
            )
            capture_exception(
                e, extra_data={"context": "Failed to update UI after message added"}
            )
            # Update status to show error
            self.update_status("Context Update Failed", "#ff0000")  # Red for error

    def update_status(self, message: str, color: str = "#00ff00"):
        """Update the status indicator with a message and color.

        Args:
            message: Status message to display
            color: CSS color string (default green)
        """
        try:
            self.status_label.setText(message)
            self.status_label.setStyleSheet(
                f"background-color: #2a2a2a; color: {color}; border: none;"
            )

            # Reset status after 3 seconds if it's not an error message
            if color != "#ff0000":
                # Use QTimer to reset the status after a delay
                from PySide6.QtCore import QTimer

                QTimer.singleShot(
                    3000, lambda: self.status_label.setText("System Ready")
                )
                QTimer.singleShot(
                    3000,
                    lambda: self.status_label.setStyleSheet(
                        "background-color: #2a2a2a; color: #00ff00; border: none;"
                    ),
                )
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            set_context("chat_widget", {"action": "update_status", "message": message})
            capture_exception(
                e, extra_data={"context": "Failed to update status - agent online"}
            )

    def clear_chat(self) -> None:
        """Clear the chat display area."""
        try:
            self.chat_display.clear()
            logger.info("Chat history cleared")
            # Display a system message indicating the chat was cleared
            self.system_message("Chat history has been cleared")
            capture_message(
                "Chat log cleared", level="info", extra_data={"context": "User action"}
            )
        except Exception as e:
            logger.error(f"Error clearing chat: {e}")
            # Add context and report to Sentry
            set_context("chat_widget", {"action": "clear_chat"})
            capture_exception(e, extra_data={"context": "Failed to clear chat log"})

    def system_message(self, message: str) -> None:
        """Display a system message in the chat.

        Args:
            message: The system message to display
        """
        try:
            # System messages should be visually distinct
            self.chat_display.append(
                f"<i><span style='color: #888888;'>System: {message}</span></i>"
            )
            logger.debug("System message displayed: %s", message)
        except Exception as e:
            logger.error(f"Error displaying system message: {e}")
            # Add context and report to Sentry
            set_context("chat_widget", {"action": "system_message", "message": message})
            capture_exception(e)

    def save_chat_history(self) -> bool:
        """Save the current chat history to a file.

        Returns:
            bool: True if saved successfully, False otherwise
        """
        # Start a performance transaction for monitoring
        transaction = start_transaction(name="chat.save_history", op="file.write")
        try:
            # Create logs directory if it doesn't exist
            logs_dir = os.path.join(os.path.expanduser("~"), ".atlas", "chat_logs")
            os.makedirs(logs_dir, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(logs_dir, f"chat_history_{timestamp}.txt")

            # Save chat content
            with open(filename, "w", encoding="utf-8") as f:
                # Get plain text content (strip HTML)
                chat_content = self.chat_display.toPlainText()
                f.write(chat_content)

            self.system_message(f"Chat history saved to: {filename}")
            logger.info(f"Chat history saved to file: {filename}")
            return True

        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            self.system_message("Failed to save chat history")
            # Add context and report to Sentry
            set_context("chat_widget", {"action": "save_chat_history"})
            capture_exception(e)
            return False
        finally:
            # Always finish the transaction
            if transaction:
                transaction.finish()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events for files."""
        try:
            # Only accept file drops
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
        except Exception as e:
            logger.error(f"Error in drag enter event: {e}")
            set_context("chat_widget", {"action": "dragEnterEvent"})
            capture_exception(e)

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events for files."""
        try:
            transaction = start_transaction(name="chat.file_drop", op="ui.action")
            urls = event.mimeData().urls()

            if not urls:
                return

            # Process the first file only for now
            file_path = urls[0].toLocalFile()

            if not os.path.exists(file_path):
                self.system_message(f"Error: File not found: {file_path}")
                return

            # Check file size - don't process huge files
            if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB limit
                self.system_message("Error: File too large (>10MB)")
                return

            # Check file extension for basic security (can be expanded)
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in [".txt", ".md", ".csv", ".json"]:
                self.system_message(f"Error: Unsupported file type: {ext}")
                return

            # Send a system message about the file drop
            self.system_message(f"File received: {os.path.basename(file_path)}")

            # You could send an event here for other components to process the file
            # For now, just include the filename in the message input
            current_text = self.message_input.text()
            if current_text:
                self.message_input.setText(
                    f"{current_text} [file: {os.path.basename(file_path)}]"
                )
            else:
                self.message_input.setText(f"[file: {os.path.basename(file_path)}]")

            logger.info(f"File dropped in chat: {file_path}")

        except Exception as e:
            logger.error(f"Error processing dropped file: {e}")
            self.system_message("Error processing the dropped file")
            set_context("chat_widget", {"action": "dropEvent"})
            capture_exception(
                e, extra_data={"context": "Failed to update status - agent offline"}
            )
        finally:
            if transaction:
                transaction.finish()
