"""
SecurityPanel (PySide6 version)
Migrated from customtkinter version in backup_ui/security_panel.py
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SecurityPanel(QWidget):
    def __init__(
        self,
        plugin_manager,
        plugin_enabled_vars,
        notification_email_var,
        notification_telegram_var,
        notification_sms_var,
        parent=None,
    ):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.plugin_enabled_vars = plugin_enabled_vars
        self.notification_email_var = notification_email_var
        self.notification_telegram_var = notification_telegram_var
        self.notification_sms_var = notification_sms_var
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)

        # Settings Group
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()
        settings_group.setLayout(settings_layout)

        # Destructive Op Confirmation Threshold
        destructive_layout = QHBoxLayout()
        destructive_label = QLabel("Destructive Op Confirmation Threshold")
        self.destructive_slider = QSlider(
            Qt.Orientation.Horizontal
        )  # lint: f7230015-c152-4618-b257-dee7376a115c
        self.destructive_slider.setRange(0, 100)
        self.destructive_slider.setSingleStep(10)
        self.destructive_slider.setValue(80)
        destructive_layout.addWidget(destructive_label)
        destructive_layout.addWidget(self.destructive_slider)
        settings_layout.addLayout(destructive_layout)

        # API Usage Alert Threshold
        api_layout = QHBoxLayout()
        api_label = QLabel("API Usage Alert Threshold")
        self.api_usage_slider = QSlider(
            Qt.Orientation.Horizontal
        )  # lint: 118aad56-54b3-4b60-9e6a-503f654bee22
        self.api_usage_slider.setRange(0, 100)
        self.api_usage_slider.setSingleStep(10)
        self.api_usage_slider.setValue(50)
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_usage_slider)
        settings_layout.addLayout(api_layout)

        # File Access Warning Threshold
        file_layout = QHBoxLayout()
        file_label = QLabel("File Access Warning Threshold")
        self.file_access_slider = QSlider(
            Qt.Orientation.Horizontal
        )  # lint: a97c2f73-a726-44f6-ab89-6c4913a92e3e
        self.file_access_slider.setRange(0, 100)
        self.file_access_slider.setSingleStep(10)
        self.file_access_slider.setValue(70)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_access_slider)
        settings_layout.addLayout(file_layout)

        main_layout.addWidget(settings_group)

        # Security Rules
        rules_label = QLabel("Security Rules (one per line)")
        main_layout.addWidget(rules_label)
        self.security_rules_text = QTextEdit()
        self.security_rules_text.setFixedHeight(150)
        self.security_rules_text.setPlainText(
            "#Example Rule: Deny all shell commands that contain 'rm -rf'\nDENY,TERMINAL,.*rm -rf.*"
        )
        main_layout.addWidget(self.security_rules_text)

        # Plugin Management
        plugin_group = QGroupBox("Plugin Management")
        plugin_layout = QVBoxLayout()
        plugin_group.setLayout(plugin_layout)
        all_plugins = (
            self.plugin_manager.get_all_plugins() if self.plugin_manager else {}
        )
        if not all_plugins:
            plugin_layout.addWidget(QLabel("No plugins found."))
        else:
            for plugin_id, plugin_data in all_plugins.items():
                manifest = plugin_data.get("manifest", {})
                plugin_name = manifest.get("name", plugin_id)
                description = manifest.get("description", "No description provided.")
                var = self.plugin_enabled_vars.get(plugin_id)
                if var is None:
                    var = False
                    self.plugin_enabled_vars[plugin_id] = var
                cb = QCheckBox(plugin_name)
                cb.setChecked(bool(var))
                # Connect to update dict
                cb.stateChanged.connect(
                    lambda state, pid=plugin_id: self.plugin_enabled_vars.__setitem__(
                        pid, state == Qt.CheckState.Checked
                    )
                )  # lint: c461a19a-f805-48e0-8e5a-320813d8ab65
                plugin_layout.addWidget(cb)
                plugin_layout.addWidget(QLabel(f"({description})"))
        main_layout.addWidget(plugin_group)

        # Notification Channels
        notif_group = QGroupBox("Notification Channels")
        notif_layout = QHBoxLayout()
        notif_group.setLayout(notif_layout)
        self.email_checkbox = QCheckBox("Email")
        self.email_checkbox.setChecked(self.notification_email_var)
        self.email_checkbox.stateChanged.connect(
            lambda state: setattr(
                self, "notification_email_var", state == Qt.CheckState.Checked
            )
        )  # lint: 751c9267-dce0-4fa3-9058-976a2a3936b2
        self.telegram_checkbox = QCheckBox("Telegram")
        self.telegram_checkbox.setChecked(self.notification_telegram_var)
        self.telegram_checkbox.stateChanged.connect(
            lambda state: setattr(
                self, "notification_telegram_var", state == Qt.CheckState.Checked
            )
        )  # lint: ebc096a5-8eb9-4eee-ace3-1f04485386f5
        self.sms_checkbox = QCheckBox("SMS")
        self.sms_checkbox.setChecked(self.notification_sms_var)
        self.sms_checkbox.stateChanged.connect(
            lambda state: setattr(
                self, "notification_sms_var", state == Qt.CheckState.Checked
            )
        )  # lint: 6c17fdc4-a2ad-4b0d-bb1a-7d093bd9941a
        notif_layout.addWidget(self.email_checkbox)
        notif_layout.addWidget(self.telegram_checkbox)
        notif_layout.addWidget(self.sms_checkbox)
        main_layout.addWidget(notif_group)

        # Buttons (Placeholder for Save/Load)
        button_frame = QFrame()
        button_layout = QHBoxLayout()
        button_frame.setLayout(button_layout)
        save_button = QPushButton("Save Settings")
        load_button = QPushButton("Load Settings")
        button_layout.addWidget(save_button)
        button_layout.addWidget(load_button)
        main_layout.addWidget(button_frame)

    # Compatibility with grid() calls in legacy code
    def grid(self, *args, **kwargs):
        # Legacy no-op for compatibility
        pass  # lint: 54301830-3520-48f5-920a-ca65c1f1001b
