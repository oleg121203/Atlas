"""
Unit Tests for AI-Driven Automation Module
"""

import unittest
from datetime import datetime

import pandas as pd

from advanced_analytics.ai_automation import AIAutomation


class TestAIAutomation(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.start_date = datetime(2025, 1, 1)
        self.end_date = datetime(2025, 12, 31)
        self.ai = AIAutomation("test_source")

    def test_load_task_data(self):
        """Test loading task data for a specified date range."""
        data = self.ai.load_task_data(self.start_date, self.end_date)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn("task_id", data.columns)
        self.assertIn("user_id", data.columns)

    def test_prioritize_tasks(self):
        """Test prioritizing tasks using AI-driven clustering."""
        tasks = [
            {"name": "Urgent report", "due_date": "today", "created_from_text": False},
            {
                "name": "Long term project planning document",
                "due_date": "not specified",
                "created_from_text": False,
            },
            {"name": "Quick call", "due_date": "tomorrow", "created_from_text": True},
        ]
        prioritized = self.ai.prioritize_tasks(tasks)

        self.assertEqual(len(prioritized), 3)
        # Check if tasks are ordered by priority
        priorities = [task["priority"] for task in prioritized]
        self.assertTrue(priorities[0] in ["high", "medium"])
        self.assertTrue(priorities[1] in ["high", "medium"])
        self.assertTrue(priorities[2] in ["medium", "low"])
        # Check that urgent task with 'today' due date is high priority
        urgent_task = next(
            task for task in prioritized if task["name"] == "Urgent report"
        )
        self.assertEqual(urgent_task["priority"], "high")

    def test_extract_task_from_text(self):
        """Test extracting task information from natural language text."""
        text_samples = [
            "Create a task: Prepare presentation due next Friday",
            "Need to call client by tomorrow",
            "Have to complete report by 12/15/25",
            "Random text with no task",
            "Make a task - Review budget on 12-15-25",
        ]
        expected_results = [
            {
                "name": "Prepare presentation",
                "due_date": "next Friday",
                "priority": "medium",
                "created_from_text": True,
            },
            {
                "name": "call client",
                "due_date": "tomorrow",
                "priority": "medium",
                "created_from_text": True,
            },
            {
                "name": "complete report",
                "due_date": "12/15/25",
                "priority": "medium",
                "created_from_text": True,
            },
            None,
            {
                "name": "Review budget",
                "due_date": "12-15-25",
                "priority": "medium",
                "created_from_text": True,
            },
        ]

        for text, expected in zip(text_samples, expected_results):
            result = self.ai.extract_task_from_text(text)
            if expected is None:
                self.assertIsNone(result)
            else:
                self.assertIsNotNone(result)
                self.assertEqual(result["name"], expected["name"])
                self.assertEqual(result["due_date"], expected["due_date"])
                self.assertEqual(result["priority"], expected["priority"])

    def test_recommend_workflow(self):
        """Test recommending workflow optimizations based on user behavior."""
        self.ai.load_task_data(self.start_date, self.end_date)
        user_id = self.ai.task_data["user_id"].iloc[0]
        recommendations = self.ai.recommend_workflow(user_id)
        self.assertIsInstance(recommendations, list)
        if recommendations:  # Recommendations might be empty depending on data
            for rec in recommendations:
                self.assertIsInstance(rec, dict)
                self.assertIn("recommendation", rec)
                self.assertIn("confidence", rec)
                self.assertIn("reason", rec)
                self.assertGreaterEqual(rec["confidence"], 0.0)
                self.assertLessEqual(rec["confidence"], 1.0)

    def test_recommend_workflow_no_data(self):
        """Test recommending workflow with no data for user."""
        recommendations = self.ai.recommend_workflow(9999)  # Non-existent user ID
        self.assertEqual(recommendations, [])


if __name__ == "__main__":
    unittest.main()
