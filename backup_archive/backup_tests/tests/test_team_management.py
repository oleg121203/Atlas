"""
Unit Tests for Team Management Module

This module contains tests for the TeamManagementDashboard class, ensuring that team management functionalities
work as expected.
"""

import os
import sqlite3
import unittest

from modules.collaboration.team_management import TeamManagementDashboard
from PySide6.QtWidgets import QApplication


class TestTeamManagement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app = None

    def setUp(self):
        self.dashboard = TeamManagementDashboard()
        self.conn = sqlite3.connect("test_team_management.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            permission_level TEXT DEFAULT 'Member'
        )""")
        self.cursor.execute("""
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

    def tearDown(self):
        self.dashboard.close()
        self.conn.close()
        os.remove("test_team_management.db")

    def test_add_team_member(self):
        initial_rows = self.dashboard.team_table.rowCount()
        self.dashboard.add_team_member()
        # Simulate adding a member through dialog
        self.cursor.execute(
            "INSERT INTO team_members (name, role, permission_level) VALUES (?, ?, ?)",
            ("Test Member", "Developer", "Member"),
        )
        self.conn.commit()
        self.dashboard.load_team_data()
        self.assertEqual(self.dashboard.team_table.rowCount(), initial_rows + 1)

    def test_assign_task(self):
        # First add a team member
        self.cursor.execute(
            "INSERT INTO team_members (name, role, permission_level) VALUES (?, ?, ?)",
            ("Test Member", "Developer", "Member"),
        )
        self.conn.commit()
        initial_rows = self.dashboard.task_table.rowCount()
        self.dashboard.assign_task()
        # Simulate assigning a task through dialog
        self.cursor.execute(
            "INSERT INTO tasks (title, description, assigned_to, due_date) VALUES (?, ?, ?, ?)",
            ("Test Task", "Test Description", 1, "2025-07-01"),
        )
        self.conn.commit()
        self.dashboard.load_team_data()
        self.assertEqual(self.dashboard.task_table.rowCount(), initial_rows + 1)

    def test_productivity_analytics(self):
        # Add test data
        self.cursor.execute(
            "INSERT INTO team_members (name, role, permission_level) VALUES (?, ?, ?)",
            ("Test Member", "Developer", "Member"),
        )
        self.cursor.execute(
            "INSERT INTO tasks (title, description, assigned_to, due_date, status) VALUES (?, ?, ?, ?, ?)",
            ("Test Task", "Test Description", 1, "2025-07-01", "Completed"),
        )
        self.cursor.execute(
            "INSERT INTO tasks (title, description, assigned_to, due_date, status) VALUES (?, ?, ?, ?, ?)",
            ("Test Task 2", "Test Description 2", 1, "2025-07-02", "Not Started"),
        )
        self.conn.commit()
        # Test analytics display (just ensure it runs without error for now)
        try:
            self.dashboard.view_productivity_analytics()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Productivity analytics failed with error: {str(e)}")


if __name__ == "__main__":
    unittest.main()
