"""
Unit Tests for Workflow Execution Engine

This module tests the core functionality of the WorkflowEngine class,
including transactional execution, state persistence, and error handling.
"""

import unittest
import os
import json
from workflow.engine import WorkflowEngine
from workflow.error_handling import ErrorHandler, StopOnCritical, RetryAction

class TestWorkflowEngine(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.db_path = "test_workflow_state.db"
        self.engine = WorkflowEngine(self.db_path)
        self.workflow_id = "test_workflow_1"
        self.initial_state = {"step": 1, "status": "started"}

    def tearDown(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_start_workflow(self):
        """Test starting a workflow and saving initial state."""
        self.engine.start_workflow(self.workflow_id, self.initial_state)
        recovered_state = self.engine.recover_workflow(self.workflow_id)
        self.assertEqual(recovered_state, self.initial_state)

    def test_execute_action_success(self):
        """Test executing a successful action within a workflow."""
        self.engine.start_workflow(self.workflow_id, self.initial_state)
        
        def successful_action(x):
            return x * 2
        
        result = self.engine.execute_action(successful_action, 5)
        self.assertEqual(result, 10)

    def test_execute_action_failure(self):
        """Test executing a failing action and rollback."""
        self.engine.start_workflow(self.workflow_id, self.initial_state)
        
        def failing_action():
            raise ValueError("Action failed")
        
        with self.assertRaises(ValueError):
            self.engine.execute_action(failing_action)

    def test_update_state(self):
        """Test updating workflow state."""
        self.engine.start_workflow(self.workflow_id, self.initial_state)
        new_state = {"step": 2, "status": "in_progress"}
        self.engine.update_state(new_state)
        recovered_state = self.engine.recover_workflow(self.workflow_id)
        self.assertEqual(recovered_state, new_state)

    def test_recover_workflow_not_found(self):
        """Test recovering a non-existent workflow."""
        recovered_state = self.engine.recover_workflow("non_existent_workflow")
        self.assertIsNone(recovered_state)

    def test_complete_workflow(self):
        """Test completing a workflow and cleaning up state."""
        self.engine.start_workflow(self.workflow_id, self.initial_state)
        self.engine.complete_workflow()
        recovered_state = self.engine.recover_workflow(self.workflow_id)
        self.assertIsNone(recovered_state)

if __name__ == '__main__':
    unittest.main()
