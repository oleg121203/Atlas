from unittest.mock import MagicMock

import pytest

from agents.enhanced_memory_manager import EnhancedMemoryManager
from agents.planning.strategic_planner import StrategicPlanner
from agents.token_tracker import TokenUsage
from utils.llm_manager import LLMManager


@pytest.fixture
def mock_llm_manager():
    """Fixture for a mocked LLMManager."""
    mock = MagicMock(spec=LLMManager)
    # Mock the result object that the chat method is expected to return
    mock.chat.return_value = MagicMock(spec=TokenUsage)
    return mock

@pytest.fixture
def mock_memory_manager():
    """Fixture for a mocked EnhancedMemoryManager."""
    mock = MagicMock(spec=EnhancedMemoryManager)
    return mock

class TestStrategicPlanner:
    """Tests for the StrategicPlanner class."""

    def test_generate_strategic_plan_success_with_numbered_list(self, mock_llm_manager, mock_memory_manager):
        """Test successful generation of a plan from a numbered list response."""
        # Arrange
        mock_response = (
            "Here is the plan:\n"
            "1. First objective.\n"
            "2. Second objective.\n"
            "3. Third objective."
        )
        mock_llm_manager.chat.return_value.response_text = mock_response
        planner = StrategicPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        goal = "Achieve world peace."

        # Act
        strategic_plan = planner.generate_strategic_plan(goal)

        # Assert
        assert strategic_plan == [
            "First objective.",
            "Second objective.",
            "Third objective.",
        ]
        mock_llm_manager.chat.assert_called_once()
        call_args, _ = mock_llm_manager.chat.call_args
        assert goal in call_args[0][1]["content"] # Goal is in the user message

    def test_generate_strategic_plan_fallback_parsing(self, mock_llm_manager, mock_memory_manager):
        """Test fallback parsing when the response is not a numbered list."""
        # Arrange
        mock_response = (
            "Your Output:\n"
            "First objective.\n"
            "Second objective."
        )
        mock_llm_manager.chat.return_value.response_text = mock_response
        planner = StrategicPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        goal = "A goal that triggers fallback."

        # Act
        strategic_plan = planner.generate_strategic_plan(goal)

        # Assert
        assert strategic_plan == [
            "First objective.",
            "Second objective.",
        ]
        mock_llm_manager.chat.assert_called_once()

    def test_generate_strategic_plan_empty_response(self, mock_llm_manager, mock_memory_manager):
        """Test handling of an empty string response from the LLM."""
        # Arrange
        mock_llm_manager.chat.return_value.response_text = ""
        planner = StrategicPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        goal = "A goal that results in an empty plan."

        # Act
        strategic_plan = planner.generate_strategic_plan(goal)

        # Assert
        assert strategic_plan == []
        mock_llm_manager.chat.assert_called_once()

    def test_generate_strategic_plan_llm_error(self, mock_llm_manager, mock_memory_manager):
        """Test handling of an exception raised by the LLMManager."""
        # Arrange
        mock_llm_manager.chat.side_effect = Exception("LLM API is down")
        planner = StrategicPlanner(llm_manager=mock_llm_manager, memory_manager=mock_memory_manager)
        goal = "A goal that causes an LLM error."

        # Act
        strategic_plan = planner.generate_strategic_plan(goal)

        # Assert
        assert strategic_plan == []
        mock_llm_manager.chat.assert_called_once()
