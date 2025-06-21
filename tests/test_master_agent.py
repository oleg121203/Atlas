import pytest
from unittest.mock import create_autospec, PropertyMock, MagicMock

from agents.master_agent import MasterAgent
from agents.agent_manager import AgentManager
from utils.llm_manager import LLMManager
from agents.memory_manager import MemoryManager
from intelligence.context_awareness_engine import ContextAwarenessEngine
from agents.planning.strategic_planner import StrategicPlanner
from agents.planning.tactical_planner import TacticalPlanner
from agents.planning.operational_planner import OperationalPlanner


@pytest.fixture
def master_agent_with_mocks():
    """Provides a MasterAgent instance with all external dependencies mocked."""
    mock_llm_manager = create_autospec(LLMManager, instance=True)
    mock_agent_manager = create_autospec(AgentManager, instance=True)
    mock_memory_manager = create_autospec(MemoryManager, instance=True)
    mock_context_engine = create_autospec(ContextAwarenessEngine, instance=True)

    master_agent = MasterAgent(
        llm_manager=mock_llm_manager,
        agent_manager=mock_agent_manager,
        memory_manager=mock_memory_manager,
        context_awareness_engine=mock_context_engine,
        status_callback=MagicMock(),
    )

    # Monkeypatch planners and set state for testing
    master_agent.strategic_planner = create_autospec(StrategicPlanner, instance=True)
    master_agent.tactical_planner = create_autospec(TacticalPlanner, instance=True)
    master_agent.operational_planner = create_autospec(OperationalPlanner, instance=True)
    master_agent.is_running = True
    type(mock_agent_manager).has_agents = PropertyMock(return_value=True)

    yield master_agent


def test_run_once_full_planning_loop_success(master_agent_with_mocks):
    """Integration test for a successful run of the full planning and execution loop."""
    # Arrange
    master_agent = master_agent_with_mocks
    goal = "Test the system"
    strategic_objectives = ["Objective 1"]
    tactical_plan = {"steps": [{"sub_goal": "Execute tool", "description": "Run the test tool."}]}
    operational_plan = {"steps": [{"tool_name": "test_tool", "arguments": {"arg1": "value1"}}], "description": "Test op plan"}
    context = {}

    # Mock the outputs of each planner and dependency
    master_agent.strategic_planner.generate_strategic_plan.return_value = strategic_objectives
    master_agent.tactical_planner.generate_tactical_plan.return_value = tactical_plan
    master_agent.operational_planner.generate_operational_plan.return_value = operational_plan
    master_agent.agent_manager.execute_tool.return_value = "Tool executed successfully"
    master_agent.context_awareness_engine.get_current_context.return_value = context

    # Act
    master_agent.run_once(goal)

    # Assert
    master_agent.strategic_planner.generate_strategic_plan.assert_called_once_with(goal)
    master_agent.tactical_planner.generate_tactical_plan.assert_called_once_with(strategic_objectives[0])
    master_agent.operational_planner.generate_operational_plan.assert_called_once_with(
        tactical_plan['steps'][0]['sub_goal'], context
    )
    master_agent.agent_manager.execute_tool.assert_called_once_with(
        operational_plan['steps'][0]['tool_name'],
        operational_plan['steps'][0]['arguments']
    )
    assert master_agent.status_callback.call_count > 0


def test_run_once_recovers_from_execution_error(master_agent_with_mocks):
    """
    Integration test to verify that the agent can recover from an execution error
    by using the LLM-powered self-correction mechanism to generate a new plan.
    """
    # Arrange
    master_agent = master_agent_with_mocks
    goal = "Test error handling"
    tool_error = ValueError("Tool failed")
    recovery_goal = "Analyze the previous tool failure and find an alternative tool."

    # Mock plans for initial attempt and recovery attempt
    failing_op_plan = {"steps": [{"tool_name": "failing_tool", "arguments": {}}], "description": "Failing op plan"}
    successful_op_plan = {"steps": [{"tool_name": "alternative_tool", "arguments": {}}], "description": "Successful recovery op plan"}

    # Mock the full planning and execution pipeline with side_effects
    master_agent.strategic_planner.generate_strategic_plan.side_effect = [
        ["Initial Objective"],  # First call
        ["Recovery Objective"]  # Second call
    ]
    master_agent.tactical_planner.generate_tactical_plan.side_effect = [
        {"steps": [{"sub_goal": "Execute failing tool"}]},
        {"steps": [{"sub_goal": "Execute alternative tool"}]}
    ]
    master_agent.operational_planner.generate_operational_plan.side_effect = [
        failing_op_plan,
        successful_op_plan
    ]
    master_agent.agent_manager.execute_tool.side_effect = [
        tool_error,  # First call fails
        "Alternative tool executed successfully"  # Second call succeeds
    ]

    # Mock the LLM call within the recovery mechanism
    master_agent.llm_manager.chat.return_value = recovery_goal

    # Act
    master_agent.run_once(goal)

    # Assert
    # 1. Verify the meta-cognitive loop was engaged
    master_agent.llm_manager.chat.assert_called_once()

    # 2. Verify the agent tried the failing tool first, then the alternative
    assert master_agent.agent_manager.execute_tool.call_count == 2
    master_agent.agent_manager.execute_tool.assert_any_call("failing_tool", {})
    master_agent.agent_manager.execute_tool.assert_any_call("alternative_tool", {})

    # 3. Verify the agent retried planning with the new recovery goal
    assert master_agent.strategic_planner.generate_strategic_plan.call_count == 2
    master_agent.strategic_planner.generate_strategic_plan.assert_any_call(goal)
    master_agent.strategic_planner.generate_strategic_plan.assert_any_call(recovery_goal)
