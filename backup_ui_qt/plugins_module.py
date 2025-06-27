from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.i18n import _
from ui.plugin_manager import PluginManager


class PluginsModule(QWidget):
    """Plugin management module with cyberpunk styling.

    Attributes:
        plugin_manager: Plugin manager instance
        tool_widgets: List of tool UI widgets
        list: QListWidget for plugins
        activate_btn: QPushButton for activating plugins
        deactivate_btn: QPushButton for deactivating plugins
        reload_btn: QPushButton for reloading plugins
        tools_frame: QFrame for plugin tools
        tools_layout: QVBoxLayout for tool widgets
        title: QLabel for module title
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the plugins module.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setObjectName("PluginsModule")
        self.plugin_manager: Optional[PluginManager] = None
        self.tool_widgets: List[QWidget] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.title = QLabel(_("🧩 Plugins"))
        self.title.setStyleSheet(
            "color: #ff00c8; font-size: 22px; font-weight: bold; letter-spacing: 1px;"
        )
        layout.addWidget(self.title)

        self.list = QListWidget()
        self.list.setDragEnabled(True)
        self.list.setDragDropMode(QAbstractItemView.InternalMove)
        self.list.setDefaultDropAction(Qt.MoveAction)
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.setStyleSheet(
            "background: #181c20; color: #fff; border: 1px solid #ff00c8; border-radius: 8px; font-size: 15px;"
        )
        layout.addWidget(self.list, stretch=1)

        btns = QHBoxLayout()
        self.activate_btn = QPushButton(_("Activate"))
        self.activate_btn.setStyleSheet(
            "background: #ff00c8; color: #181c20; font-weight: bold; border-radius: 6px; padding: 6px 18px;"
        )
        self.activate_btn.clicked.connect(self.activate_plugin)
        btns.addWidget(self.activate_btn)
        self.deactivate_btn = QPushButton(_("Deactivate"))
        self.deactivate_btn.setStyleSheet(
            "background: #23272e; color: #ff00c8; border-radius: 6px; padding: 6px 18px;"
        )
        self.deactivate_btn.clicked.connect(self.deactivate_plugin)
        btns.addWidget(self.deactivate_btn)
        self.reload_btn = QPushButton(_("Reload Plugins"))
        self.reload_btn.setStyleSheet(
            "background: #23272e; color: #ff00c8; border-radius: 6px; padding: 6px 18px; font-style: italic;"
        )
        self.reload_btn.clicked.connect(self.reload_plugins)
        btns.addWidget(self.reload_btn)
        layout.addLayout(btns)

        self.tools_frame = QFrame()
        self.tools_layout = QVBoxLayout(self.tools_frame)
        self.tools_layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.tools_frame)

    def update_ui(self) -> None:
        """Update UI elements with translated text."""
        self.title.setText(str(_("🧩 Plugins")) or "🧩 Plugins")
        self.activate_btn.setText(str(_("Activate")) or "Activate")
        self.deactivate_btn.setText(str(_("Deactivate")) or "Deactivate")
        self.reload_btn.setText(str(_("Reload Plugins")) or "Reload Plugins")

    def set_plugin_manager(self, plugin_manager: PluginManager) -> None:
        """Set the plugin manager instance.

        Args:
            plugin_manager: Plugin manager instance
        """
        self.plugin_manager = plugin_manager
        self.update_plugins()

    def update_plugins(self) -> None:
        """Update the list of plugins in the UI.

        Shows active/inactive status for each plugin.
        """
        self.list.clear()
        if not self.plugin_manager:
            return

        try:
            for name, plugin in self.plugin_manager.plugins.items():
                status = "(active)" if plugin.active else "(inactive)"
                self.list.addItem(f"{name} {status}")
            self.update_tools()
        except Exception as e:
            self.logger.error(f"Error updating plugins: {e}")

    def update_tools(self) -> None:
        """Update plugin tools in the UI.

        Removes old tools and adds new ones from active plugins.
        """
        # Remove old tools
        for widget in self.tool_widgets:
            widget.setParent(None)
        self.tool_widgets.clear()

        if not self.plugin_manager:
            return

        # Add tools from active plugins
        for plugin in self.plugin_manager.plugins.values():
            if plugin.active and hasattr(plugin, "get_widget"):
                try:
                    widget = plugin.get_widget(self)
                    if widget:
                        self.tools_layout.addWidget(widget)
                        self.tool_widgets.append(widget)
                except Exception as e:
                    self.logger.error(
                        f"Error adding widget for plugin {plugin.name}: {e}"
                    )
                    continue

    def activate_plugin(self) -> None:
        """Activate the selected plugin.

        Shows a warning if no plugin is selected.
        """
        row = self.list.currentRow()
        if row >= 0 and self.plugin_manager:
            try:
                name = self.list.item(row).text().split()[0]
                self.plugin_manager.activate_plugin(name)
                self.update_plugins()
            except Exception as e:
                QMessageBox.warning(
                    self,
                    str(_("Error")) or "Error",
                    f"{str(_('Failed to activate plugin:')) or 'Failed to activate plugin:'} {str(e)}",
                )
        else:
            QMessageBox.warning(
                self,
                str(_("Activate Plugin")) or "Activate Plugin",
                str(_("Select a plugin to activate."))
                or "Select a plugin to activate.",
            )

    def deactivate_plugin(self) -> None:
        """Deactivate the selected plugin.

        Shows a warning if no plugin is selected.
        """
        row = self.list.currentRow()
        if row >= 0 and self.plugin_manager:
            try:
                name = self.list.item(row).text().split()[0]
                self.plugin_manager.deactivate_plugin(name)
                self.update_plugins()
            except Exception as e:
                QMessageBox.warning(
                    self,
                    str(_("Error")) or "Error",
                    f"{str(_('Failed to deactivate plugin:')) or 'Failed to deactivate plugin:'} {str(e)}",
                )
        else:
            QMessageBox.warning(
                self,
                str(_("Deactivate Plugin")) or "Deactivate Plugin",
                str(_("Select a plugin to deactivate."))
                or "Select a plugin to deactivate.",
            )

    def reload_plugins(self) -> None:
        """Reload all plugins.

        Shows a message when complete.
        """
        if self.plugin_manager:
            try:
                self.plugin_manager.reload_all_plugins()
                self.update_plugins()
                QMessageBox.information(
                    self,
                    str(_("Reload Plugins")) or "Reload Plugins",
                    str(_("All plugins reloaded.")) or "All plugins reloaded.",
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    str(_("Error")) or "Error",
                    f"{str(_('Failed to reload plugins:')) or 'Failed to reload plugins:'} {str(e)}",
                )

    def search(self, query: str) -> List[Dict[str, str]]:
        """Search for plugins matching the query.

        Args:
            query: Search term

        Returns:
            List of dictionaries with 'label' and 'key' containing matching plugins
        """
        results: List[Dict[str, str]] = []
        if not self.plugin_manager:
            return results

        try:
            for plugin in self.plugin_manager.plugins.values():
                info = plugin.info()
                label = (
                    f"{info.get('name', plugin.name)}: {info.get('description', '')}"
                )
                if query.lower() in label.lower():
                    results.append({"label": label, "key": plugin.name})
        except Exception as e:
            self.logger.error(f"Error searching plugins: {e}")
        return results

    def select_by_key(self, key: str) -> None:
        """Select a plugin by its key.

        Args:
            key: Plugin key to select
        """
        for i in range(self.list.count()):
            try:
                name = self.list.item(i).text().split()[0]
                if name == key:
                    self.list.setCurrentRow(i)
                    self.list.scrollToItem(self.list.item(i))
                    break
            except Exception as e:
                self.logger.error(f"Error selecting plugin {i}: {e}")
                continue
