import time
import unittest
from unittest.mock import patch

from advanced_workflow_debugging import WorkflowDebugger


class TestWorkflowDebugger(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        self.debugger = WorkflowDebugger()

    def test_set_and_remove_breakpoint(self):
        """Test setting and removing breakpoints."""
        self.debugger.set_breakpoint("wf1", "step1")
        self.assertIn("wf1:step1", self.debugger.breakpoints)
        self.debugger.remove_breakpoint("wf1", "step1")
        self.assertNotIn("wf1:step1", self.debugger.breakpoints)

    def test_watch_variable(self):
        """Test watching variables."""
        self.debugger.watch_variable("test_var", 100)
        self.assertIn("test_var", self.debugger.watch_variables)
        self.assertEqual(self.debugger.watch_variables["test_var"], 100)

    def test_start_and_end_debug_session(self):
        """Test starting and ending a debug session."""
        self.debugger.start_debug_session("wf2")
        self.assertEqual(self.debugger.current_workflow_id, "wf2")
        self.assertIn("wf2", self.debugger.profiling_data)
        self.debugger.end_debug_session()
        self.assertIsNone(self.debugger.current_workflow_id)

    @patch("builtins.print")
    def test_before_step_breakpoint(self, mock_print):
        """Test behavior before a step with a breakpoint."""
        self.debugger.start_debug_session("wf3")
        self.debugger.set_breakpoint("wf3", "step2")
        with patch.object(self.debugger, "_handle_user_input") as mock_handle:
            self.debugger.before_step("wf3", "step2", lambda x: x, 5)
            self.assertTrue(self.debugger.paused)
            mock_handle.assert_called()

    def test_before_step_no_breakpoint(self):
        """Test behavior before a step without a breakpoint."""
        self.debugger.start_debug_session("wf4")
        self.debugger.before_step("wf4", "step3", lambda x: x, 10)
        self.assertFalse(self.debugger.paused)

    def test_after_step(self):
        """Test behavior after a step execution."""
        self.debugger.start_debug_session("wf5")
        self.debugger.before_step("wf5", "step4", lambda x: x, 15)
        # Simulate some time passing
        time.sleep(0.1)
        self.debugger.after_step("wf5", "step4", 25)
        self.assertIn("wf5:step4", self.debugger.execution_state)
        self.assertTrue(self.debugger.execution_state["wf5:step4"]["completed"])
        self.assertGreater(self.debugger.execution_state["wf5:step4"]["duration"], 0)
        self.assertEqual(self.debugger.execution_state["wf5:step4"]["result"], 25)

    def test_visual_debug_representation(self):
        """Test generating a visual debug representation."""
        self.debugger.start_debug_session("wf6")
        self.debugger.set_breakpoint("wf6", "step5")
        self.debugger.watch_variable("debug_var", 200)
        self.debugger.before_step("wf6", "step5", lambda x: x, 30)
        time.sleep(0.1)
        self.debugger.after_step("wf6", "step5", 40)
        representation = self.debugger.get_visual_debug_representation("wf6")
        self.assertIn("Debug State for Workflow wf6", representation)
        self.assertIn("Breakpoint", representation)
        self.assertIn("Watched Variables", representation)
        self.assertIn("Execution State", representation)


if __name__ == "__main__":
    unittest.main()
