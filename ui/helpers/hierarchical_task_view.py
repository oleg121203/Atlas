"""Hierarchical Task View component for Atlas."""

import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget


class HierarchicalTaskView(QWidget):
    """Hierarchical view for tasks in Atlas with cyberpunk styling."""

    task_selected = Signal(str)
    task_activated = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #0a0a0a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        self.initialize_ui()
        self.logger.info("HierarchicalTaskView component initialized")

    def initialize_ui(self) -> None:
        """Initialize the UI components for the hierarchical task view."""
        layout = QVBoxLayout(self)

        header_label = QLabel("Task Hierarchy")
        header_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #00ffaa;"
        )
        layout.addWidget(header_label)

        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["Task", "Status", "Priority"])
        self.task_tree.itemClicked.connect(self.on_task_selected)
        self.task_tree.itemDoubleClicked.connect(self.on_task_activated)
        layout.addWidget(self.task_tree)

        self.setLayout(layout)

    def update_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """Update the hierarchical task view with the provided tasks.

        Args:
            tasks (List[Dict[str, Any]]): List of task dictionaries with hierarchical structure.
        """
        self.task_tree.clear()
        self._populate_tasks(tasks, None)
        self.logger.debug(f"Updated task view with {len(tasks)} top-level tasks")

    def _populate_tasks(
        self, tasks: List[Dict[str, Any]], parent: Optional[QTreeWidgetItem]
    ) -> None:
        """Recursively populate the task tree with tasks and subtasks.

        Args:
            tasks (List[Dict[str, Any]]): List of task dictionaries.
            parent (Optional[QTreeWidgetItem]): Parent item for the tasks, None for top-level.
        """
        for task in tasks:
            task_name = task.get("name", "Unnamed Task")
            task_status = task.get("status", "Unknown")
            task_priority = task.get("priority", "Normal")
            item = QTreeWidgetItem([task_name, task_status, task_priority])
            item.setData(0, Qt.ItemDataRole.UserRole, task.get("id", task_name))
            if parent is None:
                self.task_tree.addTopLevelItem(item)
            else:
                parent.addChild(item)
            subtasks = task.get("subtasks", [])
            if subtasks:
                self._populate_tasks(subtasks, item)
            self.logger.debug(f"Added task to tree: {task_name}")

    @Slot(QTreeWidgetItem, int)
    def on_task_selected(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle task selection event.

        Args:
            item (QTreeWidgetItem): The selected item.
            column (int): The column clicked.
        """
        task_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.task_selected.emit(task_id)
        self.logger.info(f"Selected task: {task_id}")

    @Slot(QTreeWidgetItem, int)
    def on_task_activated(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle task activation event (double-click).

        Args:
            item (QTreeWidgetItem): The activated item.
            column (int): The column double-clicked.
        """
        task_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.task_activated.emit(task_id)
        self.logger.info(f"Activated task: {task_id}")
