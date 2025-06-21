import pytest
from unittest.mock import MagicMock, patch

from agents.planning.strategic_planner import StrategicPlanner
from utils.llm_manager import LLMManager
from agents.enhanced_memory_manager import EnhancedMemoryManager

@pytest.fixture
def mock_llm_manager():
    """Fixture for a mocked LLMManager."""
    mock = MagicMock(spec=LLMManager)
    return mock

@pytest.fixture
def mock_memory_manager():
    """Fixture for a mocked EnhancedMemoryManager."""
    mock = MagicMock(spec=EnhancedMemoryManager)
    return mock

class TestStrategicPlanner:
    """Tests for the StrategicPlanner class."""

    def test_generate_strategic_plan_success(self, mock_llm_manager, mock_memory_manager):
        """Test successful generation of a strategic plan."""
        # Arrange
        mock_llm_manager.llm.invoke.return_value.content = ( """
Here is the strategic plan:
1. First objective.
2. Second objective.
3. Third objective.
""" )

        planner = StrategicPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        goal = "Achieve world peace."

        # Act
        strategic_plan = planner.generate_strategic_plan(goal)

        # Assert
        assert strategic_plan == [
            "First objective.",
            "Second objective.",
            "Third objective."
        ]
        mock_llm_manager.llm.invoke.assert_called_once()
        # Verify that the prompt passed to the LLM contains the goal
        call_args, _ = mock_llm_manager.llm.invoke.call_args
        assert goal in str(call_args[0])

    def test_generate_strategic_plan_empty_response(self, mock_llm_manager, mock_memory_manager):
        """Test handling of an empty or malformed response from the LLM."""
        # Arrange
        mock_llm_manager.llm.invoke.return_value.content = "Sorry, I can't help with that."
        planner = StrategicPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        goal = "A goal that results in an empty plan."

        # Act
        strategic_plan = planner.generate_strategic_plan(goal)

        # Assert
        assert strategic_plan == []
        mock_llm_manager.llm.invoke.assert_called_once()

    def test_generate_strategic_plan_llm_error(self, mock_llm_manager, mock_memory_manager):
        """Test handling of an exception raised by the LLMManager."""
        # Arrange
        mock_llm_manager.llm.invoke.side_effect = Exception("LLM API is down")
        planner = StrategicPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        goal = "A goal that causes an LLM error."

        # Act
        strategic_plan = planner.generate_strategic_plan(goal)

        # Assert
        assert strategic_plan == []
        mock_llm_manager.llm.invoke.assert_called_once()
