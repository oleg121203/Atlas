"""Example Chat Plugin for Atlas.

This plugin demonstrates how to create a chat extension plugin
that adds new functionality to the Atlas chat module.
"""

import logging
from typing import Any, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from plugins import PluginBase

logger = logging.getLogger(__name__)


class ExampleChatPlugin(PluginBase):
    """Example chat extension plugin for Atlas.

    This plugin adds a simple text formatting tool to the chat module.
    """

    def __init__(self):
        """Initialize the example chat plugin."""
        super().__init__(name="Example Chat Plugin", version="1.0.0")
        self._widget = None
        logger.info("Example Chat Plugin initialized")

    def initialize(self) -> bool:
        """Initialize the plugin.

        Returns:
            True if initialization was successful
        """
        logger.info("Example Chat Plugin initializing...")
        return True

    def start(self) -> bool:
        """Start the plugin.

        Returns:
            True if start was successful
        """
        logger.info("Example Chat Plugin starting...")
        return super().start()

    def stop(self) -> bool:
        """Stop the plugin.

        Returns:
            True if stop was successful
        """
        logger.info("Example Chat Plugin stopping...")
        return super().stop()

    def get_widget(self) -> QWidget:
        """Get the plugin's UI widget.

        Returns:
            QWidget for the plugin UI
        """
        if not self._widget:
            self._widget = ExampleChatWidget()
        return self._widget


class ExampleChatWidget(QWidget):
    """Widget for the Example Chat Plugin.

    This widget provides text formatting options for the chat.
    """

    text_formatted = Signal(str)

    def __init__(self):
        """Initialize the chat plugin widget."""
        super().__init__()
        self.setObjectName("ExampleChatWidget")

        # Setup UI
        self.layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("Text Formatter")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)

        # Text input
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter text to format...")
        self.text_edit.setMaximumHeight(100)
        self.layout.addWidget(self.text_edit)

        # Format buttons
        self.bold_button = QPushButton("Bold")
        self.italic_button = QPushButton("Italic")
        self.code_button = QPushButton("Code")

        self.layout.addWidget(self.bold_button)
        self.layout.addWidget(self.italic_button)
        self.layout.addWidget(self.code_button)

        # Apply button
        self.apply_button = QPushButton("Apply to Chat")
        self.layout.addWidget(self.apply_button)

        # Setup signals
        self.bold_button.clicked.connect(self.format_bold)
        self.italic_button.clicked.connect(self.format_italic)
        self.code_button.clicked.connect(self.format_code)
        self.apply_button.clicked.connect(self.apply_formatting)

        # Add stretcher
        self.layout.addStretch()

    def format_bold(self):
        """Format selected text as bold."""
        text = self.text_edit.toPlainText()
        self.text_edit.setPlainText(f"**{text}**")

    def format_italic(self):
        """Format selected text as italic."""
        text = self.text_edit.toPlainText()
        self.text_edit.setPlainText(f"*{text}*")

    def format_code(self):
        """Format selected text as code."""
        text = self.text_edit.toPlainText()
        self.text_edit.setPlainText(f"`{text}`")

    def apply_formatting(self):
        """Apply formatting and emit the text_formatted signal."""
        formatted_text = self.text_edit.toPlainText()
        self.text_formatted.emit(formatted_text)
        logger.debug(f"Formatted text applied: {formatted_text}")


# Plugin instance for the plugin system
plugin = ExampleChatPlugin
