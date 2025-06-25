import json
from unittest.mock import MagicMock

import pytest

from modules.agents.enhanced_memory_manager import EnhancedMemoryManager
from modules.agents.planning.tactical_planner import TacticalPlanner
from modules.agents.token_tracker import TokenUsage
from utils.llm_manager import LLMManager


@pytest.fixture
def mock_llm_manager():
    """Fixture for a mocked LLMManager."""
    mock = MagicMock(spec=LLMManager)
    mock.chat.return_value = MagicMock(spec=TokenUsage)
    return mock

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
            "steps": [
                {"sub_goal": "First sub-goal", "description": "Do the first thing."},
                {"sub_goal": "Second sub-goal", "description": "Do the second thing."},
            ],
        }
        # The planner expects a raw JSON string, not one wrapped in markdown
        llm_response_text = json.dumps(expected_plan)
        mock_llm_manager.chat.return_value.response_text = llm_response_text

        planner = TacticalPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        objective = "Execute a two-step process."

        # Act
        tactical_plan = planner.generate_tactical_plan(objective)

        # Assert
        assert tactical_plan == expected_plan
        mock_llm_manager.chat.assert_called_once()
        call_args, _ = mock_llm_manager.chat.call_args
        assert objective in call_args[0][1]["content"]

    def test_generate_tactical_plan_invalid_json(self, mock_llm_manager, mock_memory_manager):
        """Test handling of a response with invalid JSON."""
        # Arrange
        llm_response_text = "Here is a plan: { 'steps': [ 'bad json' }"
        mock_llm_manager.chat.return_value.response_text = llm_response_text
        planner = TacticalPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        objective = "An objective that yields invalid JSON."

        # Act
        tactical_plan = planner.generate_tactical_plan(objective)

        # Assert
        assert tactical_plan == {}
        mock_llm_manager.chat.assert_called_once()

    def test_generate_tactical_plan_no_json(self, mock_llm_manager, mock_memory_manager):
        """Test handling of a response with no JSON block."""
        # Arrange
        mock_llm_manager.chat.return_value.response_text = "I am unable to create a plan for this objective."
        planner = TacticalPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        objective = "An objective that yields no JSON."

        # Act
        tactical_plan = planner.generate_tactical_plan(objective)

        # Assert
        assert tactical_plan == {}
        mock_llm_manager.chat.assert_called_once()

    def test_generate_tactical_plan_llm_error(self, mock_llm_manager, mock_memory_manager):
        """Test handling of an exception from the LLMManager."""
        # Arrange
        mock_llm_manager.chat.side_effect = Exception("LLM is offline")
        planner = TacticalPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        objective = "An objective that causes an LLM error."

        # Act
        tactical_plan = planner.generate_tactical_plan(objective)

        # Assert
        assert tactical_plan == {}
        mock_llm_manager.chat.assert_called_once()
