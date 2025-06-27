"""
View for managing tools
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget


class ToolManagementView(QWidget):
    """PySide6 implementation of ToolManagementView."""

    def __init__(self, parent=None):
        """Initialize the widget."""
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        # TODO: Implement PySide6 version of the UI
