import pytest
from unittest.mock import MagicMock, patch

from agents.master_agent import MasterAgent
from agents.agent_manager import AgentManager
from utils.llm_manager import LLMManager
from agents.enhanced_memory_manager import EnhancedMemoryManager
from intelligence.context_awareness_engine import ContextAwarenessEngine
from agents.planning.strategic_planner import StrategicPlanner
from agents.planning.tactical_planner import TacticalPlanner
from agents.planning.operational_planner import OperationalPlanner


@pytest.fixture
def mock_dependencies():
    """Provides a dictionary of mocked dependencies for MasterAgent."""
    return {
        "agent_manager": MagicMock(spec=AgentManager),
        "llm_manager": MagicMock(spec=LLMManager),
        "memory_manager": MagicMock(spec=EnhancedMemoryManager),
        "context_awareness_engine": MagicMock(spec=ContextAwarenessEngine),
        "status_callback": MagicMock(),
        "creator_auth": MagicMock(),
    }


class TestHierarchicalPlanningIntegration:
    """Integration tests for the full Strategic-Tactical-Operational planning flow."""

    def test_full_planning_flow_success(self, mock_dependencies):
        """Test a successful run through the entire planning hierarchy."""
        # Arrange
        master_agent = MasterAgent(**mock_dependencies)
        master_agent.is_running = True  # Simulate that the agent is running

        goal = "Create a comprehensive report on climate change."
        strategic_objectives = ["Gather data on rising sea levels."]
        tactical_plan = {
            "thought": "I need to find reliable sources and extract the data.",
            "steps": [
                {
                    "sub_goal": "Search for scientific papers on sea levels",
                    "description": "Use web search to find papers.",
                },
            ],
        }
        operational_plan = {
            "thought": "I will use the 'search_web' tool.",
            "description": "Search for papers",
            "steps": [
                {
                    "tool_name": "search_web",
                    "arguments": {"query": "scientific papers on rising sea levels"},
                }
            ],
        }

        # Mock the planners and the final execution step
        master_agent.strategic_planner = MagicMock(spec=StrategicPlanner)
        master_agent.tactical_planner = MagicMock(spec=TacticalPlanner)
        master_agent.operational_planner = MagicMock(spec=OperationalPlanner)
        
        master_agent.strategic_planner.generate_strategic_plan.return_value = strategic_objectives
        master_agent.tactical_planner.generate_tactical_plan.return_value = tactical_plan
        master_agent.operational_planner.generate_operational_plan.return_value = operational_plan
        
        with patch.object(
            master_agent, "_execute_plan"
        ) as mock_execute_plan:
            # Act
            master_agent.run_once(goal)

            # Assert
            # Verify that each planner was called correctly
            master_agent.strategic_planner.generate_strategic_plan.assert_called_once_with(goal)
            master_agent.tactical_planner.generate_tactical_plan.assert_called_once_with(strategic_objectives[0])
            master_agent.operational_planner.generate_operational_plan.assert_called_once_with(
                tactical_plan["steps"][0]["sub_goal"],
                mock_dependencies["context_awareness_engine"].get_current_context.return_value,
            )

            # Verify that the final plan was sent for execution
            mock_execute_plan.assert_called_once_with(operational_plan)

            # Verify status callbacks
            assert mock_dependencies["status_callback"].call_count > 5
            # Check for key phase messages
            calls = mock_dependencies["status_callback"].call_args_list
            assert any("Phase 1: Decomposing goal" in str(call) for call in calls)
            assert any("Phase 2: Breaking down objective" in str(call) for call in calls)
            assert any(
                "Executing: Use web search to find papers." in str(call) for call in calls
            )
            assert any("Goal achieved successfully" in str(call) for call in calls)
