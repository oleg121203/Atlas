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
        self.mock_context_awareness_engine = MagicMock()
        self.mock_status_callback = MagicMock()

        self.master_agent = MasterAgent(
            llm_manager=self.mock_llm_manager,
            agent_manager=self.mock_agent_manager,
            memory_manager=self.mock_memory_manager,
            context_awareness_engine=self.mock_context_awareness_engine,
            status_callback=self.mock_status_callback
        )
        self.master_agent.logger = MagicMock()
        self.master_agent.is_running = True
        self.master_agent.MAX_RETRIES = 1

    @patch('agents.master_agent.MasterAgent._execute_plan')
    @patch('agents.master_agent.MasterAgent._execute_objective_with_retries')
    @patch('agents.master_agent.MasterAgent._decompose_goal')
    def test_replanning_after_generic_failure(self, mock_decompose_goal, mock_execute_objective, mock_execute_plan):
        """
        Test that the agent attempts to create a recovery plan after a generic task failure.
        """
        initial_goal = "test goal"
        sub_goal = "test sub_goal"
        initial_plan = {"steps": [{"tool": "test_tool", "args": {}, "description": "A test step"}]}
        execution_error = Exception("Tool failed spectacularly")
        failed_step_details = initial_plan['steps'][0]

        mock_decompose_goal.return_value = [sub_goal]
        mock_execute_objective.return_value = None
        mock_execute_plan.side_effect = [(execution_error, failed_step_details, {}), (None, None, {})]

        with patch.object(self.master_agent, 'pause', MagicMock()):
            self.master_agent.run_once(initial_goal)

        mock_execute_objective.assert_called_once_with(initial_goal)

    @patch('agents.master_agent.MasterAgent._execute_plan')
    @patch('agents.master_agent.MasterAgent._execute_objective_with_retries')
    @patch('agents.master_agent.MasterAgent._decompose_goal')
    def test_recovery_from_tool_not_found_error(self, mock_decompose_goal, mock_execute_objective, mock_execute_plan):
        """
        Test that the agent handles a missing tool by falling back to a recovery plan.
        """
        initial_goal = "test goal"
        sub_goal = "test sub_goal"
        execution_error = ToolNotFoundError("Tool 'missing_tool' not found")
        failed_step_details = {"tool": "missing_tool", "args": {}}

        mock_decompose_goal.return_value = [sub_goal]
        mock_execute_objective.return_value = None
        mock_execute_plan.side_effect = [(execution_error, failed_step_details, {}), (None, None, {})]

        with patch.object(self.master_agent, 'pause', MagicMock()):
            self.master_agent.run_once(initial_goal)

        mock_execute_objective.assert_called_once_with(initial_goal)

    @patch('agents.master_agent.MasterAgent._execute_plan')
    @patch('agents.master_agent.MasterAgent._execute_objective_with_retries')
    @patch('agents.master_agent.MasterAgent._decompose_goal')
    def test_recovery_from_invalid_tool_arguments_error(self, mock_decompose_goal, mock_execute_objective, mock_execute_plan):
        """
        Test that the agent handles invalid tool arguments by falling back to a recovery plan.
        """
        initial_goal = "test goal"
        sub_goal = "test sub_goal"
        execution_error = InvalidToolArgumentsError("Invalid arguments for tool 'test_tool'")
        failed_step_details = {"tool": "test_tool", "args": {"invalid": "value"}}

        mock_decompose_goal.return_value = [sub_goal]
        mock_execute_objective.return_value = None
        mock_execute_plan.side_effect = [(execution_error, failed_step_details, {}), (None, None, {})]

        with patch.object(self.master_agent, 'pause', MagicMock()):
            self.master_agent.run_once(initial_goal)

        mock_execute_objective.assert_called_once_with(initial_goal)


if __name__ == '__main__':
    unittest.main()
