"""
Settings widget for the Atlas application.

This module provides the UI component for settings management, including
input validation and sanitization for settings inputs.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QComboBox, QLabel
from PySide6.QtCore import Qt

from ui.input_validation import validate_ui_input, sanitize_ui_input, validate_form_data, sanitize_form_data
from core.logging import get_logger

logger = get_logger("SettingsWidget")

class SettingsWidget(QWidget):
    """Settings management interface widget for Atlas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        logger.info("Settings widget initialized")
    
    def init_ui(self) -> None:
        """Initialize UI components for the settings widget."""
        layout = QVBoxLayout(self)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Language:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Ukrainian", "Russian", "English"])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)
        
        # API key input
        api_layout = QHBoxLayout()
        api_label = QLabel("API Key:")
        self.api_input = QLineEdit()
        self.api_input.setEchoMode(QLineEdit.Password)
        self.api_input.setPlaceholderText("Enter API key...")
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        layout.addLayout(api_layout)
        
        # Save button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
    
    def save_settings(self) -> None:
        """Handle saving settings with validation and sanitization."""
        # Prepare form data for validation
        form_data = {
            "API Key": (self.api_input.text(), "password")
        }
        
        # Validate form data
        is_valid, errors = validate_form_data(form_data)
        if not is_valid:
            logger.warning("Invalid settings input: %s", errors)
            # Display errors to user (could be improved with a proper error display mechanism)
            self.api_input.setPlaceholderText(errors.get("API Key", "Invalid input"))
            return
        
        # Sanitize form data
        sanitized_data = sanitize_form_data(form_data)
        sanitized_api_key = sanitized_data["API Key"]
        logger.debug("API key sanitized, original length: %d, sanitized length: %d", 
                     len(self.api_input.text()), len(sanitized_api_key))
        
        # TODO: Implement actual settings saving logic
        # For now, just log the action
        theme = self.theme_combo.currentText()
        language = self.lang_combo.currentText()
        logger.info("Settings saved - Theme: %s, Language: %s, API Key: [REDACTED]", theme, language)
        
        # Clear input after saving (for security)
        self.api_input.clear()
        self.api_input.setPlaceholderText("Settings saved")
