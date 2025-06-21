import pytest
import json
from unittest.mock import MagicMock

from agents.planning.tactical_planner import TacticalPlanner
from utils.llm_manager import LLMManager
from agents.enhanced_memory_manager import EnhancedMemoryManager

@pytest.fixture
def mock_llm_manager():
    """Fixture for a mocked LLMManager."""
    return MagicMock(spec=LLMManager)

@pytest.fixture
def mock_memory_manager():
    """Fixture for a mocked EnhancedMemoryManager."""
    return MagicMock(spec=EnhancedMemoryManager)

class TestTacticalPlanner:
    """Tests for the TacticalPlanner class."""

    def test_generate_tactical_plan_success(self, mock_llm_manager, mock_memory_manager):
        """Test successful generation of a tactical plan from a valid JSON response."""
        # Arrange
        expected_plan = {
            "thought": "The user wants to do this, so I should do that.",
            "steps": [
                {"sub_goal": "First sub-goal", "description": "Do the first thing."},
                {"sub_goal": "Second sub-goal", "description": "Do the second thing."}
            ]
        }
        llm_response_content = f"```json\n{json.dumps(expected_plan)}\n```"
        mock_llm_manager.llm.invoke.return_value.content = llm_response_content

        planner = TacticalPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        objective = "Execute a two-step process."

        # Act
        tactical_plan = planner.generate_tactical_plan(objective)

        # Assert
        assert tactical_plan == expected_plan
        mock_llm_manager.llm.invoke.assert_called_once()
        call_args, _ = mock_llm_manager.llm.invoke.call_args
        assert objective in str(call_args[0])

    def test_generate_tactical_plan_invalid_json(self, mock_llm_manager, mock_memory_manager):
        """Test handling of a response with invalid JSON."""
        # Arrange
        llm_response_content = "```json\n{\"thought\": \"this is broken...\"\n```"
        mock_llm_manager.llm.invoke.return_value.content = llm_response_content
        planner = TacticalPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        objective = "An objective that yields invalid JSON."

        # Act
        tactical_plan = planner.generate_tactical_plan(objective)

        # Assert
        assert tactical_plan == {}
        mock_llm_manager.llm.invoke.assert_called_once()

    def test_generate_tactical_plan_no_json(self, mock_llm_manager, mock_memory_manager):
        """Test handling of a response with no JSON block."""
        # Arrange
        mock_llm_manager.llm.invoke.return_value.content = "I am unable to create a plan for this objective."
        planner = TacticalPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        objective = "An objective that yields no JSON."

        # Act
        tactical_plan = planner.generate_tactical_plan(objective)

        # Assert
        assert tactical_plan == {}
        mock_llm_manager.llm.invoke.assert_called_once()

    def test_generate_tactical_plan_llm_error(self, mock_llm_manager, mock_memory_manager):
        """Test handling of an exception from the LLMManager."""
        # Arrange
        mock_llm_manager.llm.invoke.side_effect = Exception("LLM is offline")
        planner = TacticalPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        objective = "An objective that causes an LLM error."

        # Act
        tactical_plan = planner.generate_tactical_plan(objective)

        # Assert
        assert tactical_plan == {}
        mock_llm_manager.llm.invoke.assert_called_once()

