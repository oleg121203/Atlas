# Basic implementation of user_management.py for Atlas UI

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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


class UserManagement(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UserManagement")
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for managing users."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("User Management")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Table for displaying users
        self.user_table = QTableWidget()
        self.user_table.setRowCount(0)
        self.user_table.setColumnCount(3)
        self.user_table.setHorizontalHeaderLabels(["Username", "Role", "Actions"])
        self.user_table.setStyleSheet("border: 1px solid #404040; alternate-background-color: #303030;")
        self.user_table.setAlternatingRowColors(True)
        layout.addWidget(self.user_table)

        # Form for adding new users
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("New Username")
        self.username_input.setStyleSheet("padding: 5px; border: 1px solid #404040; background-color: #202020; color: #ffffff;")
        form_layout.addWidget(self.username_input)

        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("Role")
        self.role_input.setStyleSheet("padding: 5px; border: 1px solid #404040; background-color: #202020; color: #ffffff;")
        form_layout.addWidget(self.role_input)

        add_button = QPushButton("Add User")
        add_button.setStyleSheet("background-color: #007BFF; color: white; border: none; padding: 8px; font-weight: bold;")
        add_button.clicked.connect(self.add_user)
        form_layout.addWidget(add_button)

        layout.addWidget(form_widget)
        self.setLayout(layout)
        self.populate_table()

    def populate_table(self):
        """Populate the user table with sample data (to be replaced with real data)."""
        self.user_table.setRowCount(0)
        sample_users = [
            ("admin", "Administrator"),
            ("developer", "Developer"),
            ("user", "Standard User")
        ]

        for username, role in sample_users:
            row_position = self.user_table.rowCount()
            self.user_table.insertRow(row_position)
            self.user_table.setItem(row_position, 0, QTableWidgetItem(username))
            self.user_table.setItem(row_position, 1, QTableWidgetItem(role))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #dc3545; color: white; border: none; padding: 3px 6px;")
            delete_btn.clicked.connect(lambda checked, u=username: self.delete_user(u))
            action_layout.addWidget(delete_btn)
            action_layout.addStretch()
            action_widget.setLayout(action_layout)
            self.user_table.setCellWidget(row_position, 2, action_widget)

    def add_user(self):
        """Add a new user to the table."""
        username = self.username_input.text().strip()
        role = self.role_input.text().strip()

        if not username or not role:
            QMessageBox.warning(self, "Invalid Input", "Username and Role cannot be empty.")
            return

        row_position = self.user_table.rowCount()
        self.user_table.insertRow(row_position)
        self.user_table.setItem(row_position, 0, QTableWidgetItem(username))
        self.user_table.setItem(row_position, 1, QTableWidgetItem(role))

        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("background-color: #dc3545; color: white; border: none; padding: 3px 6px;")
        delete_btn.clicked.connect(lambda checked, u=username: self.delete_user(u))
        action_layout.addWidget(delete_btn)
        action_layout.addStretch()
        action_widget.setLayout(action_layout)
        self.user_table.setCellWidget(row_position, 2, action_widget)

        self.username_input.clear()
        self.role_input.clear()
        QMessageBox.information(self, "Success", f"User {username} added successfully.")

    def delete_user(self, username):
        """Delete a user from the table."""
        confirm = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete user {username}?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            for row in range(self.user_table.rowCount()):
                if self.user_table.item(row, 0).text() == username:
                    self.user_table.removeRow(row)
                    QMessageBox.information(self, "Success", f"User {username} deleted.")
                    break
