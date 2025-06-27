import json
import os
import unittest

from workflow.workflow_feedback import WorkflowFeedback


class TestWorkflowFeedback(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.test_feedback_file = "/tmp/test_workflow_feedback.json"
        self.feedback = WorkflowFeedback(self.test_feedback_file)

    def tearDown(self):
        """Clean up after each test method"""
        if os.path.exists(self.test_feedback_file):
            os.remove(self.test_feedback_file)

    def test_initialization_empty_file(self):
        """Test initialization with non-existent feedback file"""
        self.assertEqual(len(self.feedback.feedback_data), 0)

    def test_add_feedback(self):
        """Test adding feedback for a workflow"""
        workflow = {"name": "Test Workflow", "steps": []}
        user_input = "Create a test workflow"
        rating = 4
        comments = "Good structure but missing a step"
        modifications = {"added_step": {"id": "step3", "action": "finalize"}}

        self.feedback.add_feedback(
            workflow, user_input, rating, comments, modifications
        )
        self.assertEqual(len(self.feedback.feedback_data), 1)

        entry = self.feedback.feedback_data[0]
        self.assertEqual(entry["user_input"], user_input)
        self.assertEqual(entry["rating"], rating)
        self.assertEqual(entry["comments"], comments)
        self.assertEqual(entry["modifications"], modifications)
        self.assertTrue("timestamp" in entry)

        # Check if saved to file
        with open(self.test_feedback_file, "r") as f:
            saved_data = json.load(f)
            self.assertEqual(len(saved_data), 1)
            self.assertEqual(saved_data[0]["rating"], rating)

    def test_add_feedback_rating_bounds(self):
        """Test adding feedback with rating outside 1-5 range"""
        workflow = {"name": "Test Workflow", "steps": []}

        # Test rating too low
        self.feedback.add_feedback(workflow, "Test", 0)
        self.assertEqual(self.feedback.feedback_data[0]["rating"], 1)

        # Test rating too high
        self.feedback.add_feedback(workflow, "Test2", 6)
        self.assertEqual(self.feedback.feedback_data[1]["rating"], 5)

    def test_get_feedback_summary_empty(self):
        """Test feedback summary with no feedback"""
        summary = self.feedback.get_feedback_summary()
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["average_rating"], 0)
        self.assertEqual(len(summary["common_issues"]), 0)

    def test_get_feedback_summary_with_data(self):
        """Test feedback summary with multiple feedback entries"""
        workflow = {"name": "Test Workflow", "steps": []}

        self.feedback.add_feedback(workflow, "Test1", 4, "Good but missing feature")
        self.feedback.add_feedback(workflow, "Test2", 3, "Missing another thing")
        self.feedback.add_feedback(workflow, "Test3", 5, "Perfect, no issues")
        self.feedback.add_feedback(
            workflow, "Test4", 2, "Missing critical component", {"added": True}
        )

        summary = self.feedback.get_feedback_summary()
        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["average_rating"], 3.5)
        self.assertGreaterEqual(summary["modification_rate"], 25.0)
        self.assertIn("'missing' mentioned 3 times", summary["common_issues"])


if __name__ == "__main__":
    unittest.main()
