"""Enhanced Settings Panel component for Atlas."""

import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.events import SHOW_NOTIFICATION
from ui.module_communication import EVENT_BUS


class EnhancedSettingsPanel(QWidget):
    """Advanced settings panel for Atlas with cyberpunk styling."""

    settings_updated = Signal(dict)
    settings_saved = Signal()
    settings_reset = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                color: #00ffaa;
            }
            QGroupBox {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 2px;
            }
            QCheckBox {
                color: #00ffaa;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #00ffaa;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #00ffaa;
                background-color: #00ffaa;
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
        self.settings_widgets: Dict[str, Any] = {}
        self.logger.info("EnhancedSettingsPanel component initialized")

    def initialize_ui(self) -> None:
        """Initialize the UI components for the enhanced settings panel."""
        layout = QVBoxLayout(self)

        header_label = QLabel("Advanced Settings")
        header_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #00ffaa;"
        )
        layout.addWidget(header_label)

        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Placeholder for settings groups
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Buttons for save and reset
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.on_save_settings)
        button_layout.addWidget(self.save_button)

        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.on_reset_settings)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def update_settings_ui(self, settings_config: Dict[str, Any]) -> None:
        """Update the settings UI based on the provided configuration.

        Args:
            settings_config (Dict[str, Any]): Dictionary containing settings configuration.
        """
        self.settings_widgets.clear()
        scroll_content = self.findChild(QScrollArea).widget()
        scroll_layout = scroll_content.layout() if scroll_content else None

        if scroll_layout:
            # Clear existing widgets in scroll layout except for stretch
            for i in reversed(range(scroll_layout.count())):
                item = scroll_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    widget.deleteLater()
                if item:
                    scroll_layout.removeItem(item)

            for category, category_settings in settings_config.items():
                group_box = QGroupBox(category.replace("_", " ").title())
                group_layout = QVBoxLayout()

                for setting_name, setting_info in category_settings.items():
                    setting_type = setting_info.get("type", "text")
                    setting_label = setting_info.get(
                        "label", setting_name.replace("_", " ").title()
                    )
                    setting_value = setting_info.get("value")
                    setting_options = setting_info.get("options", [])

                    label = QLabel(f"{setting_label}:")
                    group_layout.addWidget(label)

                    if setting_type == "bool":
                        widget = QCheckBox()
                        widget.setChecked(bool(setting_value))
                        group_layout.addWidget(widget)
                    elif setting_type == "select":
                        widget = QComboBox()
                        widget.addItems(setting_options)
                        if setting_value in setting_options:
                            widget.setCurrentText(setting_value)
                        group_layout.addWidget(widget)
                    else:  # Default to text input
                        widget = QLineEdit()
                        widget.setText(str(setting_value))
                        group_layout.addWidget(widget)

                    full_setting_name = f"{category}.{setting_name}"
                    self.settings_widgets[full_setting_name] = widget
                    self.logger.debug(f"Added setting widget for {full_setting_name}")

                group_box.setLayout(group_layout)
                scroll_layout.addWidget(group_box)

            scroll_layout.addStretch(1)
            self.logger.info(
                f"Updated settings UI with {len(self.settings_widgets)} settings"
            )
        else:
            self.logger.warning("No scroll layout found to update settings UI")

    def get_current_settings(self) -> Dict[str, Any]:
        """Retrieve the current settings from the UI widgets.

        Returns:
            Dict[str, Any]: Dictionary of setting names and their current values.
        """
        current_settings = {}
        for setting_name, widget in self.settings_widgets.items():
            if isinstance(widget, QCheckBox):
                current_settings[setting_name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                current_settings[setting_name] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                current_settings[setting_name] = widget.text()
            self.logger.debug(
                f"Retrieved setting {setting_name}: {current_settings[setting_name]}"
            )
        return current_settings

    @Slot()
    def on_save_settings(self) -> None:
        """Handle save settings button click."""
        current_settings = self.get_current_settings()
        self.settings_updated.emit(current_settings)
        self.settings_saved.emit()
        EVENT_BUS.publish("SETTINGS_SAVED", current_settings)
        EVENT_BUS.publish(
            SHOW_NOTIFICATION, {"type": "info", "message": "Settings saved"}
        )
        self.logger.info("Settings saved")

    @Slot()
    def on_reset_settings(self) -> None:
        """Handle reset settings button click."""
        self.settings_reset.emit()
        EVENT_BUS.publish("SETTINGS_RESET", {})
        EVENT_BUS.publish(
            SHOW_NOTIFICATION, {"type": "info", "message": "Settings reset to defaults"}
        )
        self.logger.info("Settings reset to defaults")
