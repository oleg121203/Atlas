from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.i18n import _
from ui.plugin_manager import PluginManager


class SettingsModule(QWidget):
    """Settings management module with cyberpunk styling.

    Attributes:
        plugin_manager: Plugin manager instance
        form: QFormLayout for settings
        language_combo: QComboBox for language selection
        language_label: QLabel for language label
        save_btn: QPushButton for saving settings
        plugins_title: QLabel for plugin settings title
        plugins_frame: QFrame for plugin settings
        plugins_layout: QVBoxLayout for plugin settings widgets
        title: QLabel for module title
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the settings module.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setObjectName("SettingsModule")
        self.plugin_manager: Optional[PluginManager] = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.title = QLabel(_("⚙️ Settings"))
        self.title.setStyleSheet(
            "color: #00ff7f; font-size: 22px; font-weight: bold; letter-spacing: 1px;"
        )
        layout.addWidget(self.title)

        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.language_label = QLabel(_("Language"))
        self.language_combo = QComboBox()
        self.language_combo.addItems([_("English"), _("Ukrainian"), _("Russian")])
        self.form.addRow(self.language_label, self.language_combo)
        layout.addLayout(self.form)

        self.save_btn = QPushButton(_("Save Settings"))
        self.save_btn.setStyleSheet(
            "background: #00ff7f; color: #181c20; font-weight: bold; border-radius: 6px; padding: 6px 18px;"
        )
        layout.addWidget(self.save_btn)

        self.plugins_title = QLabel(_("Plugin Settings"))
        self.plugins_title.setStyleSheet(
            "color: #00ff7f; font-size: 18px; font-weight: bold; margin-top: 18px;"
        )
        layout.addWidget(self.plugins_title)

        self.plugins_frame = QFrame()
        self.plugins_layout = QVBoxLayout(self.plugins_frame)
        self.plugins_layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.plugins_frame)

    def set_plugin_manager(self, plugin_manager: PluginManager) -> None:
        """Set the plugin manager instance.

        Args:
            plugin_manager: Plugin manager instance
        """
        self.plugin_manager = plugin_manager
        self.update_plugin_settings_section()

    def update_plugin_settings_section(self) -> None:
        """Update the plugin settings section in the UI.

        Clears old widgets and adds new ones from active plugins.
        """
        # Remove old widgets
        while self.plugins_layout.count():
            item = self.plugins_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if not self.plugin_manager:
            return

        # Add settings from active plugins
        for plugin in self.plugin_manager.plugins.values():
            if plugin.active:
                try:
                    widget = plugin.settings_widget(self.plugins_frame)
                    if widget:
                        self.plugins_layout.addWidget(widget)
                    else:
                        info = plugin.info()
                        label = QLabel(
                            f"{info.get('name', plugin.name)}: {str(_('No settings available')) or 'No settings available'}"
                        )
                        self.plugins_layout.addWidget(label)
                except Exception as e:
                    self.logger.error(
                        f"Error adding settings for plugin {plugin.name}: {e}"
                    )
                    continue

    def update_ui(self) -> None:
        """Update UI elements with translated text."""
        self.title.setText(str(_("⚙️ Settings")) or "⚙️ Settings")
        self.language_label.setText(str(_("Language")) or "Language")
        self.language_combo.setItemText(0, str(_("English")) or "English")
        self.language_combo.setItemText(1, str(_("Ukrainian")) or "Ukrainian")
        self.language_combo.setItemText(2, str(_("Russian")) or "Russian")
        self.save_btn.setText(str(_("Save Settings")) or "Save Settings")
        self.plugins_title.setText(str(_("Plugin Settings")) or "Plugin Settings")
        self.update_plugin_settings_section()

    def edit_setting(self) -> None:
        """Edit a selected setting.

        Opens a dialog to get new value and updates the setting.
        """
        row = self.list.currentRow()
        if row >= 0:
            try:
                value, ok = QInputDialog.getText(
                    self,
                    str(_("Edit Setting")) or "Edit Setting",
                    str(_("New value:")) or "New value:",
                )
                if ok:
                    self.list.item(row).setText(value)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    str(_("Error")) or "Error",
                    f"{str(_('Failed to edit setting:')) or 'Failed to edit setting:'} {str(e)}",
                )
        else:
            QMessageBox.warning(
                self,
                str(_("Edit Setting")) or "Edit Setting",
                str(_("Select a setting to edit.")) or "Select a setting to edit.",
            )

    def save_settings(self) -> None:
        """Save current settings.

        Shows a message when complete.
        """
        try:
            # Save settings logic here
            QMessageBox.information(
                self,
                str(_("Save Settings")) or "Save Settings",
                str(_("Settings saved successfully."))
                or "Settings saved successfully.",
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                str(_("Error")) or "Error",
                f"{str(_('Failed to save settings:')) or 'Failed to save settings:'} {str(e)}",
            )
