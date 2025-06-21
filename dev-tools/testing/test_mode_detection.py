#!/usr/bin/env python3
"""
Test script for chat mode detection
"""

from agents.chat_context_manager import ChatContextManager
from agents.enhanced_memory_manager import EnhancedMemoryManager
from agents.token_tracker import TokenTracker
from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


def test_mode_detection():
    """Test mode detection for various messages"""

    #Initialize managers
    config_manager = ConfigManager()
    token_tracker = TokenTracker()
    llm_manager = LLMManager(token_tracker)
    memory_manager = EnhancedMemoryManager(llm_manager, config_manager)

    chat_manager = ChatContextManager(
        memory_manager=memory_manager,
    )

    #Test messages
    test_messages = [
        ("Привіт", "CASUAL_CHAT"),
        ("Tell about your code where long-term memory issue is resolved?", "SYSTEM_HELP"),
        ("Rebuild index, when finished, I'll ask questions about your code.", "SYSTEM_HELP"),
        ("How is your memory organized?", "SYSTEM_HELP"),
        ("Which provider are you using?", "SYSTEM_HELP"),
        ("About yourself", "SYSTEM_HELP"),
        ("How you work", "SYSTEM_HELP"),
        ("Show me your capabilities", "SYSTEM_HELP"),
        ("Take a screenshot", "GOAL_SETTING"),
    ]

    print("🧪 Testing Chat Mode Detection:")
    print("=" * 50)

    for message, expected in test_messages:
        context = chat_manager.analyze_message(message)
        detected = context.mode.value.upper()
        confidence = context.confidence

        status = "✅" if detected == expected else "❌"
        print(f"{status} '{message}' → {detected} (confidence: {confidence:.3f})")
        if detected != expected:
            print(f"   Expected: {expected}")
        print()

if __name__ == "__main__":
    test_mode_detection()
