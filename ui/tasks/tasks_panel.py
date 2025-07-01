from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.event_bus import EventBus


class TasksPanel(QWidget):
    def __init__(
        self, parent=None, tasks=None, mode="flat", on_refresh=None, on_action=None
    ):
        super().__init__(parent)
        self.tasks = tasks or []
        self.mode = mode
        self.on_refresh = on_refresh
        self.on_action = on_action
        self.event_bus = EventBus()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Tasks")
        title.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin: 10px 0 5px 0; color: white;"
        )
        layout.addWidget(title)

        # Mode Selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("View Mode:")
        mode_label.setStyleSheet("color: white; margin-right: 10px;")
        mode_layout.addWidget(mode_label)
        self.mode_combobox = QComboBox()
        self.mode_combobox.addItems(["Flat List", "Hierarchical"])
        self.mode_combobox.setCurrentText(
            "Flat List" if self.mode == "flat" else "Hierarchical"
        )
        self.mode_combobox.currentTextChanged.connect(self._change_mode)
        self.mode_combobox.setStyleSheet(
            "background-color: #333; color: white; border: none; padding: 5px; margin-right: 10px;"
        )
        mode_layout.addWidget(self.mode_combobox)
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_tasks)
        refresh_button.setStyleSheet(
            "background-color: #444; color: white; border: none; padding: 5px;"
        )
        mode_layout.addWidget(refresh_button)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Task List
        self.task_list = QListWidget()
        self.task_list.setStyleSheet(
            "background-color: #333; color: white; border: none; padding: 5px;"
        )
        self.task_list.itemClicked.connect(self._task_selected)
        layout.addWidget(self.task_list)

        # Task Details
        self.task_details = QTextEdit()
        self.task_details.setReadOnly(True)
        self.task_details.setStyleSheet(
            "background-color: #333; color: white; border: none; padding: 5px; margin: 5px 0;"
        )
        self.task_details.setMinimumHeight(100)
        layout.addWidget(self.task_details)

        # Action Buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self.action_button = QPushButton("Take Action")
        self.action_button.clicked.connect(self._take_action)
        self.action_button.setStyleSheet(
            "background-color: #444; color: white; border: none; padding: 5px; margin-right: 5px;"
        )
        action_layout.addWidget(self.action_button)
        layout.addLayout(action_layout)

        self.setLayout(layout)
        self._update_task_list()

    def _change_mode(self, mode_text):
        self.mode = "flat" if mode_text == "Flat List" else "hierarchical"
        self._update_task_list()

    def _refresh_tasks(self):
        if self.on_refresh:
            self.on_refresh()
        self._update_task_list()

    def _update_task_list(self):
        self.task_list.clear()
        if not self.tasks:
            self.task_list.addItem("No tasks available")
            return

        if self.mode == "flat":
            for task in self.tasks:
                self.task_list.addItem(task.get("title", "Unnamed Task"))
        else:
            # TODO: Implement hierarchical view
            self.task_list.addItem("Hierarchical view not yet implemented")

    def _task_selected(self, item):
        index = self.task_list.row(item)
        if index >= 0 and index < len(self.tasks):
            task = self.tasks[index]
            details = f"Title: {task.get('title', 'Unnamed Task')}\n"
            details += f"Status: {task.get('status', 'Unknown')}\n"
            details += f"Description: {task.get('description', 'No description')}\n"
            self.task_details.setText(details)
        else:
            self.task_details.setText("No task selected or invalid selection")

    def _take_action(self):
        current_item = self.task_list.currentItem()
        if current_item:
            index = self.task_list.row(current_item)
            if index >= 0 and index < len(self.tasks) and self.on_action:
                self.on_action(self.tasks[index])
