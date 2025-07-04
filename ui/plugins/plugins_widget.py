"""
Plugins widget for the Atlas application.

This module provides the UI component for plugin management, including
input validation and sanitization for plugin-related inputs.
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.logging import get_logger
from ui.input_validation import sanitize_ui_input, validate_ui_input

logger = get_logger("PluginsWidget")


class PluginsWidget(QWidget):
    """Plugin management interface widget for Atlas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        logger.info("Plugins widget initialized")

    def init_ui(self) -> None:
        """Initialize UI components for the plugins widget."""
        layout = QVBoxLayout(self)

        # Plugin list
        self.plugin_list = QListWidget()
        layout.addWidget(self.plugin_list)

        # Input area for plugin search or commands
        input_layout = QHBoxLayout()
        self.plugin_input = QLineEdit()
        self.plugin_input.setPlaceholderText("Search plugins or enter command...")
        self.plugin_input.returnPressed.connect(self.process_input)
        input_layout.addWidget(self.plugin_input)

        process_button = QPushButton("Process")
        process_button.clicked.connect(self.process_input)
        input_layout.addWidget(process_button)

        layout.addLayout(input_layout)

    def process_input(self) -> None:
        """Handle processing plugin input with validation and sanitization."""
        input_text = self.plugin_input.text().strip()
        if not input_text:
            return

        # Validate input
        is_valid, error_msg = validate_ui_input(input_text, "text", "Plugin Input")
        if not is_valid:
            logger.warning("Invalid plugin input: %s", error_msg)
            # Display error to user (could be improved with a proper error display mechanism)
            self.plugin_input.setPlaceholderText(error_msg)
            return

        # Sanitize input
        sanitized_input = sanitize_ui_input(input_text)
        logger.debug(
            "Plugin input sanitized, original: %s, sanitized: %s",
            input_text,
            sanitized_input,
        )

        # Add the sanitized input to the list (for demonstration)
        item = QListWidgetItem(f"Search/Command: {sanitized_input}")
        self.plugin_list.addItem(item)
        self.plugin_input.clear()

        # TODO: Implement actual plugin search or command processing logic
        logger.info("Plugin input processed: %s", sanitized_input)

    def remove_plugin(self, item: QListWidgetItem) -> None:
        """
        Remove a plugin or command from the list.

        Args:
            item: QListWidgetItem to remove
        """
        self.plugin_list.takeItem(self.plugin_list.row(item))
        logger.info("Plugin item removed")
