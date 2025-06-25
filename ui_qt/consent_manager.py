"""Consent Manager Module for Atlas

This module provides a UI for users to manage their consent preferences
for various AI actions and data usage within the Atlas application.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import logging
from core.ethics.ethical_guidelines import EthicalGuidelines

logger = logging.getLogger(__name__)


class ConsentManager(QWidget):
    """A widget for managing user consent preferences for AI actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ethics = EthicalGuidelines()
        self.user_id = "default_user"  # Replace with actual user ID in a real application
        self.setWindowTitle("Consent Manager")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("AI Action Consent Preferences")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # Description
        desc = QLabel("Manage your consent for various AI actions. Your choices can be updated at any time.")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Consent options
        self.consent_options = {
            "data_collection": QCheckBox("Allow data collection for AI training and improvement"),
            "task_execution": QCheckBox("Allow AI to execute tasks on my behalf"),
            "personalized_learning": QCheckBox("Allow personalized learning based on my interactions"),
            "ai_task_management": QCheckBox("Enable AI-Driven Task Management")
        }

        for action_type, checkbox in self.consent_options.items():
            checkbox.stateChanged.connect(lambda state, at=action_type: self.update_consent(at, state == Qt.Checked))
            layout.addWidget(checkbox)

        # Load current consent settings
        self.load_consent_settings()

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Preferences")
        save_btn.clicked.connect(self.save_preferences)
        btn_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self.reset_to_default)
        btn_layout.addWidget(reset_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_consent_settings(self):
        """Load current consent settings from EthicalGuidelines."""
        for action_type, checkbox in self.consent_options.items():
            consent = self.ethics.check_consent(self.user_id, action_type)
            checkbox.setChecked(consent)

    def update_consent(self, action_type: str, consent: bool):
        """Update consent for a specific action type in EthicalGuidelines."""
        self.ethics.update_consent(self.user_id, action_type, consent)
        logger.info(f"Updated consent for {action_type} to {consent} for user {self.user_id}")

    def save_preferences(self):
        """Save the current consent preferences."""
        # Preferences are updated in real-time via update_consent, but this could trigger a persistent save if needed
        QMessageBox.information(self, "Consent Saved", "Your consent preferences have been saved.")
        logger.info(f"Consent preferences saved for user {self.user_id}")

    def reset_to_default(self):
        """Reset consent preferences to default (no consent)."""
        for action_type, checkbox in self.consent_options.items():
            checkbox.setChecked(False)
            self.ethics.update_consent(self.user_id, action_type, False)
        QMessageBox.information(self, "Consent Reset", "Your consent preferences have been reset to default.")
        logger.info(f"Consent preferences reset to default for user {self.user_id}")
