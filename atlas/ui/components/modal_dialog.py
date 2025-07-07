"""Modal Dialog Module for Atlas UI (ASC-024)

This module defines a custom modal dialog for the Atlas application as part of the UI enhancements under ASC-024. The modal is used for task creation and other input forms, following the design specifications in ui_design_specifications.md.
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Setup logging
logger = logging.getLogger(__name__)


class ModalDialog(QDialog):
    """A custom modal dialog for input forms like task creation."""

    def __init__(self, title="New Task", parent=None):
        super().__init__(parent)
        self.setObjectName("modal")
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)
        self.setup_ui(title)
        logger.info(f"ModalDialog initialized with title: {title}")

    def setup_ui(self, title):
        """Setup the UI elements for the modal dialog.

        Args:
            title (str): The title of the modal dialog.
        """
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Header with title and close button
        self.header = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setObjectName("modalTitle")
        self.header.addWidget(self.title_label)
        self.header.addStretch()
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("closeModal")
        self.close_btn.clicked.connect(self.reject)
        self.header.addWidget(self.close_btn)
        self.layout.addLayout(self.header)

        # Form fields placeholder (basic fields for task creation)
        self.fields_layout = QVBoxLayout()

        # Title field
        self.title_input_layout = QVBoxLayout()
        self.title_label_field = QLabel("Title")
        self.title_label_field.setObjectName("modalLabel")
        self.title_input_layout.addWidget(self.title_label_field)
        self.title_input = QLineEdit()
        self.title_input.setObjectName("modalInput")
        self.title_input_layout.addWidget(self.title_input)
        self.fields_layout.addLayout(self.title_input_layout)

        # Priority field
        self.priority_input_layout = QVBoxLayout()
        self.priority_label = QLabel("Priority")
        self.priority_label.setObjectName("modalLabel")
        self.priority_input_layout.addWidget(self.priority_label)
        self.priority_input = QComboBox()
        self.priority_input.setObjectName("modalInput")
        self.priority_input.addItems(["Low", "Medium", "High"])
        self.priority_input_layout.addWidget(self.priority_input)
        self.fields_layout.addLayout(self.priority_input_layout)

        # Due Date field (placeholder, actual date picker to be implemented)
        self.due_date_input_layout = QVBoxLayout()
        self.due_date_label = QLabel("Due Date")
        self.due_date_label.setObjectName("modalLabel")
        self.due_date_input_layout.addWidget(self.due_date_label)
        self.due_date_input = QLineEdit()
        self.due_date_input.setObjectName("modalInput")
        self.due_date_input.setPlaceholderText("YYYY-MM-DD")
        self.due_date_input_layout.addWidget(self.due_date_input)
        self.fields_layout.addLayout(self.due_date_input_layout)

        # AI Suggestion placeholder
        self.ai_suggestion = QLabel("Suggested due date: 2025-07-01")
        self.ai_suggestion.setObjectName("aiSuggestion")
        self.fields_layout.addWidget(self.ai_suggestion)

        # Advanced Options Button
        self.advanced_btn = QPushButton("Show Advanced Options")
        self.advanced_btn.setObjectName("advancedOptions")
        self.advanced_btn.clicked.connect(self.toggle_advanced_options)
        self.fields_layout.addWidget(self.advanced_btn)

        # Advanced fields (hidden by default)
        self.advanced_fields = QWidget()
        self.advanced_fields_layout = QVBoxLayout()
        self.advanced_fields.setLayout(self.advanced_fields_layout)
        self.advanced_fields.setVisible(False)

        # Description field (advanced)
        self.desc_input_layout = QVBoxLayout()
        self.desc_label = QLabel("Description")
        self.desc_label.setObjectName("modalLabel")
        self.desc_input_layout.addWidget(self.desc_label)
        self.desc_input = QTextEdit()
        self.desc_input.setObjectName("modalInput")
        self.desc_input.setFixedHeight(100)
        self.desc_input_layout.addWidget(self.desc_input)
        self.advanced_fields_layout.addLayout(self.desc_input_layout)

        self.fields_layout.addWidget(self.advanced_fields)
        self.layout.addLayout(self.fields_layout)

        # Footer with buttons
        self.footer = QHBoxLayout()
        self.footer.addStretch()
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("modalSave")
        self.save_btn.clicked.connect(self.accept)
        self.footer.addWidget(self.save_btn)

        self.save_new_btn = QPushButton("Save & New")
        self.save_new_btn.setObjectName("modalSaveNew")
        self.save_new_btn.clicked.connect(self.save_and_new)
        self.footer.addWidget(self.save_new_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("modalCancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.footer.addWidget(self.cancel_btn)
        self.layout.addLayout(self.footer)

        # Set fixed width as per design specs
        self.setFixedWidth(600)
        logger.info("ModalDialog UI setup completed")
        # TODO: Implement animations for open/close as per specs

    def toggle_advanced_options(self):
        """Toggle visibility of advanced options fields."""
        is_visible = not self.advanced_fields.isVisible()
        self.advanced_fields.setVisible(is_visible)
        self.advanced_btn.setText(
            "Hide Advanced Options" if is_visible else "Show Advanced Options"
        )
        # TODO: Add animation for expanding/collapsing
        logger.info(
            f"Advanced options toggled: {'visible' if is_visible else 'hidden'}"
        )

    def save_and_new(self):
        """Save the current input and reset the form for a new entry without closing."""
        logger.info("Save & New clicked")
        # TODO: Implement save logic and form reset
        self.accept()  # Temporarily just accept, to be updated with actual logic

    def get_data(self):
        """Retrieve the data entered in the form.

        Returns:
            dict: The data from the form fields.
        """
        data = {
            "title": self.title_input.text(),
            "priority": self.priority_input.currentText(),
            "due_date": self.due_date_input.text(),
            "description": self.desc_input.toPlainText()
            if self.advanced_fields.isVisible()
            else "",
        }
        logger.info(f"Modal data retrieved: {data}")
        return data
