# Basic implementation of task_widget.py for Atlas UI

from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class TaskWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TaskWidget")
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for managing tasks."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Task Management")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Table for displaying tasks
        self.task_table = QTableWidget()
        self.task_table.setRowCount(0)
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(["Task Name", "Description", "Status", "Due Date", "Actions"])
        self.task_table.setStyleSheet("border: 1px solid #404040; alternate-background-color: #303030;")
        self.task_table.setAlternatingRowColors(True)
        self.task_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.task_table)

        # Form for adding new tasks
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)

        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("Task Name")
        self.task_name_input.setStyleSheet("padding: 5px; border: 1px solid #404040; background-color: #202020; color: #ffffff;")
        form_layout.addWidget(self.task_name_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description")
        self.description_input.setStyleSheet("padding: 5px; border: 1px solid #404040; background-color: #202020; color: #ffffff;")
        form_layout.addWidget(self.description_input)

        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_label = QLabel("Status:")
        status_label.setStyleSheet("color: #ffffff;")
        self.status_input = QComboBox()
        self.status_input.addItems(["Not Started", "In Progress", "Completed"])
        self.status_input.setStyleSheet("padding: 5px; border: 1px solid #404040; background-color: #202020; color: #ffffff;")
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_input)
        status_layout.addStretch()
        status_widget.setLayout(status_layout)
        form_layout.addWidget(status_widget)

        due_date_widget = QWidget()
        due_date_layout = QHBoxLayout(due_date_widget)
        due_date_label = QLabel("Due Date:")
        due_date_label.setStyleSheet("color: #ffffff;")
        self.due_date_input = QDateTimeEdit()
        self.due_date_input.setDateTime(QDateTime.currentDateTime().addDays(7))
        self.due_date_input.setStyleSheet("padding: 5px; border: 1px solid #404040; background-color: #202020; color: #ffffff;")
        due_date_layout.addWidget(due_date_label)
        due_date_layout.addWidget(self.due_date_input)
        due_date_layout.addStretch()
        due_date_widget.setLayout(due_date_layout)
        form_layout.addWidget(due_date_widget)

        add_button = QPushButton("Add Task")
        add_button.setStyleSheet("background-color: #007BFF; color: white; border: none; padding: 8px; font-weight: bold;")
        add_button.clicked.connect(self.add_task)
        form_layout.addWidget(add_button)

        layout.addWidget(form_widget)
        self.setLayout(layout)
        self.populate_table()

    def populate_table(self):
        """Populate the task table with sample data (to be replaced with real data)."""
        self.task_table.setRowCount(0)
        sample_tasks = [
            ("Implement UI", "Finish PySide6 integration", "In Progress", QDateTime.currentDateTime().addDays(3).toString("yyyy-MM-dd hh:mm")),
            ("Database Optimization", "Improve query performance", "Not Started", QDateTime.currentDateTime().addDays(10).toString("yyyy-MM-dd hh:mm")),
            ("Bug Fixing", "Resolve critical bugs", "Completed", QDateTime.currentDateTime().addDays(-2).toString("yyyy-MM-dd hh:mm"))
        ]

        for task_name, description, status, due_date in sample_tasks:
            row_position = self.task_table.rowCount()
            self.task_table.insertRow(row_position)
            self.task_table.setItem(row_position, 0, QTableWidgetItem(task_name))
            self.task_table.setItem(row_position, 1, QTableWidgetItem(description))
            self.task_table.setItem(row_position, 2, QTableWidgetItem(status))
            self.task_table.setItem(row_position, 3, QTableWidgetItem(due_date))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("background-color: #ffc107; color: black; border: none; padding: 3px 6px;")
            edit_btn.clicked.connect(lambda checked, t=task_name: self.edit_task(t))
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #dc3545; color: white; border: none; padding: 3px 6px;")
            delete_btn.clicked.connect(lambda checked, t=task_name: self.delete_task(t))
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addStretch()
            action_widget.setLayout(action_layout)
            self.task_table.setCellWidget(row_position, 4, action_widget)

    def add_task(self):
        """Add a new task to the table."""
        task_name = self.task_name_input.text().strip()
        description = self.description_input.text().strip()
        status = self.status_input.currentText()
        due_date = self.due_date_input.dateTime().toString("yyyy-MM-dd hh:mm")

        if not task_name:
            QMessageBox.warning(self, "Invalid Input", "Task Name cannot be empty.")
            return

        row_position = self.task_table.rowCount()
        self.task_table.insertRow(row_position)
        self.task_table.setItem(row_position, 0, QTableWidgetItem(task_name))
        self.task_table.setItem(row_position, 1, QTableWidgetItem(description))
        self.task_table.setItem(row_position, 2, QTableWidgetItem(status))
        self.task_table.setItem(row_position, 3, QTableWidgetItem(due_date))

        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet("background-color: #ffc107; color: black; border: none; padding: 3px 6px;")
        edit_btn.clicked.connect(lambda checked, t=task_name: self.edit_task(t))
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("background-color: #dc3545; color: white; border: none; padding: 3px 6px;")
        delete_btn.clicked.connect(lambda checked, t=task_name: self.delete_task(t))
        action_layout.addWidget(edit_btn)
        action_layout.addWidget(delete_btn)
        action_layout.addStretch()
        action_widget.setLayout(action_layout)
        self.task_table.setCellWidget(row_position, 4, action_widget)

        self.task_name_input.clear()
        self.description_input.clear()
        self.status_input.setCurrentIndex(0)
        self.due_date_input.setDateTime(QDateTime.currentDateTime().addDays(7))
        QMessageBox.information(self, "Success", f"Task {task_name} added successfully.")

    def edit_task(self, task_name):
        """Placeholder for editing a task."""
        QMessageBox.information(self, "Edit Task", f"Editing task {task_name}. This functionality will be implemented soon.")

    def delete_task(self, task_name):
        """Delete a task from the table."""
        confirm = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete task {task_name}?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            for row in range(self.task_table.rowCount()):
                if self.task_table.item(row, 0).text() == task_name:
                    self.task_table.removeRow(row)
                    QMessageBox.information(self, "Success", f"Task {task_name} deleted.")
                    break
