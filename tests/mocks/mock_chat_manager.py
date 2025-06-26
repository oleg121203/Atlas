from typing import Dict, Any, List

class MockChatContextManager:
    """Mock ChatContextManager class for testing."""
    
    def __init__(self, memory_manager: Any = None, llm_manager: Any = None):
        """Initialize mock chat manager."""
        self.memory_manager = memory_manager
        self.llm_manager = llm_manager
        self.messages = []
        
    def process_message(self, message: Dict[str, str]):
        """Mock process_message method."""
        self.messages.append(message)
        
    def get_messages(self) -> List[Dict[str, str]]:
        """Mock get_messages method."""
        return self.messages
        
    def clear_messages(self):
        """Mock clear_messages method."""
        self.messages.clear()
