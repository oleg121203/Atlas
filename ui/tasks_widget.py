"""
Tasks widget for the Atlas application.

This module provides the UI component for task management, including
input validation and sanitization for task creation and modification.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

from ui.input_validation import validate_ui_input, sanitize_ui_input
from core.logging import get_logger

logger = get_logger("TasksWidget")

class TasksWidget(QWidget):
    """Task management interface widget for Atlas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        logger.info("Tasks widget initialized")
    
    def init_ui(self) -> None:
        """Initialize UI components for the tasks widget."""
        layout = QVBoxLayout(self)
        
        # Task list
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)
        
        # Input area for new tasks
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter new task...")
        self.task_input.returnPressed.connect(self.add_task)
        input_layout.addWidget(self.task_input)
        
        add_button = QPushButton("Add Task")
        add_button.clicked.connect(self.add_task)
        input_layout.addWidget(add_button)
        
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
            # Display error to user (could be improved with a proper error display mechanism)
            self.task_input.setPlaceholderText(error_msg)
            return
        
        # Sanitize input
        sanitized_task = sanitize_ui_input(task_text)
        logger.debug("Task sanitized, original: %s, sanitized: %s", task_text, sanitized_task)
        
        # Add the sanitized task to the list
        item = QListWidgetItem(sanitized_task)
        self.task_list.addItem(item)
        self.task_input.clear()
        
        # TODO: Implement actual task creation logic
        logger.info("Task added: %s", sanitized_task)
    
    def remove_task(self, item: QListWidgetItem) -> None:
        """
        Remove a task from the list.
        
        Args:
            item: QListWidgetItem to remove
        """
        self.task_list.takeItem(self.task_list.row(item))
        logger.info("Task removed")
