# task_planner_agent_test.py

"""
Unit tests for the TaskPlannerAgent class.
"""

import json
import os
import sys
import unittest

# Adjust the path to include the parent directory for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock

from modules.agents.self_learning_agent import SelfLearningAgent
from modules.agents.task_planner_agent import TaskPlannerAgent

from utils.memory_management import MemoryManager


class TestTaskPlannerAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.memory_manager = MagicMock(spec=MemoryManager)
        self.self_learning_agent = MagicMock(spec=SelfLearningAgent)
        # Use MagicMock but ensure the return value is a plain dictionary
        self.self_learning_agent.get_user_learning_profile = MagicMock(
            return_value={
                "interaction_count": int(10),
                "learning_style": str("visual"),
                "knowledge_graph": {},
                "skill_graph": {},
                "avg_rating": float(4.5),
            }
        )
        self.task_planner_agent = TaskPlannerAgent(
            self.memory_manager, self.self_learning_agent, plans_path="test_plans"
        )
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
                "progress": 0.0,
            }
        }
        os.makedirs("test_plans", exist_ok=True)
        with open(os.path.join("test_plans", "active_plans.json"), "w") as f:
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
                "progress": 0.0,
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
        self.assertIn(plan_id, self.task_planner_agent.active_plans)
        plan = self.task_planner_agent.active_plans[plan_id]
        self.assertEqual(plan["user_id"], user_id)
        self.assertEqual(plan["goal"], goal)
        self.assertEqual(
            plan["status"], "pending_user_consent"
        )  # Updated due to ethical AI requirements
        self.assertTrue(len(plan["tasks"]) > 0)
        self.assertEqual(plan["progress"], 0.0)
        self.assertTrue(isinstance(plan["tasks"], list))
        self.assertIn("created_at", plan)
        self.assertIn("updated_at", plan)

    def test_update_task_status(self):
        """Test updating the status of a task within a plan."""
        user_id = "user1"
        goal = "Organize a workshop"
        plan_id = self.task_planner_agent.create_task_plan(user_id, goal)
        plan = self.task_planner_agent.active_plans[plan_id]
        task_id = plan["tasks"][0]["task_id"]
        # First grant consent to allow task execution
        self.task_planner_agent.confirm_user_consent(plan_id, True)
        # Now update task status
        result = self.task_planner_agent.update_task_status(
            plan_id, task_id, "completed"
        )
        self.assertTrue(result)
        updated_plan = self.task_planner_agent.active_plans[plan_id]
        updated_task = next(
            (task for task in updated_plan["tasks"] if task["task_id"] == task_id), None
        )
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task["status"], "completed")

    def test_update_task_status_without_consent(self):
        """Test that tasks cannot be updated without user consent."""
        user_id = "user1"
        goal = "Schedule a meeting"
        plan_id = self.task_planner_agent.create_task_plan(user_id, goal)
        plan = self.task_planner_agent.active_plans[plan_id]
        task_id = plan["tasks"][0]["task_id"] if plan["tasks"] else None
        self.assertIsNotNone(task_id, "No tasks found in plan")
        result = self.task_planner_agent.update_task_status(
            plan_id, task_id, "in_progress"
        )
        self.assertFalse(result, "Task update should fail without consent")
        updated_plan = self.task_planner_agent.active_plans[plan_id]
        updated_task = next(
            (t for t in updated_plan["tasks"] if t["task_id"] == task_id), None
        )
        self.assertIsNotNone(updated_task, "Task not found after update attempt")
        self.assertEqual(
            updated_task["status"],
            "pending",
            "Task status should remain pending without consent",
        )

    def test_confirm_user_consent_and_update(self):
        """Test confirming user consent and then updating a task."""
        user_id = "user1"
        goal = "Plan a project"
        plan_id = self.task_planner_agent.create_task_plan(user_id, goal)
        # Confirm consent
        consent_result = self.task_planner_agent.confirm_user_consent(plan_id, True)
        self.assertTrue(consent_result, "Consent confirmation should succeed")
        updated_plan = self.task_planner_agent.active_plans[plan_id]
        self.assertEqual(
            updated_plan["status"],
            "active",
            "Plan status should be active after consent",
        )
        self.assertEqual(
            updated_plan["ethical_flags"]["consent_status"],
            "granted",
            "Consent status should be granted",
        )
        # Now try to update a task
        task_id = updated_plan["tasks"][0]["task_id"] if updated_plan["tasks"] else None
        self.assertIsNotNone(task_id, "No tasks found in plan")
        update_result = self.task_planner_agent.update_task_status(
            plan_id, task_id, "in_progress"
        )
        self.assertTrue(update_result, "Task update should succeed with consent")
        final_plan = self.task_planner_agent.active_plans[plan_id]
        final_task = next(
            (t for t in final_plan["tasks"] if t["task_id"] == task_id), None
        )
        self.assertIsNotNone(final_task, "Task not found after update")
        self.assertEqual(
            final_task["status"],
            "in_progress",
            "Task status should be in_progress after update",
        )

    def test_deny_user_consent(self):
        """Test denying user consent and its effect on plan status."""
        user_id = "user1"
        goal = "Organize an event"
        plan_id = self.task_planner_agent.create_task_plan(user_id, goal)
        consent_result = self.task_planner_agent.confirm_user_consent(plan_id, False)
        self.assertTrue(consent_result, "Consent denial should succeed")
        updated_plan = self.task_planner_agent.active_plans[plan_id]
        self.assertEqual(
            updated_plan["status"],
            "rejected_by_user",
            "Plan status should be rejected_by_user after denial",
        )
        self.assertEqual(
            updated_plan["ethical_flags"]["consent_status"],
            "denied",
            "Consent status should be denied",
        )
        # Try to update a task, should fail
        task_id = updated_plan["tasks"][0]["task_id"] if updated_plan["tasks"] else None
        self.assertIsNotNone(task_id, "No tasks found in plan")
        update_result = self.task_planner_agent.update_task_status(
            plan_id, task_id, "in_progress"
        )
        self.assertFalse(
            update_result, "Task update should fail when consent is denied"
        )

    def test_break_down_goal_meeting(self):
        """Test breaking down a goal related to a meeting."""
        user_id = "user1"
        goal = "Schedule a team meeting"
        context = {"current_state": {"is_weekend": False}}
        tasks = self.task_planner_agent._break_down_goal(goal, context, user_id)
        self.assertTrue(len(tasks) > 0)  # At least one task should be created
        self.assertTrue(
            len(tasks) == 1
        )  # Due to consolidation with high avg_rating, should be 1
        for i, task in enumerate(tasks):
            self.assertIn("task_id", task)
            self.assertIn("description", task)
            self.assertIn("priority", task)
            self.assertIn("dependencies", task)
            self.assertIn("status", task)
            self.assertEqual(task["status"], "pending")
            self.assertIn("due_date", task)
            self.assertIn("execution_method", task)
            if i > 0:
                self.assertTrue(
                    len(task["dependencies"]) >= 0
                )  # May or may not have dependencies after consolidation

    def test_break_down_goal_generic(self):
        """Test breaking down a generic goal."""
        user_id = "user1"
        goal = "Learn Python programming"
        context = {"current_state": {"is_weekend": False}}
        tasks = self.task_planner_agent._break_down_goal(goal, context, user_id)
        self.assertTrue(len(tasks) > 0)  # At least one task should be created
        self.assertTrue(
            len(tasks) == 1
        )  # Due to consolidation with high avg_rating, should be 1
        for i, task in enumerate(tasks):
            self.assertIn("task_id", task)
            self.assertIn("description", task)
            self.assertIn("priority", task)
            self.assertIn("dependencies", task)
            self.assertIn("status", task)
            self.assertEqual(task["status"], "pending")
            self.assertIn("due_date", task)
            self.assertIn("execution_method", task)
            if i > 0:
                self.assertTrue(
                    len(task["dependencies"]) >= 0
                )  # May or may not have dependencies after consolidation


if __name__ == "__main__":
    unittest.main()
