import pytest
from unittest.mock import MagicMock

from agents.problem_decomposition_agent import ProblemDecompositionAgent
# Temporarily comment out the import due to missing LLMResponse
# from utils.llm_manager import LLMManager  # noqa: F401

# Mock LLMManager and LLMResponse classes if they are not available
class LLMResponse:
    def __init__(self, response_text, model="mock_model", prompt_tokens=0, completion_tokens=0, total_tokens=0):
        self.response_text = response_text
        self.model = model
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        # Additional attributes for compatibility
        self.content = response_text
        self.input_tokens = prompt_tokens
        self.output_tokens = completion_tokens
        self.token_count = total_tokens
        self.cost = 0

class MockLLMManager:
    def __init__(self):
        self.chat = MagicMock()

@pytest.fixture
def mock_llm_manager():
    """Fixture for a mocked LLMManager."""
    return MockLLMManager()

def test_decompose_goal_successful_path(decomposition_agent, mock_llm_manager):
    """
    Tests the ToT decomposition process, simulating a clear path of high-scoring thoughts.
    """
    complex_goal = "Develop a go-to-market strategy for a new AI-powered code assistant."

    def mock_chat_router(messages):
        user_prompt = messages[1]['content']

        # --- Evaluation Prompts ---
        if "Thought to Evaluate" in user_prompt:
            if "Identify target developer segments" in user_prompt:
                return LLMResponse("0.9", "mock_model", 10, 1, 11)
            elif "Create a beta testing program" in user_prompt:
                return LLMResponse("0.95", "mock_model", 10, 1, 11)
            else:
                return LLMResponse("0.5", "mock_model", 10, 1, 11)  # Lower score for other paths

        # --- Generation Prompts ---
        else:
            # Response for the root node
            if "go-to-market strategy" in user_prompt:
                return LLMResponse(
                    "1. Identify target developer segments (e.g., enterprise, startup, student).\n"
                    "2. Draft initial pricing tiers.\n"
                    "3. Brainstorm product names.",
                    "mock_model", 50, 3, 53
                )
            # Response for the best first-level thought
            elif "Identify target developer segments" in user_prompt:
                return LLMResponse(
                    "1. Create a beta testing program for early adopters.\n"
                    "2. Develop content marketing (blog posts, tutorials).\n"
                    "3. Plan a social media campaign.",
                    "mock_model", 50, 3, 53
                )
            # Generic response for other, less optimal paths
            else:
                return LLMResponse("1. Generic thought.", "mock_model", 20, 1, 21)

    mock_llm_manager.chat.side_effect = mock_chat_router
    mock_llm_manager.chat.reset_mock()

    # Execute the decomposition
    result_path = decomposition_agent.decompose_goal(complex_goal, max_depth=2, breadth=3)

    # Assert the results
    assert result_path is not None, "The result should not be None"
    assert len(result_path) == 2, "The path should contain two steps"
    assert result_path[0] == "Identify target developer segments (e.g., enterprise, startup, student)."
    assert result_path[1] == "Create a beta testing program for early adopters."
    assert mock_llm_manager.chat.call_count > 2, "LLM should be called multiple times"

def test_decompose_goal_no_viable_thoughts(decomposition_agent, mock_llm_manager):
    """
    Tests the ToT decomposition when no thoughts score above the threshold.
    Should return None, indicating failure to find a viable path.
    """
    complex_goal = "Solve an impossible problem."

    def mock_chat_router(messages):
        user_prompt = messages[1]['content']

        if "Thought to Evaluate" in user_prompt:
            return LLMResponse("0.1", "mock_model", 10, 1, 11)  # All thoughts score very low
        else:
            return LLMResponse("1. Bad idea 1.\n2. Bad idea 2.", "mock_model", 20, 2, 22)

    mock_llm_manager.chat.side_effect = mock_chat_router
    mock_llm_manager.chat.reset_mock()

    result_path = decomposition_agent.decompose_goal(complex_goal, max_depth=2, breadth=3)

    assert result_path is None, "Result should be None when no viable thoughts are found"

def test_decompose_goal_empty_response(decomposition_agent, mock_llm_manager):
    """
    Tests the ToT decomposition when the LLM returns an empty response.
    Should handle gracefully and return None.
    """
    complex_goal = "Handle empty input."

    def mock_chat_router(messages):
        user_prompt = messages[1]['content']

        if "Thought to Evaluate" in user_prompt:
            return LLMResponse("0.5", "mock_model", 10, 1, 11)
        else:
            return LLMResponse("", "mock_model", 0, 0, 0)  # Empty response

    mock_llm_manager.chat.side_effect = mock_chat_router
    mock_llm_manager.chat.reset_mock()

    result_path = decomposition_agent.decompose_goal(complex_goal, max_depth=2, breadth=3)

    assert result_path is None, "Result should be None when LLM returns empty response"

def test_decompose_goal_max_depth_reached(decomposition_agent, mock_llm_manager):
    """
    Tests that decomposition stops at max_depth, even if more thoughts could be explored.
    """
    complex_goal = "Deep problem requiring many steps."

    def mock_chat_router(messages):
        user_prompt = messages[1]['content']

        if "Thought to Evaluate" in user_prompt:
            return LLMResponse("0.9", "mock_model", 10, 1, 11)  # High score for all thoughts
        else:
            return LLMResponse("1. Next step 1.\n2. Next step 2.", "mock_model", 20, 2, 22)

    mock_llm_manager.chat.side_effect = mock_chat_router
    mock_llm_manager.chat.reset_mock()

    result_path = decomposition_agent.decompose_goal(complex_goal, max_depth=1, breadth=2)

    assert result_path is not None, "Result should not be None"
    assert len(result_path) == 1, "Path should respect max_depth=1"

def test_decompose_goal_breadth_pruning(decomposition_agent, mock_llm_manager):
    """
    Tests that only the top 'breadth' number of thoughts are kept at each level.
    """
    complex_goal = "Problem with many possible paths."

    def mock_chat_router(messages):
        user_prompt = messages[1]['content']

        if "Thought to Evaluate" in user_prompt:
            if "Best thought" in user_prompt:
                return LLMResponse("0.95", "mock_model", 10, 1, 11)
            elif "Good thought" in user_prompt:
                return LLMResponse("0.8", "mock_model", 10, 1, 11)
            else:
                return LLMResponse("0.2", "mock_model", 10, 1, 11)  # Low score for others
        else:
            return LLMResponse(
                "1. Best thought.\n2. Good thought.\n3. Poor thought.\n4. Worst thought.",
                "mock_model", 40, 4, 44
            )

    mock_llm_manager.chat.side_effect = mock_chat_router
    mock_llm_manager.chat.reset_mock()

    result_path = decomposition_agent.decompose_goal(complex_goal, max_depth=1, breadth=2)

    assert result_path is not None, "Result should not be None"
    assert result_path[0] == "Best thought.", "Should select the highest-scoring thought"
    assert mock_llm_manager.chat.call_count <= 6, "Should evaluate only top 'breadth' thoughts"

@pytest.fixture
def decomposition_agent(mock_llm_manager):
    """Fixture for a ProblemDecompositionAgent with a mocked LLMManager."""
    return ProblemDecompositionAgent(llm_manager=mock_llm_manager)
