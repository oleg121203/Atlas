"""Tests for dynamic tool creation logic in MasterAgent._execute_plan."""

from typing import Any, Dict
import unittest

from agents.master_agent import MasterAgent
from agents.agent_manager import ToolNotFoundError


class _StubLLMManager:  # noqa: D401 (simple stub)
    """Minimal stub for LLMManager (not used by these tests)."""

    def chat(self, *args: Any, **kwargs: Any) -> Any:  # noqa: D401
        class _Resp:  # pylint: disable=too-few-public-methods
            response_text = ""
        return _Resp()


class _StubMemoryManager:  # noqa: D401
    """Minimal stub for MemoryManager (not used by these tests)."""


class _StubContextAwarenessEngine:  # noqa: D401
    """Minimal stub for ContextAwarenessEngine (not used by these tests)."""


class _StubAgentManager:
    """Stubbed AgentManager that simulates missing tools then dynamic creation."""

    def __init__(self) -> None:
        self.has_agents = True  # Skip default-agent registration
        self.created_tools = set()
        self.calls = []  # type: list[str]
        # MasterAgent will set this attribute; pre-create for type checkers.
        self.master_agent_update_callback = None  # type: ignore

    # ---------------------------------------------------------------------
    # Core API used by MasterAgent
    # ---------------------------------------------------------------------
    def execute_tool(self, tool_name: str, args: Dict[str, Any]):  # noqa: D401, ANN001
        """Simulate execution or creation of tools."""
        self.calls.append(tool_name)
        # Simulate dynamic tool creation helper
        if tool_name == "create_tool":
            self.created_tools.add(args["tool_name"])
            return "created"

        # Normal tool execution path
        if tool_name not in self.created_tools:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found")
        return "success"


class TestDynamicToolCreation(unittest.TestCase):
    """Verify that MasterAgent triggers dynamic tool creation when a tool is missing."""

    def setUp(self) -> None:  # noqa: D401
        self.agent_manager = _StubAgentManager()
        self.master_agent = MasterAgent(
            agent_manager=self.agent_manager,
            llm_manager=_StubLLMManager(),
            memory_manager=_StubMemoryManager(),
            context_awareness_engine=_StubContextAwarenessEngine(),
        )

    def test_missing_tool_triggers_creation(self):  # noqa: D401
        plan = {
            "steps": [
                {
                    "tool_name": "dummy_tool",
                    "description": "Execute dummy tool",
                    "arguments": {},
                }
            ]
        }

        # Mark agent as running so _execute_plan proceeds.
        self.master_agent.is_running = True  # type: ignore
        # Should not raise exception despite the tool initially missing.
        self.master_agent._execute_plan(plan)  # type: ignore (accessing protected member for test)
        self.master_agent.is_running = False

        # Tool should have been dynamically created.
        self.assertIn("dummy_tool", self.agent_manager.created_tools)

        # Call sequence expectation: dummy_tool -> create_tool -> dummy_tool
        self.assertEqual(
            self.agent_manager.calls,
            ["dummy_tool", "create_tool", "dummy_tool"],
            "Unexpected tool invocation sequence during dynamic creation process.",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
