import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class SystemControlModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.agent_manager = None  # Initialize as None, to be set later if needed
        self._build_ui()

    def set_agent_manager(self, agent_manager):
        """Set the agent manager for this module."""
        self.agent_manager = agent_manager
        self._refresh_volume()  # Now safe to refresh volume with agent_manager set

    def _build_ui(self):
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel("System Control")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(title)
        help_btn = QPushButton("?")
        help_btn.setFixedWidth(30)
        help_btn.clicked.connect(self._show_help)
        header.addWidget(help_btn)
        header.addStretch()
        layout.addLayout(header)

        # Mute/Unmute
        mute_btn = QPushButton("Mute")
        mute_btn.clicked.connect(self._mute)
        mute_btn.setToolTip("Mute system audio")
        unmute_btn = QPushButton("Unmute")
        unmute_btn.clicked.connect(self._unmute)
        unmute_btn.setToolTip("Unmute system audio")
        row1 = QHBoxLayout()
        row1.addWidget(mute_btn)
        row1.addWidget(unmute_btn)
        layout.addLayout(row1)

        # Sleep
        sleep_btn = QPushButton("Sleep Mac")
        sleep_btn.clicked.connect(self._sleep)
        sleep_btn.setToolTip("Put Mac to sleep")
        layout.addWidget(sleep_btn)

        # Open App
        open_row = QHBoxLayout()
        open_label = QLabel("Open App:")
        self.app_entry = QLineEdit()
        self.app_entry.setPlaceholderText("App name (e.g. Safari)")
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self._open_app)
        open_btn.setToolTip("Open the specified app by name")
        open_row.addWidget(open_label)
        open_row.addWidget(self.app_entry)
        open_row.addWidget(open_btn)
        layout.addLayout(open_row)

        # Set Volume
        vol_row = QHBoxLayout()
        vol_label = QLabel("Set Volume:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setToolTip("Adjust system volume")
        set_vol_btn = QPushButton("Apply Volume")
        set_vol_btn.clicked.connect(self._set_volume)
        set_vol_btn.setToolTip("Set system volume to selected level")
        vol_row.addWidget(vol_label)
        vol_row.addWidget(self.volume_slider)
        vol_row.addWidget(set_vol_btn)
        layout.addLayout(vol_row)

        # Current Volume
        self.volume_label = QLabel("Current Volume: ?")
        layout.addWidget(self.volume_label)
        refresh_vol_btn = QPushButton("Refresh Volume")
        refresh_vol_btn.clicked.connect(self._refresh_volume)
        refresh_vol_btn.setToolTip("Get current system volume")
        layout.addWidget(refresh_vol_btn)

        # Running Apps
        self.apps_label = QLabel("Running Apps: ?")
        layout.addWidget(self.apps_label)
        refresh_apps_btn = QPushButton("Refresh Apps")
        refresh_apps_btn.clicked.connect(self._refresh_apps)
        refresh_apps_btn.setToolTip("List currently running apps")
        layout.addWidget(refresh_apps_btn)

        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

    def _show_help(self):
        QMessageBox.information(
            self,
            "System Control Help",
            "• Mute/Unmute: Control system audio.\n"
            "• Sleep Mac: Put your Mac to sleep.\n"
            "• Open App: Launch any app by name (e.g., Safari, Zoom.us).\n"
            "• Set Volume: Adjust system volume with the slider.\n"
            "• Refresh: Update current volume or running apps.\n"
            "• Status bar: See last action/result.\n"
            "\nTip: Hover over any button for a tooltip.",
        )

    def _mute(self):
        if hasattr(self, "agent_manager") and self.agent_manager:
            try:
                if hasattr(self.agent_manager, "execute_tool"):
                    result = self.agent_manager.execute_tool(
                        "system_event", {"event": "mute"}
                    )
                    self._show_feedback(result)
                    self._refresh_volume()
                    self._set_status("Muted system audio.")
                else:
                    self._execute_tool_fallback("system_event", {"event": "mute"})
            except Exception as e:
                logger.error(f"Error during mute: {e}")
        else:
            logger.warning("Agent manager not set, skipping mute")

    def _unmute(self):
        if hasattr(self, "agent_manager") and self.agent_manager:
            try:
                if hasattr(self.agent_manager, "execute_tool"):
                    result = self.agent_manager.execute_tool(
                        "system_event", {"event": "unmute"}
                    )
                    self._show_feedback(result)
                    self._refresh_volume()
                    self._set_status("Unmuted system audio.")
                else:
                    self._execute_tool_fallback("system_event", {"event": "unmute"})
            except Exception as e:
                logger.error(f"Error during unmute: {e}")
        else:
            logger.warning("Agent manager not set, skipping unmute")

    def _sleep(self):
        if hasattr(self, "agent_manager") and self.agent_manager:
            try:
                if hasattr(self.agent_manager, "execute_tool"):
                    result = self.agent_manager.execute_tool(
                        "system_event", {"event": "sleep"}
                    )
                    self._show_feedback(result)
                    self._set_status("Put Mac to sleep.")
                else:
                    self._execute_tool_fallback("system_event", {"event": "sleep"})
            except Exception as e:
                logger.error(f"Error during sleep: {e}")
        else:
            logger.warning("Agent manager not set, skipping sleep")

    def _open_app(self):
        if hasattr(self, "agent_manager") and self.agent_manager:
            try:
                if hasattr(self.agent_manager, "execute_tool"):
                    app = self.app_entry.text().strip()
                    if app:
                        result = self.agent_manager.execute_tool(
                            "system_event", {"event": "open_app", "app_name": app}
                        )
                        self._show_feedback(result)
                        self._set_status(f"Opened {app}.")
                        self.app_entry.clear()
                    else:
                        self._show_feedback(
                            {"status": "error", "error": "Please enter an app name."}
                        )
                        self._set_status("No app name entered.")
                else:
                    self._execute_tool_fallback(
                        "system_event",
                        {
                            "event": "open_app",
                            "app_name": self.app_entry.text().strip(),
                        },
                    )
            except Exception as e:
                logger.error(f"Error during open app: {e}")
        else:
            logger.warning("Agent manager not set, skipping open app")

    def _set_volume(self):
        if hasattr(self, "agent_manager") and self.agent_manager:
            try:
                if hasattr(self.agent_manager, "execute_tool"):
                    vol = int(self.volume_slider.value())
                    result = self.agent_manager.execute_tool(
                        "system_event", {"event": "set_volume", "value": vol}
                    )
                    self._show_feedback(result)
                    self._set_status(f"Set volume to {vol}%.")
                else:
                    self._execute_tool_fallback(
                        "system_event",
                        {
                            "event": "set_volume",
                            "value": int(self.volume_slider.value()),
                        },
                    )
            except Exception as e:
                logger.error(f"Error during set volume: {e}")
        else:
            logger.warning("Agent manager not set, skipping set volume")

    def _refresh_volume(self):
        """Refresh the current volume level."""
        if hasattr(self, "agent_manager") and self.agent_manager:
            try:
                if hasattr(self.agent_manager, "execute_tool"):
                    result = self.agent_manager.execute_tool(
                        "system_event", {"event": "get_volume"}
                    )
                    if result and "volume" in result:
                        self.volume_slider.setValue(int(result["volume"]))
                        self.volume_label.setText(f"Volume: {result['volume']}%")
                else:
                    self._execute_tool_fallback("system_event", {"event": "get_volume"})
            except Exception as e:
                logger.error(f"Error refreshing volume: {e}")
        else:
            logger.warning("Agent manager not set, skipping volume refresh")

    def _refresh_apps(self):
        if hasattr(self, "agent_manager") and self.agent_manager:
            try:
                if hasattr(self.agent_manager, "execute_tool"):
                    result = self.agent_manager.execute_tool(
                        "system_event", {"event": "get_running_apps"}
                    )
                    if result.get("status") == "success":
                        self.apps_label.setText(f"Running Apps: {result.get('output')}")
                        self._set_status("Updated running apps.")
                    else:
                        self.apps_label.setText("Running Apps: ?")
                        self._set_status("Could not get running apps.")
                else:
                    self._execute_tool_fallback(
                        "system_event", {"event": "get_running_apps"}
                    )
            except Exception as e:
                logger.error(f"Error during refresh apps: {e}")
        else:
            logger.warning("Agent manager not set, skipping refresh apps")

    def _execute_tool_fallback(self, tool_name, params):
        logger.warning(
            f"Agent manager does not have execute_tool method, skipping {tool_name}"
        )
        self._set_status(
            f"Error: Agent manager does not have execute_tool method for {tool_name}"
        )

    def _show_feedback(self, result):
        if result.get("status") == "success":
            self.status_bar.showMessage("Success!", 3000)
        else:
            self.status_bar.showMessage(f"Error: {result.get('error')}", 5000)

    def _set_status(self, msg):
        self.status_bar.showMessage(msg, 4000)
