"""
Test suite for PySide6 SecurityPanel migration.
"""

from PySide6.QtWidgets import QApplication

from ui.security_panel import SecurityPanel


class DummyPluginManager:
    def get_all_plugins(self):
        return {
            "test_plugin": {
                "manifest": {
                    "name": "Test Plugin",
                    "description": "A test plugin for security panel.",
                }
            }
        }


def test_security_panel_basic(qtbot):
    QApplication.instance() or QApplication([])
    plugin_manager = DummyPluginManager()
    plugin_enabled_vars = {"test_plugin": True}
    panel = SecurityPanel(
        plugin_manager=plugin_manager,
        plugin_enabled_vars=plugin_enabled_vars,
        notification_email_var=True,
        notification_telegram_var=False,
        notification_sms_var=True,
    )
    qtbot.addWidget(panel)
    assert panel.destructive_slider.value() == 80
    assert panel.api_usage_slider.value() == 50
    assert panel.file_access_slider.value() == 70
    assert panel.security_rules_text.toPlainText().startswith("#Example Rule")
    # Plugin checkbox exists and is checked
    email_found = any(
        isinstance(child, type(panel.email_checkbox)) and child.text() == "Email"
        for child in panel.findChildren(type(panel.email_checkbox))
    )
    assert email_found
    assert panel.email_checkbox.isChecked() is True
    assert panel.telegram_checkbox.isChecked() is False
    assert panel.sms_checkbox.isChecked() is True
    # Plugin enabled var is updated by checkbox
    panel.email_checkbox.setChecked(False)
    assert panel.notification_email_var is False
