from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QInputDialog, QMessageBox, QFrame
from ui_qt.i18n import _

class TasksModule(QWidget):
    """Tasks management module with cyberpunk styling.

    Attributes:
        plugin_manager: Plugin manager instance
        tool_widgets: List of tool UI widgets
        list: QListWidget for tasks
        add_btn: QPushButton for adding tasks
        del_btn: QPushButton for deleting tasks
        tools_frame: QFrame for plugin tools
        tools_layout: QVBoxLayout for tool widgets
        title: QLabel for module title
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the tasks module.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setObjectName("TasksModule")
        self.plugin_manager: Optional[PluginManager] = None
        self.tool_widgets: List[QWidget] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.title = QLabel(_("📋 Tasks (Cyberpunk)"))
        self.title.setStyleSheet("color: #ff00a0; font-size: 22px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(self.title)

        self.list = QListWidget()
        self.list.setStyleSheet("background: #181c20; color: #fff; border: 1px solid #ff00a0; border-radius: 8px; font-size: 15px;")
        self.list.setDragDropMode(self.list.InternalMove)
        layout.addWidget(self.list, stretch=1)

        btns = QHBoxLayout()
        self.add_btn = QPushButton(_("Add Task"))
        self.add_btn.setStyleSheet("background: #ff00a0; color: #181c20; font-weight: bold; border-radius: 6px; padding: 6px 18px;")
        self.add_btn.clicked.connect(self.add_task)
        btns.addWidget(self.add_btn)
        self.del_btn = QPushButton(_("Delete Task"))
        self.del_btn.setStyleSheet("background: #23272e; color: #ff00a0; border-radius: 6px; padding: 6px 18px;")
        self.del_btn.clicked.connect(self.delete_task)
        btns.addWidget(self.del_btn)
        layout.addLayout(btns)

        self.tools_frame = QFrame()
        self.tools_layout = QVBoxLayout(self.tools_frame)
        self.tools_layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.tools_frame)

    def update_ui(self) -> None:
        """Update UI elements with translated text."""
        self.title.setText(str(_("📋 Tasks (Cyberpunk)")) or "📋 Tasks (Cyberpunk)")
        self.add_btn.setText(str(_("Add Task")) or "Add Task")
        self.del_btn.setText(str(_("Delete Task")) or "Delete Task")

    def set_plugin_manager(self, plugin_manager: PluginManager) -> None:
        """Set the plugin manager instance.

        Args:
            plugin_manager: Plugin manager instance
        """
        self.plugin_manager = plugin_manager
        self.update_tools()

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
            if plugin.active:
                widget = plugin.get_widget(self)
                if widget:
                    self.tools_layout.addWidget(widget)
                    self.tool_widgets.append(widget)

    def add_task(self) -> None:
        """Add a new task to the list.

        Opens a dialog to get task name and adds it to the list.
        """
        text, ok = QInputDialog.getText(
            self,
            str(_("Add Task")) or "Add Task",
            str(_("Task name:")) or "Task name:"
        )
        if ok and text:
            try:
                self.list.addItem(text)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    str(_("Error")) or "Error",
                    f"{str(_("Failed to add task:")) or 'Failed to add task:'} {str(e)}"
                )

    def delete_task(self) -> None:
        """Delete the selected task.

        Shows a warning if no task is selected.
        """
        row = self.list.currentRow()
        if row >= 0:
            try:
                self.list.takeItem(row)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    str(_("Error")) or "Error",
                    f"{str(_("Failed to delete task:")) or 'Failed to delete task:'} {str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                str(_("Delete Task")) or "Delete Task",
                str(_("Select a task to delete.")) or "Select a task to delete."
            )

    def search(self, query: str) -> List[Dict[str, str]]:
        """Search for tasks containing the query.

        Args:
            query: Search term

        Returns:
            List of dictionaries with 'label' and 'key' containing matching tasks
        """
        results: List[Dict[str, str]] = []
        for i in range(self.list.count()):
            try:
                text = self.list.item(i).text()
                if query.lower() in text.lower():
                    results.append({
                        'label': text,
                        'key': text
                    })
            except Exception as e:
                self.logger.error(f"Error searching task {i}: {e}")
                continue
        return results

    def select_by_key(self, key: str) -> None:
        """Select a task by its key.

        Args:
            key: Task key to select
        """
        for i in range(self.list.count()):
            try:
                if self.list.item(i).text() == key:
                    self.list.setCurrentRow(i)
                    self.list.scrollToItem(self.list.item(i))
                    break
            except Exception as e:
                self.logger.error(f"Error selecting task {i}: {e}")
                continue