from typing import List, Dict, Any

class ChatProcessor:
    def __init__(self):
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}

    def process_message(self, user_id: str, message: str) -> str:
        """Process a user message and return a response."""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({'role': 'user', 'content': message})
        # Placeholder for actual processing logic
        response = f"Echo: {message}"
        self.conversations[user_id].append({'role': 'assistant', 'content': response})
        return response

    def get_conversation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get the conversation history for a user."""
        return self.conversations.get(user_id, [])
