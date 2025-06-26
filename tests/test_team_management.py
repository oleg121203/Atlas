"""Unit Tests for Team Management Module"""

import unittest
import os
import sys
import json
import time

from unittest.mock import patch

# Ensure the parent directory is in the path so we can import from team_management
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from team_management import TeamManager

class TestTeamManager(unittest.TestCase):
    def setUp(self):
        self.team_manager = TeamManager()
        # Clear any existing data for a clean test environment
        self.team_manager.teams = {}
        self.team_manager.users = {}
        self.team_manager.tasks = {}
        self.team_manager._save_data()

    def test_create_team(self):
        team_id = self.team_manager.create_team("Test Team", "admin1")
        self.assertIsNotNone(team_id)
        self.assertIn(team_id, self.team_manager.teams)
        self.assertEqual(self.team_manager.teams[team_id]['name'], "Test Team")
        self.assertIn("admin1", self.team_manager.teams[team_id]['admins'])
        self.assertIn("admin1", self.team_manager.teams[team_id]['members'])

    def test_add_user_to_team(self):
        team_id = self.team_manager.create_team("Test Team", "admin1")
        result = self.team_manager.add_user_to_team(team_id, "user1", is_admin=False)
        self.assertTrue(result)
        self.assertIn("user1", self.team_manager.teams[team_id]['members'])
        self.assertNotIn("user1", self.team_manager.teams[team_id]['admins'])

    def test_add_user_to_team_as_admin(self):
        team_id = self.team_manager.create_team("Test Team", "admin1")
        result = self.team_manager.add_user_to_team(team_id, "admin2", is_admin=True)
        self.assertTrue(result)
        self.assertIn("admin2", self.team_manager.teams[team_id]['members'])
        self.assertIn("admin2", self.team_manager.teams[team_id]['admins'])

    def test_add_user_to_nonexistent_team(self):
        result = self.team_manager.add_user_to_team("nonexistent", "user1")
        self.assertFalse(result)

    def test_remove_user_from_team(self):
        team_id = self.team_manager.create_team("Test Team", "admin1")
        self.team_manager.add_user_to_team(team_id, "user1", is_admin=False)
        result = self.team_manager.remove_user_from_team(team_id, "user1")
        self.assertTrue(result)
        self.assertNotIn("user1", self.team_manager.teams[team_id]['members'])
        self.assertNotIn("user1", self.team_manager.teams[team_id]['admins'])

    def test_remove_user_from_nonexistent_team(self):
        result = self.team_manager.remove_user_from_team("nonexistent", "user1")
        self.assertFalse(result)

    def test_create_task(self):
        task_id = self.team_manager.create_task("Test Task", "Task Description", "creator1")
        self.assertIsNotNone(task_id)
        self.assertIn(task_id, self.team_manager.tasks)
        self.assertEqual(self.team_manager.tasks[task_id]['title'], "Test Task")
        self.assertEqual(self.team_manager.tasks[task_id]['description'], "Task Description")
        self.assertEqual(self.team_manager.tasks[task_id]['creator_id'], "creator1")
        self.assertEqual(self.team_manager.tasks[task_id]['status'], "open")

    def test_assign_task_to_team(self):
        team_id = self.team_manager.create_team("Test Team", "admin1")
        task_id = self.team_manager.create_task("Test Task", "Task Description", "creator1")
        result = self.team_manager.assign_task_to_team(team_id, task_id)
        self.assertTrue(result)
        self.assertIn(task_id, self.team_manager.teams[team_id]['tasks'])
        self.assertEqual(self.team_manager.tasks[task_id]['team_id'], team_id)

    def test_assign_task_to_nonexistent_team(self):
        task_id = self.team_manager.create_task("Test Task", "Task Description", "creator1")
        result = self.team_manager.assign_task_to_team("nonexistent", task_id)
        self.assertFalse(result)

    def test_assign_nonexistent_task_to_team(self):
        team_id = self.team_manager.create_team("Test Team", "admin1")
        result = self.team_manager.assign_task_to_team(team_id, "nonexistent")
        self.assertFalse(result)

    def test_assign_task_to_user(self):
        task_id = self.team_manager.create_task("Test Task", "Task Description", "creator1")
        result = self.team_manager.assign_task_to_user(task_id, "user1")
        self.assertTrue(result)
        self.assertEqual(self.team_manager.tasks[task_id]['assignee_id'], "user1")

    def test_assign_nonexistent_task_to_user(self):
        result = self.team_manager.assign_task_to_user("nonexistent", "user1")
        self.assertFalse(result)

    def test_update_task_status(self):
        task_id = self.team_manager.create_task("Test Task", "Task Description", "creator1")
        result = self.team_manager.update_task_status(task_id, "in_progress", 50)
        self.assertTrue(result)
        self.assertEqual(self.team_manager.tasks[task_id]['status'], "in_progress")
        self.assertEqual(self.team_manager.tasks[task_id]['progress'], 50)

    def test_update_nonexistent_task_status(self):
        result = self.team_manager.update_task_status("nonexistent", "in_progress", 50)
        self.assertFalse(result)

    def test_get_team_tasks(self):
        team_id = self.team_manager.create_team("Test Team", "admin1")
        task_id1 = self.team_manager.create_task("Task 1", "Description 1", "creator1")
        task_id2 = self.team_manager.create_task("Task 2", "Description 2", "creator1")
        self.team_manager.assign_task_to_team(team_id, task_id1)
        self.team_manager.assign_task_to_team(team_id, task_id2)
        team_tasks = self.team_manager.get_team_tasks(team_id)
        self.assertEqual(len(team_tasks), 2)
        task_ids = [task['id'] for task in team_tasks]
        self.assertIn(task_id1, task_ids)
        self.assertIn(task_id2, task_ids)

    def test_get_team_tasks_nonexistent_team(self):
        team_tasks = self.team_manager.get_team_tasks("nonexistent")
        self.assertEqual(len(team_tasks), 0)

    def test_get_user_tasks(self):
        task_id1 = self.team_manager.create_task("Task 1", "Description 1", "creator1")
        task_id2 = self.team_manager.create_task("Task 2", "Description 2", "creator1")
        self.team_manager.assign_task_to_user(task_id1, "user1")
        self.team_manager.assign_task_to_user(task_id2, "user1")
        user_tasks = self.team_manager.get_user_tasks("user1")
        self.assertEqual(len(user_tasks), 2)
        task_ids = [task['id'] for task in user_tasks]
        self.assertIn(task_id1, task_ids)
        self.assertIn(task_id2, task_ids)

    def test_get_user_tasks_no_tasks(self):
        user_tasks = self.team_manager.get_user_tasks("user1")
        self.assertEqual(len(user_tasks), 0)

    def test_get_team_progress(self):
        team_id = self.team_manager.create_team("Test Team", "admin1")
        task_id1 = self.team_manager.create_task("Task 1", "Description 1", "creator1")
        task_id2 = self.team_manager.create_task("Task 2", "Description 2", "creator1")
        self.team_manager.assign_task_to_team(team_id, task_id1)
        self.team_manager.assign_task_to_team(team_id, task_id2)
        self.team_manager.update_task_status(task_id1, "completed", 100)
        progress = self.team_manager.get_team_progress(team_id)
        self.assertEqual(progress['total_tasks'], 2)
        self.assertEqual(progress['completed_tasks'], 1)
        self.assertEqual(progress['progress_percent'], 50.0)

    def test_get_team_progress_no_tasks(self):
        team_id = self.team_manager.create_team("Test Team", "admin1")
        progress = self.team_manager.get_team_progress(team_id)
        self.assertEqual(progress['total_tasks'], 0)
        self.assertEqual(progress['completed_tasks'], 0)
        self.assertEqual(progress['progress_percent'], 0)

    def test_get_team_progress_nonexistent_team(self):
        progress = self.team_manager.get_team_progress("nonexistent")
        self.assertEqual(progress['total_tasks'], 0)
        self.assertEqual(progress['completed_tasks'], 0)
        self.assertEqual(progress['progress_percent'], 0)

    def test_add_user(self):
        result = self.team_manager.add_user("user1", "User One", "user1@example.com")
        self.assertTrue(result)
        self.assertIn("user1", self.team_manager.users)
        self.assertEqual(self.team_manager.users["user1"]['name'], "User One")
        self.assertEqual(self.team_manager.users["user1"]['email'], "user1@example.com")

    def test_add_existing_user(self):
        self.team_manager.add_user("user1", "User One", "user1@example.com")
        result = self.team_manager.add_user("user1", "User Two", "user2@example.com")
        self.assertFalse(result)
        self.assertEqual(self.team_manager.users["user1"]['name'], "User One")

    def test_get_user_teams(self):
        team_id1 = self.team_manager.create_team("Team 1", "admin1")
        team_id2 = self.team_manager.create_team("Team 2", "admin1")
        self.team_manager.add_user_to_team(team_id1, "user1")
        self.team_manager.add_user_to_team(team_id2, "user1")
        user_teams = self.team_manager.get_user_teams("user1")
        self.assertEqual(len(user_teams), 2)
        team_ids = [team['id'] for team in user_teams]
        self.assertIn(team_id1, team_ids)
        self.assertIn(team_id2, team_ids)

    def test_get_user_teams_nonexistent_user(self):
        user_teams = self.team_manager.get_user_teams("nonexistent")
        self.assertEqual(len(user_teams), 0)

if __name__ == '__main__':
    unittest.main()
