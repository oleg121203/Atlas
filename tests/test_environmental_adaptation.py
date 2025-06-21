"""Tests for environmental adaptation logic in MasterAgent._execute_objective_with_retries."""

import unittest
from typing import Any, Dict

from agents.master_agent import MasterAgent, PlanExecutionError


class _StubLLMManager:
    """Minimal stub for LLMManager (not used by these tests)."""

    def chat(self, *args: Any, **kwargs: Any) -> Any:
        class _Resp:  # pylint: disable=too-few-public-methods
            response_text = ""
        return _Resp()


class _StubMemoryManager:
    """Minimal stub for MemoryManager (not used by these tests)."""


class _StubAgentManager:
    """Bare-bones AgentManager stub (no tool execution needed here)."""

    def __init__(self) -> None:
        self.has_agents = True  # Skip default-agent registration
        self.master_agent_update_callback = None  # type: ignore[attr-defined]


class _ChangingContextEngine:
    """Returns a monotonically increasing context so each call differs."""

    def __init__(self) -> None:
        self._counter = 0

    def get_current_context(self) -> Dict[str, Any]:
        self._counter += 1
        return {"version": self._counter}


class _SpyMasterAgent(MasterAgent):
    """Overrides _execute_plan to simulate a failure on first call."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.plan_calls = 0

    # pylint: disable=arguments-differ
    def _execute_plan(self, plan: Dict[str, Any]) -> None:  # type: ignore
        self.plan_calls += 1
        if self.plan_calls == 1:
            raise PlanExecutionError("Simulated failure", step={}, original_exception=Exception("boom"))
        # On second attempt succeed (no action needed)

    def _generate_plan(self, goal: str) -> Dict[str, Any]:
        """Return a dummy plan (content irrelevant for this test)."""
        return {"steps": [{"tool_name": "dummy", "description": "", "arguments": {}}]}


class TestEnvironmentalAdaptation(unittest.TestCase):
    """Verify that MasterAgent detects environment change and retries without calling recovery logic."""

    def setUp(self) -> None:
        self.master_agent = _SpyMasterAgent(
            agent_manager=_StubAgentManager(),
            llm_manager=_StubLLMManager(),
            memory_manager=_StubMemoryManager(),
            context_awareness_engine=_ChangingContextEngine(),
        )

    def test_environment_change_triggers_retry(self):
        # Mark running to bypass is_running guard if present.
        self.master_agent.is_running = True  # type: ignore

        # Should complete without raising despite first attempt failing.
        self.master_agent._execute_objective_with_retries("dummy goal")  # type: ignore (protected access)

        # _execute_plan should have been invoked twice: fail -> env changed -> retry.
        self.assertEqual(
            self.master_agent.plan_calls,
            2,
            "Environment change did not cause a re-execution of the plan.",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
