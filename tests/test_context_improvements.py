#!/usr/bin/env python3
"""
Test script for improved chat context manager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.chat_context_manager import ChatContextManager, ChatMode

def test_context_detection():
    """Test context detection improvements."""
    print("🧪 Testing improved chat context detection...\n")
    
    ccm = ChatContextManager()
    
    test_cases = [
        ("Привіт друже, як тебе звати?", ChatMode.CASUAL_CHAT),
        ("Мене цікавить чи забезпечена в тебе пам'ять довгострокова?", ChatMode.SYSTEM_HELP),
        ("Які у тебе інструменти?", ChatMode.SYSTEM_HELP),
        ("Take a screenshot", ChatMode.GOAL_SETTING),
        ("What is your status?", ChatMode.STATUS_CHECK),
    ]
    
    for i, (message, expected_mode) in enumerate(test_cases, 1):
        try:
            context = ccm.analyze_message(message)
            status = "✅" if context.mode == expected_mode else "❌"
            print(f"{status} Test {i}: '{message}'")
            print(f"   Expected: {expected_mode.value}")
            print(f"   Got: {context.mode.value} (confidence: {context.confidence:.2f})")
            print()
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
            print()

def test_response_generation():
    """Test response generation improvements."""
    print("🧪 Testing improved response generation...\n")
    
    ccm = ChatContextManager()
    
    # Test memory question response
    message = "Мене цікавить чи забезпечена в тебе пам'ять довгострокова?"
    context = ccm.analyze_message(message)
    prompt = ccm.generate_response_prompt(context, message)
    
    print("📝 Memory question prompt preview:")
    print(prompt[:300] + "...")
    print()
    
    # Test casual greeting response  
    message2 = "Привіт, як справи?"
    context2 = ccm.analyze_message(message2)
    prompt2 = ccm.generate_response_prompt(context2, message2)
    
    print("📝 Casual greeting prompt preview:")
    print(prompt2[:200] + "...")
    print()

if __name__ == "__main__":
    test_context_detection()
    test_response_generation()
    print("✨ Testing completed!")
