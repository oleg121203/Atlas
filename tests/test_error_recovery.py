import unittest
from unittest.mock import MagicMock, patch

from agents.agent_manager import AgentManager, ToolNotFoundError, InvalidToolArgumentsError
from utils.llm_manager import LLMManager
from agents.master_agent import MasterAgent
from agents.memory_manager import MemoryManager


class TestErrorRecovery(unittest.TestCase):

    def setUp(self):
        """Set up a MasterAgent with mock components for testing."""
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_agent_manager = MagicMock(spec=AgentManager)
        self.mock_agent_manager._agents = {'some_agent': MagicMock()}
        self.mock_memory_manager = MagicMock(spec=MemoryManager)
        self.mock_status_callback = MagicMock()

        self.master_agent = MasterAgent(
            llm_manager=self.mock_llm_manager,
            agent_manager=self.mock_agent_manager,
            memory_manager=self.mock_memory_manager,
            status_callback=self.mock_status_callback
        )
        self.master_agent.logger = MagicMock()
        self.master_agent.is_running = True
        self.master_agent.MAX_RETRIES = 1

    @patch('agents.master_agent.MasterAgent._execute_plan')
    @patch('agents.master_agent.MasterAgent._generate_plan')
    @patch('agents.master_agent.MasterAgent._decompose_goal')
    def test_replanning_after_generic_failure(self, mock_decompose_goal, mock_generate_plan, mock_execute_plan):
        """
        Test that the agent attempts to create a recovery plan after a generic task failure.
        """
        initial_goal = "test goal"
        sub_goal = "test sub_goal"
        initial_plan = {"steps": [{"tool": "test_tool", "args": {}, "description": "A test step"}]}
        execution_error = Exception("Tool failed spectacularly")
        failed_step_details = initial_plan['steps'][0]

        mock_decompose_goal.return_value = [sub_goal]
        mock_generate_plan.return_value = initial_plan
        mock_execute_plan.side_effect = [(execution_error, failed_step_details, {}), (None, None, {})]

        with patch.object(self.master_agent, 'pause', MagicMock()):
            self.master_agent.run_once(initial_goal)

        self.assertEqual(mock_generate_plan.call_count, 2)
        last_call_args = mock_generate_plan.call_args[0]
        self.assertIn("The original sub-goal was", last_call_args[0])
        self.assertIn("failed at the step", last_call_args[0])

    @patch('agents.master_agent.MasterAgent._execute_plan')
    @patch('agents.master_agent.MasterAgent._generate_plan')
    @patch('agents.master_agent.MasterAgent._decompose_goal')
    def test_recovery_from_tool_not_found_error(self, mock_decompose_goal, mock_generate_plan, mock_execute_plan):
        """
        Test that the agent generates a specific recovery plan when a tool is not found.
        """
        initial_goal = "use a missing tool"
        sub_goal = "use a missing tool"
        plan = {"steps": [{"tool": "missing_tool", "args": {}, "description": "Use the missing tool"}]}
        error = ToolNotFoundError("Tool 'missing_tool' not found.")
        failed_step_details = plan['steps'][0]

        mock_decompose_goal.return_value = [sub_goal]
        mock_generate_plan.return_value = plan
        mock_execute_plan.side_effect = [(error, failed_step_details, {}), (None, None, {})]

        with patch.object(self.master_agent, 'pause', MagicMock()):
            self.master_agent.run_once(initial_goal)

        self.assertEqual(mock_generate_plan.call_count, 2)
        recovery_goal_arg = mock_generate_plan.call_args[0][0]
        self.assertIn("The plan failed because the tool 'missing_tool' does not exist", recovery_goal_arg)
        self.assertIn("Your new goal is to first create the missing tool", recovery_goal_arg)

    @patch('agents.master_agent.MasterAgent._execute_plan')
    @patch('agents.master_agent.MasterAgent._generate_plan')
    @patch('agents.master_agent.MasterAgent._decompose_goal')
    def test_recovery_from_invalid_tool_arguments_error(self, mock_decompose_goal, mock_generate_plan, mock_execute_plan):
        """
        Test that the agent generates a specific recovery plan for invalid tool arguments.
        """
        initial_goal = "use a tool with bad args"
        sub_goal = "use a tool with bad args"
        plan = {"steps": [{"tool": "bad_arg_tool", "args": {"wrong": "arg"}, "description": "Use tool with bad args"}]}
        error = InvalidToolArgumentsError("Invalid arguments. Doc: 'This tool does something.'")
        failed_step_details = plan['steps'][0]

        mock_decompose_goal.return_value = [sub_goal]
        mock_generate_plan.return_value = plan
        mock_execute_plan.side_effect = [(error, failed_step_details, {}), (None, None, {})]

        with patch.object(self.master_agent, 'pause', MagicMock()):
            self.master_agent.run_once(initial_goal)

        self.assertEqual(mock_generate_plan.call_count, 2)
        recovery_goal_arg = mock_generate_plan.call_args[0][0]
        self.assertIn("due to invalid arguments", recovery_goal_arg)
        self.assertIn("Pay close attention to the tool's documentation", recovery_goal_arg)
        self.assertIn("This tool does something.", recovery_goal_arg)


if __name__ == '__main__':
    unittest.main()
