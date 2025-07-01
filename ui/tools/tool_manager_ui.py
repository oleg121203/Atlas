import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.events import NEW_TOOL_REGISTERED, TOOL_ERROR, TOOL_EXECUTED
from ui.components.loading_spinner import LoadingSpinner


class ToolManagerUI(QWidget):
    """UI component for managing tools in Atlas."""

    tool_selected = Signal(str)
    tool_activated = Signal(str)

    def __init__(
        self, config: Optional[Dict[str, Any]] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.tools: List[str] = []
        self.initialize_ui()
        # Connect to backend manager
        from agents.self_regeneration_manager import self_regeneration_manager

        self.tool_activated.connect(self_regeneration_manager.handle_tool_activation)
        self.event_bus.subscribe(TOOL_EXECUTED, self._on_tool_executed)
        self.event_bus.subscribe(TOOL_ERROR, self._on_tool_error)
        self.event_bus.subscribe(NEW_TOOL_REGISTERED, self._on_tools_changed)
        self.event_bus.subscribe("ToolRemoved", self._on_tools_changed)

    def initialize_ui(self) -> None:
        """Initialize the UI components for tool management."""
        self.setWindowTitle("Atlas Tool Manager")
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Available Tools")
        header_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #00ffaa;"
        )
        layout.addWidget(header_label)

        # Tool List
        self.tool_list = QListWidget()
        self.tool_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QListWidget::item {
                border-bottom: 1px solid #00ffaa;
            }
            QListWidget::item:selected {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        self.tool_list.itemClicked.connect(self.on_tool_selected)
        layout.addWidget(self.tool_list)

        # Buttons
        button_layout = QHBoxLayout()
        self.activate_button = QPushButton("Activate Tool")
        self.activate_button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        self.activate_button.clicked.connect(self.on_activate_tool)
        button_layout.addWidget(self.activate_button)

        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_tools)
        button_layout.addWidget(self.refresh_button)

        self.spinner = LoadingSpinner(self)
        layout.addWidget(self.spinner)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.apply_cyberpunk_style()

    def apply_cyberpunk_style(self) -> None:
        """Apply cyberpunk styling to the tool manager UI."""
        self.setStyleSheet("background-color: #0a0a0a;")

    def update_tool_list(self, tools: List[str]) -> None:
        """Update the list of available tools."""
        self.tools = tools
        self.tool_list.clear()
        self.tool_list.addItems(tools)
        self.logger.info("Updated tool list with %d tools", len(tools))

    @Slot()
    def on_tool_selected(self) -> None:
        """Handle tool selection event."""
        selected_items = self.tool_list.selectedItems()
        if selected_items:
            tool_name = selected_items[0].text()
            self.tool_selected.emit(tool_name)
            self.logger.info("Selected tool: %s", tool_name)

    @Slot()
    def on_activate_tool(self) -> None:
        """Handle tool activation event."""
        selected_items = self.tool_list.selectedItems()
        if selected_items:
            tool_name = selected_items[0].text()
            self.activate_button.setEnabled(False)
            self.spinner.start()
            self.tool_activated.emit(tool_name)
            self.logger.info("Activated tool: %s", tool_name)

    @Slot()
    def refresh_tools(self) -> None:
        """Refresh the list of available tools."""
        self.logger.info("Refreshing tool list")
        from agents.self_regeneration_manager import self_regeneration_manager

        tools = self_regeneration_manager.get_available_tools()
        self.update_tool_list(tools)

    def _on_tool_executed(self, data):
        self.spinner.stop()
        self.activate_button.setEnabled(True)
        self.logger.info(f"Tool executed: {data}")
        msg = data.get("message") if isinstance(data, dict) else str(data)
        QMessageBox.information(
            self, "Tool Executed", msg or "Tool executed successfully."
        )
        # Оновити статус-бар через EventBus
        if hasattr(self, "event_bus"):
            self.event_bus.publish(
                "ShowNotification",
                {"type": "info", "message": msg or "Tool executed successfully."},
            )

    def _on_tool_error(self, data):
        self.spinner.stop()
        self.activate_button.setEnabled(True)
        self.logger.error(f"Tool error: {data}")
        msg = data.get("error") if isinstance(data, dict) else str(data)
        QMessageBox.critical(self, "Tool Error", msg or "Tool execution failed.")
        # Оновити статус-бар через EventBus
        if hasattr(self, "event_bus"):
            self.event_bus.publish(
                "ShowNotification",
                {"type": "error", "message": msg or "Tool execution failed."},
            )

    def _on_tools_changed(self, data):
        self.logger.info(f"Tools changed event: {data}")
        self.refresh_tools()
