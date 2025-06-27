"""
Unit Tests for Advanced Workflow Execution

This module tests the advanced features of the WorkflowEngine,
including parallel execution, conditional branching, and template execution.
"""

import time
import unittest

from workflow.execution import AdvancedWorkflowEngine


class TestAdvancedWorkflowEngine(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.db_path = "test_workflow_state.db"
        self.engine = AdvancedWorkflowEngine(self.db_path, max_workers=2)
        self.workflow_id = "test_advanced_workflow_1"
        self.initial_state = {"step": 1, "status": "started"}

    def tearDown(self):
        """Clean up test environment after each test."""
        import os

        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_execute_parallel_success(self):
        """Test executing multiple actions in parallel successfully."""
        self.engine.start_workflow(self.workflow_id, self.initial_state)

        def action1():
            time.sleep(1)
            return "Result 1"

        def action2():
            time.sleep(1)
            return "Result 2"

        start_time = time.time()
        results = self.engine.execute_parallel([action1, action2])
        end_time = time.time()

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], "Result 1")
        self.assertEqual(results[1], "Result 2")
        self.assertLess(
            end_time - start_time, 1.5
        )  # Should be parallel, so less than sequential time

    def test_execute_parallel_with_failure(self):
        """Test parallel execution with one action failing, using AlwaysContinue strategy."""
        self.engine.start_workflow(self.workflow_id, self.initial_state)
        self.engine.set_error_strategy("always_continue")

        def action1():
            time.sleep(1)
            return "Result 1"

        def action2():
            time.sleep(1)
            raise ValueError("Action 2 failed")

        results = self.engine.execute_parallel([action1, action2])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], "Result 1")
        self.assertIsNone(results[1])

    def test_execute_conditional_true(self):
        """Test conditional execution where condition evaluates to True."""
        self.engine.start_workflow(self.workflow_id, self.initial_state)

        def condition():
            return True

        def true_action():
            return "True Result"

        def false_action():
            return "False Result"

        result = self.engine.execute_conditional(condition, true_action, false_action)
        self.assertEqual(result, "True Result")

    def test_execute_conditional_false(self):
        """Test conditional execution where condition evaluates to False."""
        self.engine.start_workflow(self.workflow_id, self.initial_state)

        def condition():
            return False

        def true_action():
            return "True Result"

        def false_action():
            return "False Result"

        result = self.engine.execute_conditional(condition, true_action, false_action)
        self.assertEqual(result, "False Result")

    def test_register_and_execute_template(self):
        """Test registering and executing a workflow from a template."""
        template_id = "test_template_1"
        template = {
            "initial_state": {"template": "test"},
            "actions": [
                {"type": "simple", "name": "action1"},
                {
                    "type": "parallel",
                    "actions": [{"name": "parallel1"}, {"name": "parallel2"}],
                },
                {
                    "type": "conditional",
                    "condition": {"name": "cond1"},
                    "true_action": {"name": "true_act"},
                    "false_action": {"name": "false_act"},
                },
            ],
        }
        self.engine.register_template(template_id, template, version=1)
        self.engine.execute_from_template(template_id)
        # If no exceptions are raised, the test passes as the dummy actions log their execution

    def test_migrate_template(self):
        """Test migrating a template from one version to another."""
        template_id = "test_template_2"
        old_template = {"version": "1.0", "data": "old"}
        self.engine.register_template(template_id, old_template, version=1)

        def migration_func(template):
            template["data"] = "new"
            template["version"] = "2.0"
            return template

        self.engine.migrate_workflow(template_id, 1, 2, migration_func)
        self.assertEqual(self.engine.versions[template_id], 2)
        self.assertEqual(self.engine.templates[template_id]["data"], "new")
        self.assertEqual(self.engine.templates[template_id]["version"], "2.0")


if __name__ == "__main__":
    unittest.main()
