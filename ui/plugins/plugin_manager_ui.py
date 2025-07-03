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

from core.plugin_system import PluginSystem
from ui.module_communication import EVENT_BUS


class PluginManagerUI(QWidget):
    """UI component for managing plugins in Atlas."""

    plugin_selected = Signal(str)
    plugin_activated = Signal(str)
    plugin_deactivated = Signal(str)

    def __init__(self, plugin_system: PluginSystem, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.plugin_system = plugin_system
        self.event_bus = EVENT_BUS
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

        # Connect to event bus if available
        if self.event_bus:
            self.event_bus.subscribe("plugin_loaded", self._on_plugin_event)
            self.event_bus.subscribe("plugin_unloaded", self._on_plugin_event)
            self.event_bus.subscribe("plugin_activated", self._on_plugin_event)
            self.event_bus.subscribe("plugin_deactivated", self._on_plugin_event)

        self.logger.debug("PluginManagerUI signals connected")

    @Slot()
    def refresh_plugins(self) -> None:
        """Refresh the list of available plugins."""
        self.logger.info("Refreshing plugin list")
        self.plugin_list.clear()

        # Get list of loaded plugins
        plugin_names = self.plugin_system.list_plugins()

        # Also discover available plugins that might not be loaded
        discovered_plugins = self.plugin_system.registry.discover_plugins()
        all_plugins = list(set(plugin_names + discovered_plugins))

        for plugin_name in all_plugins:
            item = QListWidgetItem(plugin_name)
            item.setData(Qt.ItemDataRole.UserRole, plugin_name)
            self.plugin_list.addItem(item)

        self.logger.info(f"Refreshed plugin list with {len(all_plugins)} plugins")

    @Slot()
    def load_all_plugins(self) -> None:
        """Load all available plugins."""
        self.logger.info("Loading all plugins")

        # Discover and load all plugins
        discovered_plugins = self.plugin_system.registry.discover_plugins()
        for plugin_name in discovered_plugins:
            self.plugin_system.load_plugin(plugin_name)

        self.refresh_plugins()

    def _on_plugin_event(self, event_data: Dict[str, Any]) -> None:
        """Handle plugin events from the event bus."""
        plugin_name = event_data.get("plugin_name", "")
        self.logger.debug(f"Plugin event received for: {plugin_name}")

        # Refresh the display for the current selection
        selected_items = self.plugin_list.selectedItems()
        if (
            selected_items
            and selected_items[0].data(Qt.ItemDataRole.UserRole) == plugin_name
        ):
            self.update_details(plugin_name)

        # Also refresh the list in case new plugins were discovered
        self.refresh_plugins()

    @Slot(list)
    def on_plugins_loaded(self, metadata_list: List[Dict[str, Any]]) -> None:
        """Handle plugins loaded event - deprecated in new system."""
        # This method is kept for backward compatibility but uses new API
        self.refresh_plugins()

    @Slot()
    def on_plugin_selected(self) -> None:
        """Handle plugin selection in the list."""
        selected_items = self.plugin_list.selectedItems()
        if not selected_items:
            self.clear_details()
            return

        item = selected_items[0]
        plugin_name = item.data(Qt.ItemDataRole.UserRole)
        self.logger.info(f"Plugin selected: {plugin_name}")
        self.plugin_selected.emit(plugin_name)
        self.update_details(plugin_name)

    def update_details(self, plugin_name: str) -> None:
        """Update the details panel for the selected plugin."""
        # Get plugin status from the plugin system
        status_info = self.plugin_system.get_plugin_status(plugin_name)

        if status_info["status"] == "not_loaded":
            self.name_label.setText(f"Name: {plugin_name}")
            self.version_label.setText("Version: Unknown")
            self.author_label.setText("Author: Unknown")
            self.description_label.setText("Description: Plugin not loaded")
            self.status_label.setText("Status: Not loaded")
            self.activate_button.setEnabled(False)
            self.deactivate_button.setEnabled(False)
        else:
            plugin = self.plugin_system.get_plugin(plugin_name)
            if plugin:
                metadata = plugin.get_metadata()
                self.name_label.setText(f"Name: {metadata.get('name', plugin_name)}")
                self.version_label.setText(
                    f"Version: {metadata.get('version', 'Unknown')}"
                )
                self.author_label.setText(
                    f"Author: {metadata.get('author', 'Unknown')}"
                )
                self.description_label.setText(
                    f"Description: {metadata.get('description', 'No description')}"
                )

                is_active = status_info["active"]
                self.status_label.setText(
                    f"Status: {'Active' if is_active else 'Loaded'}"
                )
                self.activate_button.setEnabled(not is_active)
                self.deactivate_button.setEnabled(is_active)
            else:
                self.clear_details()

        self.logger.debug(f"Updated details for plugin: {plugin_name}")

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

        plugin_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.logger.info(f"Activating plugin: {plugin_name}")

        # Load plugin if not loaded
        if (
            plugin_name not in self.plugin_system.list_plugins()
            and not self.plugin_system.load_plugin(plugin_name)
        ):
            self.logger.error(f"Failed to load plugin: {plugin_name}")
            return

        # Activate the plugin
        if self.plugin_system.activate_plugin(plugin_name):
            self.plugin_activated.emit(plugin_name)
            self.update_details(plugin_name)
            self.logger.info(f"Plugin {plugin_name} activated successfully")
        else:
            self.logger.error(f"Failed to activate plugin: {plugin_name}")

    @Slot()
    def on_deactivate_clicked(self) -> None:
        """Handle deactivate button click."""
        selected_items = self.plugin_list.selectedItems()
        if not selected_items:
            return

        plugin_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.logger.info(f"Deactivating plugin: {plugin_name}")

        if self.plugin_system.deactivate_plugin(plugin_name):
            self.plugin_deactivated.emit(plugin_name)
            self.update_details(plugin_name)
            self.logger.info(f"Plugin {plugin_name} deactivated")
        else:
            self.logger.error(f"Failed to deactivate plugin: {plugin_name}")

    @Slot(str, str)
    def on_plugin_status_changed(self, plugin_name: str, status: str) -> None:
        """Handle plugin status change event - deprecated in new system."""
        # This method is kept for backward compatibility
        # The new system uses event bus events instead
        self._on_plugin_event({"plugin_name": plugin_name, "status": status})
