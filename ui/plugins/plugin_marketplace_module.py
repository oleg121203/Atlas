from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utils.logger import get_logger

logger = get_logger()


class PluginMarketplace(QWidget):
    """
    A module for discovering, installing, and updating plugins from a marketplace or repository.
    """

    plugin_installed = Signal(str)
    plugin_updated = Signal(str)

    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setObjectName("PluginMarketplace")
        self.init_ui()
        logger.info("Plugin Marketplace module initialized")

    def init_ui(self):
        """Initialize the user interface for the plugin marketplace."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Plugin Marketplace", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Search Bar
        search_layout = QVBoxLayout()
        search_label = QLabel("Search Plugins:", self)
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter plugin name or keyword...")
        self.search_input.textChanged.connect(self.search_plugins)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Plugin List
        self.plugin_list = QListWidget(self)
        self.plugin_list.setStyleSheet("margin: 10px; padding: 5px;")
        self.plugin_list.itemClicked.connect(self.on_plugin_selected)
        layout.addWidget(self.plugin_list)

        # Action Buttons
        button_layout = QVBoxLayout()
        self.install_button = QPushButton("Install Plugin", self)
        self.install_button.setEnabled(False)
        self.install_button.clicked.connect(self.install_plugin)
        self.update_button = QPushButton("Update Plugin", self)
        self.update_button.setEnabled(False)
        self.update_button.clicked.connect(self.update_plugin)
        button_layout.addWidget(self.install_button)
        button_layout.addWidget(self.update_button)
        layout.addLayout(button_layout)

        # Placeholder for initial plugin list
        self.populate_plugin_list([])

        self.setLayout(layout)

    def populate_plugin_list(self, plugins):
        """Populate the plugin list with available plugins from the marketplace."""
        self.plugin_list.clear()
        for plugin in plugins:
            item = QListWidgetItem(f"{plugin['name']} (v{plugin['version']})")
            item.setData(Qt.UserRole, plugin)
            self.plugin_list.addItem(item)
        if not plugins:
            item = QListWidgetItem(
                "No plugins available. Search for plugins or check your connection."
            )
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.plugin_list.addItem(item)

    def search_plugins(self, text):
        """Search for plugins based on user input. Placeholder for actual search functionality."""
        logger.debug(f"Searching for plugins with keyword: {text}")
        # Placeholder: In a real implementation, this would query a remote repository
        if text:
            mock_plugins = [
                {
                    "name": "Example Plugin",
                    "version": "1.0.0",
                    "description": "A sample plugin for testing.",
                },
                {
                    "name": f"{text} Plugin",
                    "version": "0.1.0",
                    "description": f"A plugin related to {text}.",
                },
            ]
            self.populate_plugin_list(mock_plugins)
        else:
            self.populate_plugin_list([])

    def on_plugin_selected(self, item):
        """Handle plugin selection from the list."""
        plugin_data = item.data(Qt.UserRole)
        if plugin_data:
            self.install_button.setEnabled(True)
            # Check if the plugin is already installed to enable update button
            plugin_name = plugin_data["name"]
            installed_plugins = self.plugin_manager.get_all_plugins()
            if plugin_name in installed_plugins:
                installed_version = installed_plugins[plugin_name]["metadata"].get(
                    "version", "0.0.0"
                )
                if self.plugin_manager._compare_version(
                    plugin_data["version"], f">{installed_version}"
                ):
                    self.update_button.setEnabled(True)
                else:
                    self.update_button.setEnabled(False)
            else:
                self.update_button.setEnabled(False)

    def install_plugin(self):
        """Install the selected plugin. Placeholder for actual installation."""
        selected_item = self.plugin_list.currentItem()
        if selected_item:
            plugin_data = selected_item.data(Qt.UserRole)
            if plugin_data:
                plugin_name = plugin_data["name"]
                logger.info(f"Installing plugin: {plugin_name}")
                # Placeholder for actual installation logic
                QMessageBox.information(
                    self,
                    "Plugin Installed",
                    f"Plugin {plugin_name} has been installed successfully.",
                )
                self.plugin_installed.emit(plugin_name)
                self.install_button.setEnabled(False)

    def update_plugin(self):
        """Update the selected plugin to the latest version. Placeholder for actual update."""
        selected_item = self.plugin_list.currentItem()
        if selected_item:
            plugin_data = selected_item.data(Qt.UserRole)
            if plugin_data:
                plugin_name = plugin_data["name"]
                logger.info(f"Updating plugin: {plugin_name}")
                # Placeholder for actual update logic
                QMessageBox.information(
                    self,
                    "Plugin Updated",
                    f"Plugin {plugin_name} has been updated to version {plugin_data['version']}.",
                )
                self.plugin_updated.emit(plugin_name)
                self.update_button.setEnabled(False)
