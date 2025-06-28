"""Theme Switcher component for Atlas."""

import logging
from typing import List, Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QVBoxLayout, QWidget


class ThemeSwitcher(QWidget):
    """UI component for switching between themes in Atlas with cyberpunk styling."""

    theme_selected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                color: #00ffaa;
            }
            QComboBox {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 2px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #00ffaa;
                border-left-style: solid;
            }
            QComboBox::down-arrow {
                image: url(noimg);
                width: 8px;
                height: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                selection-background-color: #00ffaa;
                selection-color: #000000;
            }
            QPushButton {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        self.initialize_ui()
        self.logger.info("ThemeSwitcher component initialized")

    def initialize_ui(self) -> None:
        """Initialize the UI components for the theme switcher."""
        layout = QVBoxLayout(self)

        header_label = QLabel("Theme Switcher")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ffaa;")
        layout.addWidget(header_label)

        self.theme_dropdown = QComboBox()
        self.theme_dropdown.currentTextChanged.connect(self.on_theme_selected)
        layout.addWidget(self.theme_dropdown)

        self.apply_button = QPushButton("Apply Theme")
        self.apply_button.clicked.connect(self.on_apply_theme)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def update_theme_list(self, theme_ids: List[str]) -> None:
        """Update the list of available themes in the dropdown.

        Args:
            theme_ids (List[str]): List of theme identifiers.
        """
        self.theme_dropdown.clear()
        self.theme_dropdown.addItems(theme_ids)
        self.logger.info(f"Updated theme list with {len(theme_ids)} themes")

    def set_current_theme(self, theme_id: str) -> None:
        """Set the currently selected theme in the dropdown.

        Args:
            theme_id (str): The ID of the theme to set as current.
        """
        index = self.theme_dropdown.findText(theme_id)
        if index >= 0:
            self.theme_dropdown.setCurrentIndex(index)
            self.logger.debug(f"Set current theme to: {theme_id}")
        else:
            self.logger.warning(f"Theme not found in dropdown: {theme_id}")

    @Slot(str)
    def on_theme_selected(self, theme_id: str) -> None:
        """Handle theme selection change in the dropdown.

        Args:
            theme_id (str): The selected theme ID.
        """
        self.logger.info(f"Theme selected: {theme_id}")

    @Slot()
    def on_apply_theme(self) -> None:
        """Handle apply theme button click."""
        selected_theme = self.theme_dropdown.currentText()
        if selected_theme:
            self.theme_selected.emit(selected_theme)
            self.logger.info(f"Applying theme: {selected_theme}")
        else:
            self.logger.warning("No theme selected to apply")
