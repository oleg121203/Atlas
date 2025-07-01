"""
Configuration UI Widget for Atlas

This module provides a UI widget for editing application configuration settings.
"""

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class ConfigWidget(QWidget):
    """Widget for editing application configuration settings."""

    def __init__(self, config_manager, parent: Optional[QWidget] = None):
        """Initialize the configuration widget.

        Args:
            config_manager: The configuration manager instance.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Configuration Settings")
        self.resize(600, 400)
        self._setup_ui()
        self._load_config()
        logger.info("Configuration widget initialized")

    def _setup_ui(self):
        """Set up the user interface components."""
        self.layout = QVBoxLayout(self)

        # Application Settings
        app_group = QWidget()
        app_layout = QVBoxLayout(app_group)
        app_layout.addWidget(QLabel("Application Settings", self))

        # App Name
        app_name_layout = QHBoxLayout()
        self.app_name_input = QLineEdit(self)
        app_name_layout.addWidget(QLabel("Application Name:", self))
        app_name_layout.addWidget(self.app_name_input)
        app_layout.addLayout(app_name_layout)

        # Version
        version_layout = QHBoxLayout()
        self.version_input = QLineEdit(self)
        version_layout.addWidget(QLabel("Version:", self))
        version_layout.addWidget(self.version_input)
        app_layout.addLayout(version_layout)

        # Environment
        env_layout = QHBoxLayout()
        self.env_combo = QComboBox(self)
        self.env_combo.addItems(["development", "production", "testing"])
        env_layout.addWidget(QLabel("Environment:", self))
        env_layout.addWidget(self.env_combo)
        app_layout.addLayout(env_layout)

        self.layout.addWidget(app_group)

        # UI Settings
        ui_group = QWidget()
        ui_layout = QVBoxLayout(ui_group)
        ui_layout.addWidget(QLabel("UI Settings", self))

        # Theme
        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(["dark", "light"])
        theme_layout.addWidget(QLabel("Theme:", self))
        theme_layout.addWidget(self.theme_combo)
        ui_layout.addLayout(theme_layout)

        # Font Size
        font_size_layout = QHBoxLayout()
        self.font_size_input = QLineEdit(self)
        font_size_layout.addWidget(QLabel("Font Size:", self))
        font_size_layout.addWidget(self.font_size_input)
        ui_layout.addLayout(font_size_layout)

        self.layout.addWidget(ui_group)

        # Debug Settings
        debug_group = QWidget()
        debug_layout = QVBoxLayout(debug_group)
        debug_layout.addWidget(QLabel("Debug Settings", self))

        # Debug Toggle
        debug_layout2 = QHBoxLayout()
        self.debug_checkbox = QCheckBox("Enable Debug Mode", self)
        debug_layout.addWidget(self.debug_checkbox)

        # Log Level
        log_level_layout = QHBoxLayout()
        self.log_level_combo = QComboBox(self)
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        log_level_layout.addWidget(QLabel("Log Level:", self))
        log_level_layout.addWidget(self.log_level_combo)
        debug_layout.addLayout(log_level_layout)
        debug_layout.addLayout(debug_layout2)

        self.layout.addWidget(debug_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_config)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)
        logger.info("Configuration UI setup complete")

    def _load_config(self):
        """Load configuration values into UI elements."""
        self.app_name_input.setText(self.config_manager.get("app_name", "Atlas"))
        self.version_input.setText(self.config_manager.get("version", "1.0.0"))
        self.env_combo.setCurrentText(self.config_manager.get_environment())
        self.theme_combo.setCurrentText(self.config_manager.get("theme", "dark"))
        self.font_size_input.setText(str(self.config_manager.get("ui.font_size", 12)))
        self.debug_checkbox.setChecked(self.config_manager.get("debug", False))
        self.log_level_combo.setCurrentText(
            self.config_manager.get("log_level", "INFO")
        )
        logger.info("Configuration values loaded into UI")

    def save_config(self):
        """Save configuration from UI elements to config manager."""
        try:
            # Update configuration
            self.config_manager.set("app_name", self.app_name_input.text())
            self.config_manager.set("version", self.version_input.text())
            new_env = self.env_combo.currentText()
            self.config_manager.set_environment(new_env)
            self.config_manager.set("theme", self.theme_combo.currentText())
            font_size = int(self.font_size_input.text())
            self.config_manager.set(
                "ui",
                {
                    "font_size": font_size,
                    "window_width": self.config_manager.get("ui.window_width", 1200),
                    "window_height": self.config_manager.get("ui.window_height", 800),
                },
            )
            debug_enabled = self.debug_checkbox.isChecked()
            self.config_manager.set("debug", debug_enabled)
            log_level = self.log_level_combo.currentText()
            self.config_manager.set("log_level", log_level)

            # Save to file
            if self.config_manager.save(new_env):
                QMessageBox.information(
                    self, "Success", "Configuration saved successfully."
                )
                logger.info("Configuration saved successfully")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "Failed to save configuration.")
                logger.error("Failed to save configuration")
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {str(e)}")
            logger.error(f"Invalid input while saving configuration: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected error while saving configuration: {e}")
