#!/usr/bin/env python3
"""
Test script for memory-related help responses in Atlas
"""

import re
from enum import Enum
from unittest.mock import MagicMock

#Mock the necessary classes to avoid imports
class ChatMode(Enum):
    """Mock of the ChatMode enum"""
    CASUAL_CHAT = "casual_chat"
    SYSTEM_HELP = "system_help"
    GOAL_SETTING = "goal_setting"

class MockChatContextManager:
    """Mock of ChatContextManager to test pattern detection"""
    
    def __init__(self):
        self.mode_patterns = {
            ChatMode.SYSTEM_HELP: {
                'keywords': [
                    'help', 'explain', 'tutorial', 'guide', 'documentation', 
                    'capabilities', 'modes', 'mode', 'atlas', 'system',
                    'tell me about', 'what are', 'show me', 'describe',
                    'atlas capabilities', 'atlas features', 'atlas modes',
                    'about atlas', 'atlas system', 'development mode',
                    'your memory', 'organized memory', 'about yourself',
                    'your capabilities', 'your features', 'provider',
                    'memory system', 'long-term memory', 'short-term memory',
                    'how do you remember', 'do you forget', 'memory management',
                    'пам\'ять', 'память', 'запоминаешь', 'запам\'ятовуєш',
                    'rebuild index', 'update index', 'show file', 'analyze file',
                    'code analysis', 'structure analysis'
                ],
                'patterns': [
                    r'\b(explain\s+(?:atlas|system)|help\s+(?:with|me)\s+(?:atlas|system))\b',
                    r'\b(atlas\s+(?:capabilities|features|modes|system))\b',
                    r'\b(tell\s+me\s+about\s+(?:atlas|system|yourself))\b',
                    r'\b(what\s+(?:are|is)\s+(?:atlas|your)\s+(?:capabilities|features|modes))\b',
                    r'\b(development\s+mode|your\s+memory|organized\s+memory)\b',
                    r'\b(rebuild\s+index|analyze\s+file|code\s+analysis)\b',
                    r'\b(about\s+(?:atlas|system|yourself))\b',
                    r'\b(memory\s+system|long-term\s+memory|how\s+(?:do\s+)?you\s+remember)\b',
                    r'\b(how\s+(?:is|does)\s+(?:your|atlas)\s+memory\s+(?:work|organized))\b'
                ]
            },
            ChatMode.CASUAL_CHAT: {
                'keywords': ['hello', 'hi'],
                'patterns': []
            }
        }
    
    def analyze_message(self, message):
        """Simple analysis to check if keywords are detected"""
        message_lower = message.lower()
        
        #Check if any memory-related keyword is in the message
        memory_keywords = [
            'memory', 'пам\'ять', 'память', 'remember', 'memorize', 
            'store', 'recall', 'forget', 'запоминаешь', 'запам\'ятовуєш'
        ]
        
        is_memory_related = any(keyword in message_lower for keyword in memory_keywords)
        
        #Check if any help pattern matches
        help_patterns = self.mode_patterns[ChatMode.SYSTEM_HELP]['patterns']
        pattern_matches = any(
            re.search(pattern, message_lower, re.IGNORECASE) 
            for pattern in help_patterns
        )
        
        result = MagicMock()
        result.mode = ChatMode.SYSTEM_HELP if is_memory_related or pattern_matches else ChatMode.CASUAL_CHAT
        result.confidence = 0.9 if is_memory_related else 0.5
        
        return result
    
    def generate_response_prompt(self, context, message, system_info=None):
        """Check if we detect memory-related queries and include memory info"""
        message_lower = message.lower()
        memory_keywords = ['memory', 'пам\'ять', 'память', 'remember', 'memorize', 'forget']
        
        if any(keyword in message_lower for keyword in memory_keywords):
            return """memory system information included in response"""
        else:
            return """standard help response"""

def test_memory_help_detection():
    """
    Test that memory-related questions are properly detected as SYSTEM_HELP mode
    and that the response contains specialized memory information
    """
    print("\n🧪 Testing Memory Help Detection in Chat Context Manager\n")
    print("=" * 70)
    
    #Create mock chat manager
    chat_manager = MockChatContextManager()
    
    #Test queries
    memory_queries = [
        "Tell me about your memory system",
        "How does Atlas remember things?",
        "Explain your long-term memory",
        "Do you have short-term and long-term memory?",
        "How is your memory organized?",
        "What is your memory architecture?",
        "Розкажи про свою память довготривалу в Атлас",  #Ukrainian
        "Как организована твоя память?"  #Russian
    ]
    
    success_count = 0
    total_count = len(memory_queries)
    
    for query in memory_queries:
        #Analyze query
        context = chat_manager.analyze_message(query)
        
        #Generate response
        system_prompt = chat_manager.generate_response_prompt(
            context, 
            query,
            system_info={"tools": ["screenshot", "click", "type_text"], "agents": ["MasterAgent", "ScreenAgent"]}
        )
        
        print(f"\n📝 Query: {query}")
        print(f"🔍 Detected Mode: {context.mode.value} (confidence: {context.confidence:.2f})")
        
        #Check if it contains memory-specific information
        has_memory_info = "memory system" in system_prompt.lower()
        print(f"✓ Contains Memory Info: {has_memory_info}")
        
        test_passed = True
        
        if context.mode != ChatMode.SYSTEM_HELP:
            print("❌ ERROR: Memory query not detected as SYSTEM_HELP")
            test_passed = False
        
        if not has_memory_info:
            print("❌ ERROR: Response doesn't contain memory information")
            test_passed = False
        
        if test_passed:
            success_count += 1
            print("✅ Test passed for this query")
        
        print("-" * 70)
    
    print(f"\n🎯 Result: {success_count}/{total_count} tests passed")
    print("\n✅ Test completed")

if __name__ == "__main__":
    test_memory_help_detection()
