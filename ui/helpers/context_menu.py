"""Context Menu component for Atlas."""

import logging
from typing import Callable, List, Optional, Tuple

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QAction, QMenu, QWidget  # type: ignore


class ContextMenu(QMenu):
    """Custom context menu for Atlas with cyberpunk styling."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setStyleSheet("""
            QMenu {
                background-color: #0a0a0a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
            }
            QMenu::item {
                background-color: transparent;
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        self.logger.info("ContextMenu component initialized")

    def add_action(self, text: str, callback: Callable[[], None]) -> QAction:
        """Add an action to the context menu.

        Args:
            text (str): The text to display for the action.
            callback (Callable[[], None]): The function to call when the action is triggered.

        Returns:
            QAction: The created action.
        """
        action = QAction(text, self)
        action.triggered.connect(callback)
        self.addAction(action)
        self.logger.debug(f"Added action to context menu: {text}")
        return action

    def show_at(
        self, pos: QPoint, actions: List[Tuple[str, Callable[[], None]]]
    ) -> None:
        """Show the context menu at the specified position with the given actions.

        Args:
            pos (QPoint): The position to show the context menu.
            actions (List[Tuple[str, Callable[[], None]]]): List of (text, callback) pairs for menu actions.
        """
        self.clear()
        for text, callback in actions:
            self.add_action(text, callback)
        self.exec(pos)
        self.logger.debug(f"Showing context menu at position {pos}")
