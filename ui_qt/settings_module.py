from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QInputDialog, QMessageBox, QFormLayout, QComboBox, QFrame
from PySide6.QtCore import Qt
from ui_qt.i18n import _

class SettingsModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsModule")
        self.plugin_manager = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.title = QLabel(_("⚙️ Settings"))
        self.title.setStyleSheet("color: #00ff7f; font-size: 22px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(self.title)

        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.language_label = QLabel(_("Language"))
        self.language_combo = QComboBox()
        self.language_combo.addItems([_("English"), _("Ukrainian"), _("Russian")])
        self.form.addRow(self.language_label, self.language_combo)
        layout.addLayout(self.form)

        self.save_btn = QPushButton(_("Save Settings"))
        self.save_btn.setStyleSheet("background: #00ff7f; color: #181c20; font-weight: bold; border-radius: 6px; padding: 6px 18px;")
        layout.addWidget(self.save_btn)

        self.plugins_title = QLabel(_("Plugin Settings"))
        self.plugins_title.setStyleSheet("color: #00ff7f; font-size: 18px; font-weight: bold; margin-top: 18px;")
        layout.addWidget(self.plugins_title)

        self.plugins_frame = QFrame()
        self.plugins_layout = QVBoxLayout(self.plugins_frame)
        self.plugins_layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.plugins_frame)

    def set_plugin_manager(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.update_plugin_settings_section()

    def update_plugin_settings_section(self):
        # Очистити попередні віджети
        while self.plugins_layout.count():
            item = self.plugins_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        if not self.plugin_manager:
            return
        for name, plugin in self.plugin_manager.plugins.items():
            if plugin.active:
                w = plugin.settings_widget(self.plugins_frame)
                if w:
                    self.plugins_layout.addWidget(w)
                else:
                    info = plugin.info()
                    self.plugins_layout.addWidget(QLabel(f"{info.get('name')}: {_('No settings available')}"))

    def update_ui(self):
        self.title.setText(_("⚙️ Settings"))
        self.language_label.setText(_("Language"))
        self.language_combo.setItemText(0, _( "English"))
        self.language_combo.setItemText(1, _( "Ukrainian"))
        self.language_combo.setItemText(2, _( "Russian"))
        self.save_btn.setText(_("Save Settings"))
        self.plugins_title.setText(_("Plugin Settings"))
        self.update_plugin_settings_section()

    def edit_setting(self):
        row = self.list.currentRow()
        if row >= 0:
            value, ok = QInputDialog.getText(self, "Edit Setting", "New value:")
            if ok:
                self.list.item(row).setText(value)
        else:
            QMessageBox.warning(self, "Edit Setting", "Select a setting to edit.")

    def save_settings(self):
        QMessageBox.information(self, "Save Settings", "Settings saved (stub).") 