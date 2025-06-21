import unittest
from unittest.mock import MagicMock, patch

from agents.agent_manager import (
    AgentManager,
    InvalidToolArgumentsError,
    ToolNotFoundError,
)
from agents.master_agent import MasterAgent, PlanExecutionError
from agents.memory_manager import MemoryManager
from agents.tool_creator_agent import ToolCreatorAgent
from intelligence.context_awareness_engine import ContextAwarenessEngine
from utils.llm_manager import LLMManager


class TestMasterAgentEnvironmentalAdaptation(unittest.TestCase):
    """
    Tests for the MasterAgent's environmental adaptation and error recovery logic.
    These tests simulate various execution errors and validate that the agent
    responds correctly by creating tools, replanning, retrying, or halting.
    """
    def setUp(self):
        """Set up the test environment with a MasterAgent and mocked dependencies."""
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_memory_manager = MagicMock(spec=MemoryManager)
        self.mock_agent_manager = MagicMock(spec=AgentManager)
        self.mock_context_engine = MagicMock(spec=ContextAwarenessEngine)
        self.mock_status_callback = MagicMock()

        # Mock the tool creator agent, which is a dependency of AgentManager
        self.mock_agent_manager.tool_creator_agent = MagicMock(spec=ToolCreatorAgent)

        self.master_agent = MasterAgent(
            llm_manager=self.mock_llm_manager,
            memory_manager=self.mock_memory_manager,
            agent_manager=self.mock_agent_manager,
            context_awareness_engine=self.mock_context_engine,
            status_callback=self.mock_status_callback,
        )
        self.master_agent.is_running = True
        self.master_agent.MAX_RETRIES = 3

    def _get_simple_plan(self, tool_name="test_tool", args=None):
        """Helper to create a simple, valid plan structure."""
        if args is None:
            args = {"arg1": "value1"}
        return {
            "steps": [
                {
                    "step_id": 1,
                    "description": f"Use the {tool_name} tool.",
                    "tool_name": tool_name,
                    "args": args,
                },
            ],
        }

    @patch("agents.master_agent.MasterAgent._generate_plan")
    def test_successful_recovery_after_tool_not_found(self, mock_generate_plan):
        """Test that the agent successfully recovers after a ToolNotFoundError."""
        goal = "Use a tool that doesn't exist yet."
        tool_name = "magical_tool"
        mock_generate_plan.return_value = self._get_simple_plan(tool_name=tool_name)

        def execute_tool_side_effect(*args, **kwargs):
            if self.mock_agent_manager.execute_tool.call_count == 1:
                raise ToolNotFoundError(f"Tool '{tool_name}' not found.")
            return {"status": "success", "output": "Tool executed successfully after creation."}
        self.mock_agent_manager.execute_tool.side_effect = execute_tool_side_effect

        self.mock_agent_manager.tool_creator_agent.create_tool.return_value = {"status": "success"}

        self.master_agent._execute_objective_with_retries(goal)

        self.mock_agent_manager.tool_creator_agent.create_tool.assert_called_once()
        self.assertEqual(self.mock_agent_manager.execute_tool.call_count, 2)

    @patch("agents.master_agent.MasterAgent._generate_plan")
    def test_successful_recovery_after_invalid_tool_arguments(self, mock_generate_plan):
        """Test successful recovery via replanning after InvalidToolArgumentsError."""
        goal = "Use a tool with bad arguments."
        mock_generate_plan.return_value = self._get_simple_plan()

        error_message = "Invalid arguments."
        def execute_tool_side_effect(*args, **kwargs):
            if self.mock_agent_manager.execute_tool.call_count == 1:
                raise InvalidToolArgumentsError(error_message)
            return {"status": "success", "output": "Replanned and executed successfully."}
        self.mock_agent_manager.execute_tool.side_effect = execute_tool_side_effect

        self.master_agent._execute_objective_with_retries(goal)

        self.assertEqual(mock_generate_plan.call_count, 2)
        second_call_args, _ = mock_generate_plan.call_args_list[1]
        self.assertIn(error_message, second_call_args[0])

    @patch("agents.master_agent.MasterAgent._generate_plan")
    def test_successful_recovery_after_generic_error(self, mock_generate_plan):
        """Test successful recovery after one generic, transient error."""
        goal = "Perform a flaky operation."
        mock_generate_plan.return_value = self._get_simple_plan()

        def execute_tool_side_effect(*args, **kwargs):
            if self.mock_agent_manager.execute_tool.call_count == 1:
                raise Exception("A transient error occurred.")
            return {"status": "success", "output": "It worked this time."}
        self.mock_agent_manager.execute_tool.side_effect = execute_tool_side_effect

        self.master_agent._execute_objective_with_retries(goal)

        self.assertEqual(self.mock_agent_manager.execute_tool.call_count, 2)

    @patch("agents.master_agent.MasterAgent._generate_plan")
    def test_execution_stops_after_max_retries(self, mock_generate_plan):
        """Test that execution halts after exceeding the maximum number of retries."""
        goal = "Perform an operation that is always broken."
        mock_generate_plan.return_value = self._get_simple_plan()

        self.mock_agent_manager.execute_tool.side_effect = Exception("This is always broken.")

        with self.assertRaises(PlanExecutionError):
            self.master_agent._execute_objective_with_retries(goal)

        self.assertEqual(self.mock_agent_manager.execute_tool.call_count, self.master_agent.MAX_RETRIES)

if __name__ == "__main__":
    unittest.main()
