"""
Missing UI modules that need to be created or fixed.

This file contains placeholder implementations for missing UI components
that are referenced in main_window.py but don't exist or have issues.
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class PlaceholderWidget(QWidget):
    """A placeholder widget for missing modules."""

    def __init__(self, module_name: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.module_name = module_name
        self.setup_ui()

    def setup_ui(self):
        """Set up the placeholder UI."""
        layout = QVBoxLayout(self)

        title = QLabel(f"📋 {self.module_name}")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #ffaa00;
                padding: 20px;
                text-align: center;
                border: 2px dashed #ffaa00;
                border-radius: 8px;
                margin: 20px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        description = QLabel(
            f"The {self.module_name} module is not yet implemented.\n\n"
            "This is a placeholder that will be replaced with the actual module."
        )
        description.setStyleSheet("""
            QLabel {
                color: #ccc;
                font-size: 14px;
                padding: 15px;
                text-align: center;
                line-height: 1.5;
            }
        """)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)

        layout.addStretch()


# Export for use in main_window.py
__all__ = ["PlaceholderWidget"]
