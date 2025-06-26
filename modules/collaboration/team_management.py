"""
Team Management Module for Atlas

This module provides functionality for managing teams, assigning tasks, and tracking progress.
It includes UI components for team management dashboards and analytics for productivity insights.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QComboBox, QMessageBox
from PySide6.QtCore import Qt
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class TeamManagementDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Team Management Dashboard")
        self.resize(800, 600)
        self.setup_ui()
        self.setup_database()
        self.load_team_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Team Overview Section
        team_layout = QHBoxLayout()
        team_label = QLabel("Team Overview")
        team_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        team_layout.addWidget(team_label)
        team_layout.addStretch()
        add_member_btn = QPushButton("Add Team Member")
        add_member_btn.clicked.connect(self.add_team_member)
        team_layout.addWidget(add_member_btn)
        layout.addLayout(team_layout)

        # Team Members Table
        self.team_table = QTableWidget()
        self.team_table.setColumnCount(4)
        self.team_table.setHorizontalHeaderLabels(["ID", "Name", "Role", "Tasks Assigned"])
        self.team_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.team_table.doubleClicked.connect(self.view_member_details)
        layout.addWidget(self.team_table)

        # Task Assignment Section
        task_layout = QHBoxLayout()
        task_label = QLabel("Task Assignment")
        task_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        task_layout.addWidget(task_label)
        task_layout.addStretch()
        assign_task_btn = QPushButton("Assign Task")
        assign_task_btn.clicked.connect(self.assign_task)
        task_layout.addWidget(assign_task_btn)
        layout.addLayout(task_layout)

        # Task Table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(["Task ID", "Title", "Assigned To", "Status", "Due Date"])
        self.task_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.task_table.doubleClicked.connect(self.view_task_details)
        layout.addWidget(self.task_table)

        # Productivity Analytics Button
        analytics_btn = QPushButton("View Productivity Analytics")
        analytics_btn.clicked.connect(self.view_productivity_analytics)
        layout.addWidget(analytics_btn)

        self.setLayout(layout)

    def setup_database(self):
        self.conn = sqlite3.connect('team_management.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            permission_level TEXT DEFAULT 'Member'
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            assigned_to INTEGER,
            status TEXT DEFAULT 'Not Started',
            due_date TEXT,
            FOREIGN KEY (assigned_to) REFERENCES team_members(id)
        )""")
        self.conn.commit()

    def load_team_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM team_members")
        members = cursor.fetchall()
        self.team_table.setRowCount(len(members))
        for row, member in enumerate(members):
            for col, data in enumerate(member[:4]):
                self.team_table.setItem(row, col, QTableWidgetItem(str(data)))

        cursor.execute("SELECT t.id, t.title, m.name, t.status, t.due_date FROM tasks t LEFT JOIN team_members m ON t.assigned_to = m.id")
        tasks = cursor.fetchall()
        self.task_table.setRowCount(len(tasks))
        for row, task in enumerate(tasks):
            for col, data in enumerate(task):
                self.task_table.setItem(row, col, QTableWidgetItem(str(data) if data else ""))

    def add_team_member(self):
        dialog = AddMemberDialog(self)
        if dialog.exec_():
            name, role, permission = dialog.get_data()
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO team_members (name, role, permission_level) VALUES (?, ?, ?)", 
                          (name, role, permission))
            self.conn.commit()
            self.load_team_data()

    def assign_task(self):
        dialog = AssignTaskDialog(self, self.conn)
        if dialog.exec_():
            title, description, assigned_to, due_date = dialog.get_data()
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO tasks (title, description, assigned_to, due_date) VALUES (?, ?, ?, ?)", 
                          (title, description, assigned_to, due_date))
            self.conn.commit()
            self.load_team_data()

    def view_member_details(self, index):
        member_id = int(self.team_table.item(index.row(), 0).text())
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM team_members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        if member:
            dialog = MemberDetailsDialog(self, member)
            dialog.exec_()

    def view_task_details(self, index):
        task_id = int(self.task_table.item(index.row(), 0).text())
        cursor = self.conn.cursor()
        cursor.execute("SELECT t.*, m.name FROM tasks t LEFT JOIN team_members m ON t.assigned_to = m.id WHERE t.id = ?", (task_id,))
        task = cursor.fetchone()
        if task:
            dialog = TaskDetailsDialog(self, task)
            dialog.exec_()

    def view_productivity_analytics(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT m.name, COUNT(t.id) as task_count, SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks "
                      "FROM team_members m LEFT JOIN tasks t ON m.id = t.assigned_to GROUP BY m.id, m.name")
        data = cursor.fetchall()

        if data:
            df = pd.DataFrame(data, columns=['Name', 'Total Tasks', 'Completed Tasks'])
            fig, ax = plt.subplots(figsize=(10, 6))
            df.plot(x='Name', y=['Total Tasks', 'Completed Tasks'], kind='bar', ax=ax)
            ax.set_title('Team Productivity Analytics')
            ax.set_ylabel('Number of Tasks')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            QMessageBox.information(self, "No Data", "No productivity data available to display.")

    def closeEvent(self, event):
        self.conn.close()
        super().closeEvent(event)

class AddMemberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Team Member")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Name")
        layout.addWidget(self.name_input)

        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("Enter Role")
        layout.addWidget(self.role_input)

        self.permission_combo = QComboBox()
        self.permission_combo.addItems(["Admin", "Member"])
        layout.addWidget(self.permission_combo)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def get_data(self):
        return self.name_input.text(), self.role_input.text(), self.permission_combo.currentText()

class AssignTaskDialog(QDialog):
    def __init__(self, parent=None, conn=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Assign Task")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter Task Title")
        layout.addWidget(self.title_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter Task Description")
        layout.addWidget(self.desc_input)

        self.assignee_combo = QComboBox()
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM team_members")
        members = cursor.fetchall()
        for member in members:
            self.assignee_combo.addItem(member[1], member[0])
        layout.addWidget(self.assignee_combo)

        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate())
        layout.addWidget(self.due_date_input)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def get_data(self):
        return (self.title_input.text(), self.desc_input.toPlainText(), 
                self.assignee_combo.currentData(), self.due_date_input.date().toString("yyyy-MM-dd"))

class MemberDetailsDialog(QDialog):
    def __init__(self, parent=None, member_data=None):
        super().__init__(parent)
        self.setWindowTitle("Team Member Details")
        self.member_data = member_data
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"ID: {self.member_data[0]}"))
        layout.addWidget(QLabel(f"Name: {self.member_data[1]}"))
        layout.addWidget(QLabel(f"Role: {self.member_data[2]}"))
        layout.addWidget(QLabel(f"Permission Level: {self.member_data[3]}"))

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

class TaskDetailsDialog(QDialog):
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.setWindowTitle("Task Details")
        self.task_data = task_data
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Task ID: {self.task_data[0]}"))
        layout.addWidget(QLabel(f"Title: {self.task_data[1]}"))
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(desc_label)
        desc_text = QTextEdit()
        desc_text.setText(self.task_data[2])
        desc_text.setReadOnly(True)
        layout.addWidget(desc_text)
        layout.addWidget(QLabel(f"Assigned To: {self.task_data[5] if self.task_data[5] else 'Not Assigned'}"))
        layout.addWidget(QLabel(f"Status: {self.task_data[4]}"))
        layout.addWidget(QLabel(f"Due Date: {self.task_data[3]}"))

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)
