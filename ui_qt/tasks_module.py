from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QInputDialog, QMessageBox, QFrame
from PySide6.QtCore import Qt
from ui_qt.i18n import _

class TasksModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TasksModule")
        self.plugin_manager = None
        self.tool_widgets = []
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

    def update_ui(self):
        self.title.setText(_("📋 Tasks (Cyberpunk)"))
        self.add_btn.setText(_("Add Task"))
        self.del_btn.setText(_("Delete Task"))

    def set_plugin_manager(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.update_tools()

    def update_tools(self):
        # Очистити старі тулси
        for w in self.tool_widgets:
            w.setParent(None)
        self.tool_widgets.clear()
        if not self.plugin_manager:
            return
        for name, plugin in self.plugin_manager.plugins.items():
            if plugin.active:
                widget = plugin.get_widget(self)
                if widget:
                    self.tools_layout.addWidget(widget)
                    self.tool_widgets.append(widget)

    def add_task(self):
        text, ok = QInputDialog.getText(self, _( "Add Task"), _( "Task name:"))
        if ok and text:
            self.list.addItem(text)

    def delete_task(self):
        row = self.list.currentRow()
        if row >= 0:
            self.list.takeItem(row)
        else:
            QMessageBox.warning(self, _( "Delete Task"), _( "Select a task to delete."))

    def search(self, query):
        """Повертає список словників: {'label': текст задачі, 'key': текст задачі}"""
        results = []
        for i in range(self.list.count()):
            text = self.list.item(i).text()
            if query.lower() in text.lower():
                results.append({'label': text, 'key': text})
        return results

    def select_by_key(self, key):
        for i in range(self.list.count()):
            if self.list.item(i).text() == key:
                self.list.setCurrentRow(i)
                self.list.scrollToItem(self.list.item(i))
                break 