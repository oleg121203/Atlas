from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.event_bus import EventBus


class SystemControlPanel(QWidget):
    def __init__(self, parent=None, agent_manager=None):
        super().__init__(parent)
        self.agent_manager = agent_manager
        self.event_bus = EventBus()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("System Control")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0 5px 0;")
        layout.addWidget(title)

        # Help Button
        help_layout = QHBoxLayout()
        help_layout.addStretch()
        help_button = QPushButton("?")
        help_button.setFixedWidth(30)
        help_button.setStyleSheet(
            "background-color: #3A7CA5; color: white; border: none; padding: 5px;"
        )
        help_button.clicked.connect(self._show_help)
        help_layout.addWidget(help_button)
        layout.addLayout(help_layout)

        # Mute/Unmute Button
        mute_button = QPushButton("Mute")
        mute_button.clicked.connect(self._mute)
        mute_button.setStyleSheet(
            "background-color: #444; color: white; border: none; padding: 10px; margin: 5px 0;"
        )
        layout.addWidget(mute_button)
        # TODO: Add tooltip functionality for PySide6

        # Sleep Mac Button
        sleep_button = QPushButton("Sleep Mac")
        sleep_button.clicked.connect(self._sleep_mac)
        sleep_button.setStyleSheet(
            "background-color: #444; color: white; border: none; padding: 10px; margin: 5px 0;"
        )
        layout.addWidget(sleep_button)

        # Open App Section
        app_layout = QHBoxLayout()
        app_label = QLabel("Open App:")
        app_label.setStyleSheet("color: white; margin-right: 10px;")
        app_layout.addWidget(app_label)
        self.app_combobox = QComboBox()
        self.app_combobox.setEditable(True)
        self.app_combobox.setStyleSheet(
            "background-color: #333; color: white; border: none; padding: 5px; margin-right: 10px;"
        )
        app_layout.addWidget(self.app_combobox)
        open_app_button = QPushButton("Open")
        open_app_button.clicked.connect(self._open_app)
        open_app_button.setStyleSheet(
            "background-color: #444; color: white; border: none; padding: 5px;"
        )
        app_layout.addWidget(open_app_button)
        layout.addLayout(app_layout)

        # Volume Control Section
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Set Volume:")
        volume_label.setStyleSheet("color: white; margin-right: 10px;")
        volume_layout.addWidget(volume_label)
        self.volume_slider = QSlider()
        self.volume_slider.setOrientation(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self._set_volume)
        self.volume_slider.setStyleSheet("background-color: #333; margin-right: 10px;")
        volume_layout.addWidget(self.volume_slider)
        self.volume_value_label = QLabel("50")
        self.volume_value_label.setStyleSheet(
            "color: white; margin-right: 10px; min-width: 30px;"
        )
        volume_layout.addWidget(self.volume_value_label)
        refresh_volume_button = QPushButton("Refresh")
        refresh_volume_button.clicked.connect(self._refresh_volume)
        refresh_volume_button.setStyleSheet(
            "background-color: #444; color: white; border: none; padding: 5px;"
        )
        volume_layout.addWidget(refresh_volume_button)
        layout.addLayout(volume_layout)

        # Current Volume Display
        self.volume_label = QLabel("Current Volume: ?")
        self.volume_label.setStyleSheet("color: white; margin: 5px 0;")
        layout.addWidget(self.volume_label)

        # Refresh Apps Button
        refresh_apps_button = QPushButton("Refresh Apps")
        refresh_apps_button.clicked.connect(self._refresh_apps)
        refresh_apps_button.setStyleSheet(
            "background-color: #444; color: white; border: none; padding: 10px; margin: 5px 0;"
        )
        layout.addWidget(refresh_apps_button)

        # Feedback Label
        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet("color: #2E8B57; margin: 10px 0;")
        layout.addWidget(self.feedback_label)

        # Status Bar
        self.status_bar = QLabel("Ready")
        self.status_bar.setStyleSheet(
            "background-color: #222; color: white; padding: 5px; margin: 10px 0 0 0;"
        )
        layout.addWidget(self.status_bar)

        layout.addStretch()
        self.setLayout(layout)

        self._refresh_volume()
        self._refresh_apps()

    def _mute(self):
        result = self.agent_manager.execute_tool("system_event", {"event": "mute"})
        self._show_feedback(result)

    def _sleep_mac(self):
        result = self.agent_manager.execute_tool("system_event", {"event": "sleep_mac"})
        self._show_feedback(result)

    def _open_app(self):
        app_name = self.app_combobox.currentText()
        if app_name:
            result = self.agent_manager.execute_tool(
                "system_event", {"event": "open_app", "app_name": app_name}
            )
            self._show_feedback(result)

    def _set_volume(self):
        volume = self.volume_slider.value()
        self.volume_value_label.setText(str(volume))
        result = self.agent_manager.execute_tool(
            "system_event", {"event": "set_volume", "volume": volume}
        )
        self._show_feedback(result)
        self._refresh_volume()

    def _refresh_volume(self):
        result = self.agent_manager.execute_tool(
            "system_event", {"event": "get_volume"}
        )
        if result.get("status") == "success":
            self.volume_label.setText(f"Current Volume: {result.get('output')}")
            self._set_status(f"Current volume: {result.get('output')}")
        else:
            self.volume_label.setText("Current Volume: ?")
            self._set_status("Could not get volume.")

    def _refresh_apps(self):
        result = self.agent_manager.execute_tool(
            "system_event", {"event": "get_running_apps"}
        )
        if result.get("status") == "success":
            apps = result.get("output", "").split(",")
            apps = [app.strip() for app in apps if app.strip()]
            self.app_combobox.clear()
            self.app_combobox.addItems(apps)
            self._set_status(f"Updated {len(apps)} running apps")
        else:
            self._set_status("Could not update running apps")

    def _show_feedback(self, result):
        if result.get("status") == "success":
            self.feedback_label.setText("Success!")
            self.feedback_label.setStyleSheet("color: #2E8B57;")
        else:
            self.feedback_label.setText(f"Error: {result.get('error')}")
            self.feedback_label.setStyleSheet("color: #B22222;")

    def _set_status(self, msg):
        self.status_bar.setText(msg)

    def _show_help(self):
        # TODO: Implement help dialog in PySide6
        pass
