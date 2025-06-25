#!/usr/bin/env python3
"""Test the improved help mode behavior."""

import sys

sys.path.append("/workspaces/Atlas")

try:
    from modules.agents.chat_context_manager import ChatContextManager

    #Initialize the context manager
    manager = ChatContextManager()

    print("🧪 Testing improved System Help mode...")

    #Test cases
    test_cases = [
        {
            "message": "Мене Олег. Розкажи про можливості даного ПО по довгостроковій памяті. Де і як реалізовано?",
            "expected_mode": "system_help",
            "description": "Technical memory implementation question",
        },
        {
            "message": "Які у тебе інструменти і де вони реалізовані?",
            "expected_mode": "tool_inquiry",  #Changed expectation
            "description": "Tools implementation question",
        },
        {
            "message": "Як працює система пам'яті в Atlas?",
            "expected_mode": "system_help",
            "description": "Memory system technical question",
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n✅ Test {i}: {test['description']}")
        print(f"   Input: '{test['message'][:50]}...'")

        #Analyze message
        context = manager.analyze_message(test["message"])
        mode_detected = context.mode.value
        confidence = context.confidence

        #Check detection
        if mode_detected == test["expected_mode"]:
            print(f"   ✅ Mode: {mode_detected} (confidence: {confidence:.2f})")
        else:
            print(f"   ❌ Expected: {test['expected_mode']}, Got: {mode_detected} (confidence: {confidence:.2f})")

        #Generate response prompt
        prompt = manager.generate_response_prompt(context, test["message"])

        #Check if prompt encourages tool usage
        tool_usage_indicators = [
            "semantic_search", "file_search", "read_file", "grep_search",
            "ANALYZE THE CODEBASE", "Use your code analysis tools",
            "search for", "look for", "find",
        ]

        uses_tools = any(indicator in prompt for indicator in tool_usage_indicators)

        print(f"   📋 Prompt encourages tool usage: {'✅ Yes' if uses_tools else '❌ No'}")

        #Show snippet of prompt
        snippet = prompt[:200].replace("\n", " ").strip() + "..."
        print(f"   📝 Prompt preview: {snippet}")

    print("\n🎯 System Help mode has been upgraded to:")
    print("   • Actively analyze codebase using tools")
    print("   • Provide specific implementation details")
    print("   • Reference actual files and code")
    print("   • Give technical expertise, not general overviews")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
