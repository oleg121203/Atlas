"""
Unit tests for WorkflowManager

Tests workflow creation, execution, state persistence, and error recovery.
"""

import os
import shutil
import unittest

from core.logging import get_logger
from core.workflow_manager import WorkflowManager

logger = get_logger("TestWorkflowManager")


class TestWorkflowManager(unittest.TestCase):
    """Test cases for WorkflowManager."""

    def setUp(self):
        """Set up test environment before each test."""
        self.config = {"workflow_states_dir": "workflows/states", "max_retries": 3}
        self.workflow_manager = WorkflowManager(self.config)

        # Create temporary directories for testing
        os.makedirs("workflows/states", exist_ok=True)

        # Sample workflow definition
        self.sample_workflow = {
            "initial_step": "start",
            "steps": {
                "start": {"next_step": "process", "simulate_failure": False},
                "process": {"next_step": "end", "simulate_failure": False},
                "end": {"simulate_failure": False},
            },
        }

        # Failing workflow definition
        self.failing_workflow = {
            "initial_step": "start",
            "steps": {
                "start": {"next_step": "process", "simulate_failure": False},
                "process": {"next_step": "end", "simulate_failure": True},
                "end": {"simulate_failure": False},
            },
        }

    def tearDown(self):
        """Clean up test environment after each test."""
        shutil.rmtree("workflows", ignore_errors=True)

    def test_create_workflow(self):
        """Test creating a new workflow."""
        success = self.workflow_manager.create_workflow(
            "test_workflow", self.sample_workflow
        )
        self.assertTrue(success, "Workflow creation should succeed")
        self.assertIn(
            "test_workflow",
            self.workflow_manager.workflows,
            "Workflow should be in manager",
        )
        state = self.workflow_manager.get_workflow_state("test_workflow")
        self.assertEqual(
            state["status"], "created", "Workflow status should be created"
        )

    def test_start_workflow(self):
        """Test starting a workflow."""
        self.workflow_manager.create_workflow("test_workflow", self.sample_workflow)
        success = self.workflow_manager.start_workflow("test_workflow")
        self.assertTrue(success, "Workflow start should succeed")
        state = self.workflow_manager.get_workflow_state("test_workflow")
        self.assertEqual(
            state["status"], "running", "Workflow status should be running"
        )

    def test_start_nonexistent_workflow(self):
        """Test starting a workflow that doesn't exist."""
        success = self.workflow_manager.start_workflow("nonexistent")
        self.assertFalse(success, "Starting nonexistent workflow should fail")

    def test_execute_step_success(self):
        """Test executing a step successfully."""
        self.workflow_manager.create_workflow("test_workflow", self.sample_workflow)
        self.workflow_manager.start_workflow("test_workflow")
        success = self.workflow_manager.execute_step("test_workflow")
        self.assertTrue(success, "Step execution should succeed")
        state = self.workflow_manager.get_workflow_state("test_workflow")
        self.assertEqual(
            state["current_step"], "process", "Workflow should move to next step"
        )
        self.assertEqual(
            state["status"], "running", "Workflow status should remain running"
        )

    def test_execute_step_failure(self):
        """Test executing a step that fails."""
        self.workflow_manager.create_workflow("test_workflow", self.failing_workflow)
        self.workflow_manager.start_workflow("test_workflow")
        # First step succeeds
        success = self.workflow_manager.execute_step("test_workflow")
        self.assertTrue(success, "First step execution should succeed")
        # Second step fails
        success = self.workflow_manager.execute_step("test_workflow")
        self.assertFalse(success, "Second step execution should fail")
        state = self.workflow_manager.get_workflow_state("test_workflow")
        self.assertEqual(state["status"], "error", "Workflow status should be error")
        self.assertIsNotNone(
            state["error"], "Workflow state should contain error information"
        )
        self.assertEqual(state["retry_count"], 1, "Retry count should be incremented")

    def test_retry_step(self):
        """Test retrying a failed step."""
        self.workflow_manager.create_workflow("test_workflow", self.failing_workflow)
        self.workflow_manager.start_workflow("test_workflow")
        self.workflow_manager.execute_step("test_workflow")  # First step succeeds
        self.workflow_manager.execute_step("test_workflow")  # Second step fails
        success = self.workflow_manager.retry_step("test_workflow")
        self.assertFalse(success, "Retry should fail again")
        state = self.workflow_manager.get_workflow_state("test_workflow")
        self.assertEqual(
            state["retry_count"], 2, "Retry count should be incremented again"
        )

    def test_retry_max_attempts(self):
        """Test retrying beyond max attempts."""
        self.workflow_manager.create_workflow("test_workflow", self.failing_workflow)
        self.workflow_manager.start_workflow("test_workflow")
        self.workflow_manager.execute_step("test_workflow")  # First step succeeds
        self.workflow_manager.execute_step("test_workflow")  # Second step fails
        for _ in range(3):
            self.workflow_manager.retry_step("test_workflow")
        state = self.workflow_manager.get_workflow_state("test_workflow")
        self.assertEqual(
            state["status"],
            "failed",
            "Workflow status should be failed after max retries",
        )

    def test_rollback_workflow(self):
        """Test rolling back a workflow after failure."""
        self.workflow_manager.create_workflow("test_workflow", self.failing_workflow)
        self.workflow_manager.start_workflow("test_workflow")
        self.workflow_manager.execute_step("test_workflow")  # First step succeeds
        self.workflow_manager.execute_step("test_workflow")  # Second step fails
        success = self.workflow_manager.rollback_workflow("test_workflow")
        self.assertTrue(success, "Rollback should succeed")
        state = self.workflow_manager.get_workflow_state("test_workflow")
        self.assertEqual(
            state["current_step"],
            "start",
            "Workflow should rollback to last successful step",
        )
        self.assertEqual(
            state["status"],
            "running",
            "Workflow status should be running after rollback",
        )
        self.assertIsNone(state["error"], "Error should be cleared after rollback")

    def test_persist_and_load_workflow_state(self):
        """Test persisting and loading workflow state."""
        self.workflow_manager.create_workflow("test_workflow", self.sample_workflow)
        self.workflow_manager.start_workflow("test_workflow")
        self.workflow_manager.execute_step("test_workflow")

        # Create a new manager to load the state
        new_manager = WorkflowManager(self.config)
        success = new_manager.load_workflow_state("test_workflow")
        self.assertTrue(success, "Loading workflow state should succeed")
        state = new_manager.get_workflow_state("test_workflow")
        self.assertEqual(
            state["current_step"], "process", "Loaded state should match executed state"
        )


if __name__ == "__main__":
    unittest.main()
