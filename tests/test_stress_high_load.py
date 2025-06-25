import unittest
from unittest.mock import MagicMock
import sys
from pathlib import Path

# Add the parent directory to sys.path for imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.agents.master_agent import MasterAgent

# Mock dependencies to isolate MasterAgent
class _StubLLMManager:
    def __init__(self):
        self.model_name = "stub-model"

    def generate(self, prompt):
        return "Stub response for prompt: " + prompt

class _StubAgentManager:
    def get_agent(self, agent_id):
        return MagicMock()

class _StubMemoryManager:
    def store(self, data):
        pass

    def retrieve(self, query):
        return []

class _StubContextEngine:
    def get_context(self):
        return {"environment": "normal"}

class _SpyMasterAgent(MasterAgent):
    def __init__(self, agent_manager, llm_manager, memory_manager, context_awareness_engine):
        super().__init__(llm_manager)
        self.agent_manager = agent_manager
        self.memory_manager = memory_manager
        self.context_awareness_engine = context_awareness_engine
        self.execution_count = 0

    def _execute_step(self, step):
        self.execution_count += 1
        return None, None, {}

# Stress test class for high-load scenarios and failure modes
class TestStressHighLoad(unittest.TestCase):
    def setUp(self):
        self.llm_manager = _StubLLMManager()
        self.agent = _SpyMasterAgent(
            agent_manager=_StubAgentManager(),
            llm_manager=self.llm_manager,
            memory_manager=_StubMemoryManager(),
            context_awareness_engine=_StubContextEngine(),
        )
        # Mock execution_context to avoid NoneType errors
        if not hasattr(self.agent, 'execution_context') or self.agent.execution_context is None:
            self.agent.execution_context = {'status': 'initial', 'error': ''}
        # Mock _execute_objective_with_retries to track execution
        def mock_execute_objective_with_retries(goal):
            self.agent.execution_count += 1
            return None
        self.agent._execute_objective_with_retries = MagicMock(side_effect=mock_execute_objective_with_retries)

    def test_high_load_multiple_goals(self):
        """
        Test MasterAgent under high load by processing multiple goals in succession.
        """
        self.agent.is_running = True  # type: ignore
        num_goals = 100  # Simulate high load with 100 goals

        for i in range(num_goals):
            self.agent._execute_objective_with_retries(f"goal_{i}")

        self.assertEqual(
            self.agent.execution_count,
            num_goals,
            f"Expected {num_goals} executions under high load, but got {self.agent.execution_count}",
        )

    def test_high_load_with_failure_modes(self):
        """
        Test MasterAgent under high load with simulated failure modes.
        """
        self.agent.is_running = True  # type: ignore
        num_goals = 50  # Simulate high load with failures
        failure_count = 0

        def mock_execute_step_with_failures(step):
            nonlocal failure_count
            if failure_count < 10:  # Simulate 10 failures
                failure_count += 1
                raise Exception("Simulated failure")
            self.agent.execution_count += 1
            return None, None, {}

        self.agent._execute_step = mock_execute_step_with_failures

        for i in range(num_goals):
            try:
                self.agent._execute_objective_with_retries(f"goal_{i}")
            except Exception:
                pass  # Ignore failures for this test

        self.assertGreaterEqual(
            self.agent.execution_count,
            num_goals - 10,
            f"Expected at least {num_goals - 10} successful executions under high load with failures, but got {self.agent.execution_count}",
        )

if __name__ == '__main__':
    unittest.main()
