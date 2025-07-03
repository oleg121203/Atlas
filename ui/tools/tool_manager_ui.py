"""Tool Manager UI for Atlas."""

import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from tools.tool_manager import ToolManager
from ui.module_communication import EVENT_BUS


class ToolManagerUI(QWidget):
    """UI component for managing tools in Atlas."""

    tool_selected = Signal(str)
    tool_activated = Signal(str)

    def __init__(self, tool_manager: ToolManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.tool_manager = tool_manager
        self.event_bus = EVENT_BUS
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        self.connect_signals()
        self.logger.info("ToolManagerUI initialized")

    def setup_ui(self) -> None:
        """Set up the user interface for tool management."""
        # Main layout
        main_layout = QHBoxLayout(self)
        splitter = QSplitter()
        main_layout.addWidget(splitter)

        # Left panel - Tool list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        list_group = QGroupBox("Tools")
        list_layout = QVBoxLayout(list_group)

        self.tool_list = QListWidget()
        self.tool_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QListWidget::item {
                border-bottom: 1px solid #333;
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        list_layout.addWidget(self.tool_list)

        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.initialize_button = QPushButton("Initialize All")
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.initialize_button)
        list_layout.addLayout(button_layout)

        left_layout.addWidget(list_group)

        # Right panel - Tool details and controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        details_group = QGroupBox("Tool Details")
        details_layout = QVBoxLayout(details_group)

        self.name_label = QLabel("Name: ")
        self.version_label = QLabel("Version: ")
        self.category_label = QLabel("Category: ")
        self.description_label = QLabel("Description: ")
        self.status_label = QLabel("Status: Not loaded")

        details_layout.addWidget(self.name_label)
        details_layout.addWidget(self.version_label)
        details_layout.addWidget(self.category_label)
        details_layout.addWidget(self.description_label)
        details_layout.addWidget(self.status_label)

        control_layout = QHBoxLayout()
        self.load_button = QPushButton("Load")
        self.unload_button = QPushButton("Unload")
        self.execute_button = QPushButton("Execute")
        self.unload_button.setEnabled(False)
        self.execute_button.setEnabled(False)

        control_layout.addWidget(self.load_button)
        control_layout.addWidget(self.unload_button)
        control_layout.addWidget(self.execute_button)
        details_layout.addLayout(control_layout)

        right_layout.addWidget(details_group)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 400])

        self.setMinimumSize(600, 400)
        self.apply_cyberpunk_style()

    def apply_cyberpunk_style(self) -> None:
        """Apply cyberpunk styling to the tool manager UI."""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                color: #00ffaa;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                margin-top: 0.5em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
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
            QPushButton:disabled {
                background-color: #333;
                color: #666;
                border-color: #666;
            }
        """)

    def connect_signals(self) -> None:
        """Connect signals for tool management UI."""
        self.refresh_button.clicked.connect(self.refresh_tools)
        self.initialize_button.clicked.connect(self.initialize_all_tools)
        self.tool_list.itemSelectionChanged.connect(self.on_tool_selected)
        self.load_button.clicked.connect(self.on_load_clicked)
        self.unload_button.clicked.connect(self.on_unload_clicked)
        self.execute_button.clicked.connect(self.on_execute_clicked)

        # Connect to event bus if available
        if self.event_bus:
            self.event_bus.subscribe("tool_loaded", self._on_tool_event)
            self.event_bus.subscribe("tool_unloaded", self._on_tool_event)
            self.event_bus.subscribe("tool_error", self._on_tool_error)

    def _on_tool_event(self, event_data: Dict[str, Any]) -> None:
        """Handle tool events from the event bus."""
        tool_name = event_data.get("tool_name", "")
        self.logger.debug(f"Tool event received for: {tool_name}")

        # Refresh the display for the current selection
        selected_items = self.tool_list.selectedItems()
        if selected_items and selected_items[0].text() == tool_name:
            self.update_details(tool_name)

    def _on_tool_error(self, event_data: Dict[str, Any]) -> None:
        """Handle tool error events."""
        tool_name = event_data.get("tool_name", "")
        error = event_data.get("error", "Unknown error")
        self.logger.error(f"Tool error for {tool_name}: {error}")

        QMessageBox.critical(
            self, "Tool Error", f"Error in tool '{tool_name}': {error}"
        )

    @Slot()
    def refresh_tools(self) -> None:
        """Refresh the list of available tools."""
        self.logger.info("Refreshing tool list")
        self.tool_list.clear()

        # Get list of loaded tools
        loaded_tools = self.tool_manager.list_tools()

        # Get list of registered tool classes
        registered_tools = self.tool_manager.list_tool_classes()

        # Combine both lists
        all_tools = list(set(loaded_tools + registered_tools))

        for tool_name in all_tools:
            item = QListWidgetItem(tool_name)
            self.tool_list.addItem(item)

        self.logger.info(f"Refreshed tool list with {len(all_tools)} tools")

    @Slot()
    def initialize_all_tools(self) -> None:
        """Initialize all tools."""
        self.logger.info("Initializing all tools")
        self.tool_manager.initialize_all_tools()
        self.refresh_tools()

    @Slot()
    def on_tool_selected(self) -> None:
        """Handle tool selection in the list."""
        selected_items = self.tool_list.selectedItems()
        if not selected_items:
            self.clear_details()
            return

        tool_name = selected_items[0].text()
        self.logger.info(f"Tool selected: {tool_name}")
        self.tool_selected.emit(tool_name)
        self.update_details(tool_name)

    def update_details(self, tool_name: str) -> None:
        """Update the details panel for the selected tool."""
        # Check if tool is loaded
        tool = self.tool_manager.get_tool(tool_name)
        metadata = self.tool_manager.get_tool_metadata(tool_name)

        if tool and metadata:
            self.name_label.setText(f"Name: {metadata.get('name', tool_name)}")
            self.version_label.setText(f"Version: {metadata.get('version', 'Unknown')}")
            self.category_label.setText(
                f"Category: {metadata.get('category', 'Unknown')}"
            )
            self.description_label.setText(
                f"Description: {metadata.get('description', 'No description')}"
            )
            self.status_label.setText("Status: Loaded")

            self.load_button.setEnabled(False)
            self.unload_button.setEnabled(True)
            self.execute_button.setEnabled(True)
        else:
            # Tool is registered but not loaded
            self.name_label.setText(f"Name: {tool_name}")
            self.version_label.setText("Version: Unknown")
            self.category_label.setText("Category: Unknown")
            self.description_label.setText("Description: Tool not loaded")
            self.status_label.setText("Status: Not loaded")

            self.load_button.setEnabled(True)
            self.unload_button.setEnabled(False)
            self.execute_button.setEnabled(False)

    def clear_details(self) -> None:
        """Clear the details panel."""
        self.name_label.setText("Name: ")
        self.version_label.setText("Version: ")
        self.category_label.setText("Category: ")
        self.description_label.setText("Description: ")
        self.status_label.setText("Status: Not selected")

        self.load_button.setEnabled(False)
        self.unload_button.setEnabled(False)
        self.execute_button.setEnabled(False)

    @Slot()
    def on_load_clicked(self) -> None:
        """Handle load button click."""
        selected_items = self.tool_list.selectedItems()
        if not selected_items:
            return

        tool_name = selected_items[0].text()
        self.logger.info(f"Loading tool: {tool_name}")

        if self.tool_manager.load_tool(tool_name):
            self.update_details(tool_name)
            self.logger.info(f"Tool {tool_name} loaded successfully")
        else:
            self.logger.error(f"Failed to load tool: {tool_name}")
            QMessageBox.warning(
                self, "Load Failed", f"Failed to load tool: {tool_name}"
            )

    @Slot()
    def on_unload_clicked(self) -> None:
        """Handle unload button click."""
        selected_items = self.tool_list.selectedItems()
        if not selected_items:
            return

        tool_name = selected_items[0].text()
        self.logger.info(f"Unloading tool: {tool_name}")

        if self.tool_manager.unload_tool(tool_name):
            self.update_details(tool_name)
            self.logger.info(f"Tool {tool_name} unloaded successfully")
        else:
            self.logger.error(f"Failed to unload tool: {tool_name}")
            QMessageBox.warning(
                self, "Unload Failed", f"Failed to unload tool: {tool_name}"
            )

    @Slot()
    def on_execute_clicked(self) -> None:
        """Handle execute button click."""
        selected_items = self.tool_list.selectedItems()
        if not selected_items:
            return

        tool_name = selected_items[0].text()
        self.logger.info(f"Executing tool: {tool_name}")

        # For now, just emit the activation signal
        # Later we can add a dialog for tool parameters
        self.tool_activated.emit(tool_name)

        QMessageBox.information(
            self, "Tool Executed", f"Tool '{tool_name}' execution requested"
        )
