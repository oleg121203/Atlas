"""Plugin Manager UI for Atlas."""

import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from plugins.plugin_manager import PluginManager


class PluginManagerUI(QWidget):
    """UI component for managing plugins in Atlas."""

    plugin_selected = Signal(str)
    plugin_activated = Signal(str)
    plugin_deactivated = Signal(str)

    def __init__(self, plugin_manager: PluginManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.plugin_manager = plugin_manager
        self.setup_ui()
        self.connect_signals()
        self.logger.info("PluginManagerUI initialized")

    def setup_ui(self) -> None:
        """Set up the user interface for plugin management."""
        # Main layout
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Left panel - Plugin list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setLayout(left_layout)

        list_group = QGroupBox("Plugins")
        list_layout = QVBoxLayout(list_group)
        list_group.setLayout(list_layout)

        self.plugin_list = QListWidget()
        self.plugin_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        list_layout.addWidget(self.plugin_list)

        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.load_button = QPushButton("Load All")
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.load_button)
        list_layout.addLayout(button_layout)

        left_layout.addWidget(list_group)
        left_layout.addStretch()

        # Right panel - Plugin details and controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setLayout(right_layout)

        details_group = QGroupBox("Plugin Details")
        details_layout = QVBoxLayout(details_group)
        details_group.setLayout(details_layout)

        self.name_label = QLabel("Name: ")
        self.version_label = QLabel("Version: ")
        self.author_label = QLabel("Author: ")
        self.description_label = QLabel("Description: ")
        self.status_label = QLabel("Status: Not loaded")

        details_layout.addWidget(self.name_label)
        details_layout.addWidget(self.version_label)
        details_layout.addWidget(self.author_label)
        details_layout.addWidget(self.description_label)
        details_layout.addWidget(self.status_label)
        details_layout.addStretch()

        control_layout = QHBoxLayout()
        self.activate_button = QPushButton("Activate")
        self.deactivate_button = QPushButton("Deactivate")
        self.deactivate_button.setEnabled(False)
        control_layout.addWidget(self.activate_button)
        control_layout.addWidget(self.deactivate_button)
        details_layout.addLayout(control_layout)

        right_layout.addWidget(details_group)
        right_layout.addStretch()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 400])

        self.setMinimumSize(600, 400)
        self.logger.debug("PluginManagerUI setup completed")

    def connect_signals(self) -> None:
        """Connect signals for plugin management UI."""
        self.refresh_button.clicked.connect(self.refresh_plugins)
        self.load_button.clicked.connect(self.load_all_plugins)
        self.plugin_list.itemSelectionChanged.connect(self.on_plugin_selected)
        self.activate_button.clicked.connect(self.on_activate_clicked)
        self.deactivate_button.clicked.connect(self.on_deactivate_clicked)
        self.plugin_manager.plugins_loaded.connect(self.on_plugins_loaded)
        self.plugin_manager.plugin_status_changed.connect(self.on_plugin_status_changed)
        self.logger.debug("PluginManagerUI signals connected")

    @Slot()
    def refresh_plugins(self) -> None:
        """Refresh the list of available plugins."""
        self.logger.info("Refreshing plugin list")
        self.plugin_list.clear()
        plugin_ids = self.plugin_manager.discover_plugins()
        for plugin_id in plugin_ids:
            item = QListWidgetItem(plugin_id)
            item.setData(Qt.ItemDataRole.UserRole, plugin_id)
            self.plugin_list.addItem(item)
        self.logger.info(f"Discovered {len(plugin_ids)} plugins")

    @Slot()
    def load_all_plugins(self) -> None:
        """Load all available plugins."""
        self.logger.info("Loading all plugins")
        self.plugin_manager.load_plugins()
        self.refresh_plugins()

    @Slot(list)
    def on_plugins_loaded(self, metadata_list: List[Dict[str, Any]]) -> None:
        """Handle plugins loaded event.

        Args:
            metadata_list (List[Dict[str, Any]]): List of metadata for loaded plugins.
        """
        self.logger.info(
            f"Received plugins loaded event with {len(metadata_list)} plugins"
        )
        self.plugin_list.clear()
        for metadata in metadata_list:
            plugin_id = metadata.get("id", "Unknown")
            item = QListWidgetItem(plugin_id)
            item.setData(Qt.ItemDataRole.UserRole, plugin_id)
            self.plugin_list.addItem(item)
        self.logger.debug("Updated plugin list UI after plugins loaded")

    @Slot()
    def on_plugin_selected(self) -> None:
        """Handle plugin selection in the list."""
        selected_items = self.plugin_list.selectedItems()
        if not selected_items:
            self.clear_details()
            return

        item = selected_items[0]
        plugin_id = item.data(Qt.ItemDataRole.UserRole)
        self.logger.info(f"Plugin selected: {plugin_id}")
        self.plugin_selected.emit(plugin_id)
        self.update_details(plugin_id)

    def update_details(self, plugin_id: str) -> None:
        """Update the details panel for the selected plugin.

        Args:
            plugin_id (str): ID of the selected plugin.
        """
        metadata = self.plugin_manager.get_plugin_metadata(plugin_id)
        if not metadata:
            self.clear_details()
            return

        self.name_label.setText(f"Name: {metadata.get('name', 'Unknown')}")
        self.version_label.setText(f"Version: {metadata.get('version', 'Unknown')}")
        self.author_label.setText(f"Author: {metadata.get('author', 'Unknown')}")
        self.description_label.setText(
            f"Description: {metadata.get('description', 'No description')}"
        )

        plugin = self.plugin_manager.get_plugin(plugin_id)
        if plugin:
            self.status_label.setText(
                f"Status: {'Active' if plugin.is_active else 'Inactive'}"
            )
            self.activate_button.setEnabled(not plugin.is_active)
            self.deactivate_button.setEnabled(plugin.is_active)
        else:
            self.status_label.setText("Status: Not loaded")
            self.activate_button.setEnabled(False)
            self.deactivate_button.setEnabled(False)

        self.logger.debug(f"Updated details for plugin: {plugin_id}")

    def clear_details(self) -> None:
        """Clear the details panel."""
        self.name_label.setText("Name: ")
        self.version_label.setText("Version: ")
        self.author_label.setText("Author: ")
        self.description_label.setText("Description: ")
        self.status_label.setText("Status: Not loaded")
        self.activate_button.setEnabled(False)
        self.deactivate_button.setEnabled(False)
        self.logger.debug("Cleared plugin details")

    @Slot()
    def on_activate_clicked(self) -> None:
        """Handle activate button click."""
        selected_items = self.plugin_list.selectedItems()
        if not selected_items:
            return

        plugin_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.logger.info(f"Activating plugin: {plugin_id}")
        plugin = self.plugin_manager.get_plugin(plugin_id)
        if plugin and not plugin.is_active:
            if plugin.initialize():
                self.plugin_activated.emit(plugin_id)
                self.update_details(plugin_id)
                self.logger.info(f"Plugin {plugin_id} activated successfully")
            else:
                self.logger.error(f"Failed to activate plugin: {plugin_id}")
        else:
            self.logger.warning(f"Plugin {plugin_id} not found or already active")

    @Slot()
    def on_deactivate_clicked(self) -> None:
        """Handle deactivate button click."""
        selected_items = self.plugin_list.selectedItems()
        if not selected_items:
            return

        plugin_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.logger.info(f"Deactivating plugin: {plugin_id}")
        plugin = self.plugin_manager.get_plugin(plugin_id)
        if plugin and plugin.is_active:
            plugin.shutdown()
            self.plugin_deactivated.emit(plugin_id)
            self.update_details(plugin_id)
            self.logger.info(f"Plugin {plugin_id} deactivated")
        else:
            self.logger.warning(f"Plugin {plugin_id} not found or already inactive")

    @Slot(str, str)
    def on_plugin_status_changed(self, plugin_id: str, status: str) -> None:
        """Handle plugin status change event.

        Args:
            plugin_id (str): ID of the plugin.
            status (str): New status of the plugin.
        """
        self.logger.info(f"Plugin status changed: {plugin_id} - {status}")
        selected_items = self.plugin_list.selectedItems()
        if (
            selected_items
            and selected_items[0].data(Qt.ItemDataRole.UserRole) == plugin_id
        ):
            self.update_details(plugin_id)
        self.logger.debug(f"Updated UI for plugin status change: {plugin_id}")
