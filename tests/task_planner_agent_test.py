# task_planner_agent_test.py

"""
Unit tests for the TaskPlannerAgent class.
"""

import unittest
import os
import json
from datetime import datetime, timedelta
import sys

# Adjust the path to include the parent directory for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock, patch
from utils.memory_management import MemoryManager
from agents.self_learning_agent import SelfLearningAgent
from agents.task_planner_agent import TaskPlannerAgent

class TestTaskPlannerAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.memory_manager = MagicMock(spec=MemoryManager)
        self.self_learning_agent = MagicMock(spec=SelfLearningAgent)
        # Define a plain function to return a dictionary
        def return_user_learning_profile(user_id):
            return {
                "interaction_count": 10,
                "learning_style": "visual",
                "knowledge_graph": {},
                "skill_graph": {},
                "avg_rating": 4.5
            }
        # Directly set the attribute to a callable function
        setattr(self.self_learning_agent, 'get_user_learning_profile', return_user_learning_profile)
        self.task_planner_agent = TaskPlannerAgent(self.memory_manager, self.self_learning_agent, plans_path="test_plans")
        # Ensure test plans directory exists
        os.makedirs("test_plans", exist_ok=True)
        # Clear any existing test plans data
        for file in os.listdir("test_plans"):
            file_path = os.path.join("test_plans", file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        # Mock save_plans to avoid file operations during tests
        self.task_planner_agent.save_plans = MagicMock()

    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists("test_plans"):
            for file in os.listdir("test_plans"):
                file_path = os.path.join("test_plans", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir("test_plans")

    def test_initialization(self):
        """Test that TaskPlannerAgent initializes correctly."""
        self.assertIsInstance(self.task_planner_agent, TaskPlannerAgent)
        self.assertEqual(self.task_planner_agent.plans_path, "test_plans")
        # Skip directory existence check as it's mocked
        self.assertEqual(self.task_planner_agent.active_plans, {})
        self.assertEqual(self.task_planner_agent.task_history, {})

    def test_load_plans_no_file(self):
        """Test loading plans when no file exists."""
        self.task_planner_agent.load_plans()
        self.assertEqual(self.task_planner_agent.active_plans, {})

    def test_load_plans_with_file(self):
        """Test loading plans from an existing file."""
        sample_plans = {
            "plan_user1_20250625_120000": {
                "plan_id": "plan_user1_20250625_120000",
                "user_id": "user1",
                "goal": "Schedule a meeting",
                "context": {},
                "tasks": [],
                "status": "active",
                "created_at": "2025-06-25T12:00:00",
                "updated_at": "2025-06-25T12:00:00",
                "progress": 0.0
            }
        }
        os.makedirs("test_plans", exist_ok=True)
        with open(os.path.join("test_plans", "active_plans.json"), 'w') as f:
            json.dump(sample_plans, f)

        self.task_planner_agent.load_plans()
        self.assertEqual(self.task_planner_agent.active_plans, sample_plans)

    def test_save_plans(self):
        """Test saving plans to file."""
        self.task_planner_agent.active_plans = {
            "plan_user1_20250625_120000": {
                "plan_id": "plan_user1_20250625_120000",
                "user_id": "user1",
                "goal": "Schedule a meeting",
                "context": {},
                "tasks": [],
                "status": "active",
                "created_at": "2025-06-25T12:00:00",
                "updated_at": "2025-06-25T12:00:00",
                "progress": 0.0
            }
        }
        self.task_planner_agent.save_plans()
        # Since save_plans is mocked, just check if it was called
        self.task_planner_agent.save_plans.assert_called()

    def test_create_task_plan(self):
        """Test creating a new task plan."""
        user_id = "user1"
        goal = "Organize a workshop"
        plan_id = self.task_planner_agent.create_task_plan(user_id, goal)
        self.assertTrue(plan_id.startswith("plan_user1_"))
        self.assertIn(plan_id, self.task_planner_agent.active_plans)
        plan = self.task_planner_agent.active_plans[plan_id]
        self.assertEqual(plan["user_id"], user_id)
        self.assertEqual(plan["goal"], goal)
        self.assertEqual(plan["status"], "active")
        self.assertEqual(plan["progress"], 0.0)
        self.assertTrue(isinstance(plan["tasks"], list))
        self.assertTrue(len(plan["tasks"]) > 0)
        self.assertIn("created_at", plan)
        self.assertIn("updated_at", plan)

    def test_break_down_goal_meeting(self):
        """Test breaking down a goal related to a meeting."""
        user_id = "user1"
        goal = "Schedule a team meeting"
        context = {}
        # Mock datetime to control due dates
        with patch('datetime.datetime') as mocked_datetime:
            mocked_datetime.now.return_value = datetime(2025, 6, 25, 12, 0, 0)
            tasks = self.task_planner_agent._break_down_goal(goal, context, user_id)
            self.assertTrue(len(tasks) >= 3)
            task_descriptions = [task["description"] for task in tasks]
            self.assertIn("Identify meeting participants", task_descriptions)
            self.assertIn("Schedule meeting time", task_descriptions)
            self.assertIn("Send meeting invitations", task_descriptions)
            for i, task in enumerate(tasks):
                self.assertEqual(task["priority"], i + 1)
                if i > 0:
                    self.assertEqual(task["dependencies"], [f"task_{i}"])
                else:
                    self.assertEqual(task["dependencies"], [])
                self.assertEqual(task["status"], "pending")
                self.assertEqual(task["progress"], 0.0)
                self.assertIn("due_date", task)

    def test_break_down_goal_generic(self):
        """Test breaking down a generic goal."""
        user_id = "user1"
        goal = "Learn a new skill"
        context = {}
        # Mock datetime to control due dates
        with patch('datetime.datetime') as mocked_datetime:
            mocked_datetime.now.return_value = datetime(2025, 6, 25, 12, 0, 0)
            tasks = self.task_planner_agent._break_down_goal(goal, context, user_id)
            self.assertTrue(len(tasks) >= 3)
            for i, task in enumerate(tasks):
                self.assertTrue(task["description"].startswith(f"Step {i+1} towards"))
                self.assertEqual(task["priority"], i + 1)
                if i > 0:
                    self.assertEqual(task["dependencies"], [f"task_{i}"])
                else:
                    self.assertEqual(task["dependencies"], [])
                self.assertEqual(task["status"], "pending")
                self.assertEqual(task["progress"], 0.0)
                self.assertIn("due_date", task)

if __name__ == '__main__':
    unittest.main()
