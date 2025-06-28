"""Tooltip component for Atlas."""

import logging
from typing import Optional

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QToolTip, QWidget


class Tooltip(QWidget):
    """Custom tooltip component for Atlas with cyberpunk styling."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setWindowFlag(Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        self.logger.info("Tooltip component initialized")

    def show_tooltip(self, text: str, widget: QWidget, pos: tuple[int, int]) -> None:
        """Display the tooltip with the specified text at the given position relative to the widget.

        Args:
            text (str): The text to display in the tooltip.
            widget (QWidget): The widget to associate the tooltip with.
            pos (tuple[int, int]): The (x, y) position relative to the widget where the tooltip should appear.
        """
        QToolTip.showText(widget.mapToGlobal(QPoint(pos[0], pos[1])), text, widget)
        self.logger.debug(f"Showing tooltip: {text} at position {pos}")
