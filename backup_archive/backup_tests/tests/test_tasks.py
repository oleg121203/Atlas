"""
Test cases for the tasks module of Atlas application.
"""

import unittest

from modules.tasks.task_manager import TaskManager

from core.application import AtlasApplication


class TestTasksModule(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.app = AtlasApplication([])
        self.task_manager = TaskManager()

    def test_task_manager_initialization(self):
        """Test if the task manager initializes correctly."""
        self.assertIsNotNone(self.task_manager)
        self.assertTrue(hasattr(self.task_manager, "create_task"))

    def test_task_creation(self):
        """Test if a task can be created successfully."""
        task_name = "Test Task"
        task_id = self.task_manager.create_task(task_name)
        self.assertIsNotNone(task_id)
        self.assertIsInstance(task_id, str)


if __name__ == "__main__":
    unittest.main()
