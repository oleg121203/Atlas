from typing import Dict, List, Any

class MockLLMManager:
    """Mock LLMManager class for testing."""
    
    def __init__(self):
        """Initialize mock LLM manager."""
        self.model = "mock_model"
        self.temperature = 0.7
        
    def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Mock chat method."""
        return {
            'response_text': "Mock response",
            'usage': {
                'prompt_tokens': len(messages),
                'completion_tokens': 10,
                'total_tokens': len(messages) + 10
            }
        }
