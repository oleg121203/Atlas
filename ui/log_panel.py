"""
Panel for displaying log messages.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class LogPanel(QWidget):
    """PySide6 implementation of log panel."""

    def __init__(self, parent=None):
        """Initialize the log panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Log text area
        self.log_textbox = QTextEdit()
        self.log_textbox.setFont(QFont("monospace", 12))
        self.log_textbox.setReadOnly(True)
        layout.addWidget(self.log_textbox)

        # Button frame
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(5)

        # Copy button
        copy_btn = QPushButton("Copy All")
        copy_btn.clicked.connect(self.copy_all)
        btn_layout.addWidget(copy_btn)

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear)
        btn_layout.addWidget(clear_btn)

        # Add stretch to push buttons to the left
        btn_layout.addStretch()

        layout.addWidget(btn_frame)

    def add_log(self, text):
        """Add a log message to the text area.

        Args:
            text: The log message to add
        """
        cursor = self.log_textbox.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_textbox.setTextCursor(cursor)
        self.log_textbox.insertPlainText(text + "\n")
        self.log_textbox.ensureCursorVisible()

    def clear(self):
        """Clear all log messages."""
        self.log_textbox.clear()

    def copy_all(self):
        """Copy all log messages to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_textbox.toPlainText())

    def get_logs(self):
        """Get all log messages.

        Returns:
            str: All log messages
        """
        return self.log_textbox.toPlainText()

    def set_font(self, font_name=None, font_size=None):
        """Set the font for the log text area.

        Args:
            font_name: Name of the font
            font_size: Size of the font
        """
        font = self.log_textbox.font()
        if font_name is not None:
            font.setFamily(font_name)
        if font_size is not None:
            font.setPointSize(font_size)
        self.log_textbox.setFont(font)
