"""
Tasfrom datetime import datetime
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.logging import get_logger
from ui.input_validation import sanitize_ui_input, validate_ui_inputhe Atlas application.

This module provides the UI component for task management, including
task creation, monitoring, and status updates.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.logging import get_logger
from ui.input_validation import sanitize_ui_input, validate_ui_input

logger = get_logger("TasksWidget")


class TasksWidget(QWidget):
    """Task management interface widget for Atlas."""

    task_created = Signal(dict)  # Emitted when a new task is created
    task_cancelled = Signal(str)  # Emitted when a task is cancelled

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        logger.info("Tasks widget initialized")
        self._task_counter = 0

    def init_ui(self) -> None:
        """Initialize UI components for the tasks widget."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Tasks")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ffaa;")
        layout.addWidget(header)

        # Tasks list with cyberpunk styling
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        layout.addWidget(self.task_list)

        # Input area for new tasks
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter new task...")
        self.task_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        self.task_input.returnPressed.connect(self.add_task)
        input_layout.addWidget(self.task_input)

        # Add button with cyberpunk styling
        add_button = QPushButton("Add Task")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        add_button.clicked.connect(self.add_task)
        input_layout.addWidget(add_button)

        # Cancel button
        cancel_button = QPushButton("Cancel Task")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #ff5555;
                border: 1px solid #ff5555;
                border-radius: 3px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #ff5555;
                color: #000000;
            }
        """)
        cancel_button.clicked.connect(self.cancel_selected_task)
        input_layout.addWidget(cancel_button)

        layout.addLayout(input_layout)

    def add_task(self) -> None:
        """Handle adding a new task with validation and sanitization."""
        task_text = self.task_input.text().strip()
        if not task_text:
            return

        # Validate input
        is_valid, error_msg = validate_ui_input(task_text, "text", "Task")
        if not is_valid:
            logger.warning("Invalid task input: %s", error_msg)
            self.task_input.setPlaceholderText(error_msg)
            return

        # Sanitize input
        sanitized_task = sanitize_ui_input(task_text)
        logger.debug(
            "Task input sanitized, original: %s, sanitized: %s",
            task_text,
            sanitized_task,
        )

        # Create task data
        self._task_counter += 1
        task = {
            "id": f"task_{self._task_counter}",
            "name": sanitized_task,
            "type": "default",
            "description": sanitized_task,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }

        # Add to UI and emit signal
        self.add_task_to_list(task)
        self.task_created.emit(task)
        self.task_input.clear()
        logger.info("Task created: %s", task["id"])

    def add_task_to_list(self, task: Dict[str, Any]) -> None:
        """Add a task to the list widget with proper display."""
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, task["id"])
        item.setData(Qt.ItemDataRole.UserRole + 1, task)
        self._update_task_display(item, task)
        self.task_list.addItem(item)

    def update_task_status(
        self, task_id: str, status: str, result: Optional[Dict] = None
    ) -> None:
        """Update the status and optionally the result of a task in the list."""
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == task_id:
                task_data = item.data(Qt.ItemDataRole.UserRole + 1)
                if isinstance(task_data, dict):
                    task_data["status"] = status
                    if result:
                        task_data["result"] = result
                    self._update_task_display(item, task_data)
                break

    def cancel_selected_task(self) -> None:
        """Cancel the currently selected task."""
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        task_id = item.data(Qt.ItemDataRole.UserRole)
        self.task_cancelled.emit(task_id)

        # Update task status
        task_data = item.data(Qt.ItemDataRole.UserRole + 1)
        if isinstance(task_data, dict):
            task_data["status"] = "cancelled"
            self._update_task_display(item, task_data)
        logger.info("Task cancelled: %s", task_id)

    def _update_task_display(self, item: QListWidgetItem, task: Dict[str, Any]) -> None:
        """Update the display text and style of a task item."""
        status = task.get("status", "pending")

        # Set text
        item.setText(f"{task['name']} [{status}]")

        # Set color based on status
        if status == "in_progress":
            item.setForeground(Qt.GlobalColor.cyan)
        elif status == "completed":
            item.setForeground(Qt.GlobalColor.green)
        elif status in ("failed", "cancelled"):
            item.setForeground(Qt.GlobalColor.red)
        else:  # pending
            item.setForeground(Qt.GlobalColor.white)
