#!/usr/bin/env python3
"""
Test to verify that the system operates exclusively in English after translation integration.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.agents.chat_context_manager import ChatContextManager, ChatMode

from tools.translation_tool import TranslationTool


def test_english_only_processing():
    """Test that all internal processing happens in English only."""
    print("=== Testing English-Only System Processing ===\n")

    # Initialize components
    manager = ChatContextManager()
    translator = TranslationTool()

    # Test cases: Ukrainian/Russian input that should be translated to English
    test_cases = [
        {
            "input": "допоможи мені з Atlas",
            "expected_mode": ChatMode.SYSTEM_HELP,
            "description": "Ukrainian help request",
        },
        {
            "input": "які інструменти доступні?",
            "expected_mode": ChatMode.TOOL_INQUIRY,
            "description": "Ukrainian tool inquiry",
        },
        {
            "input": "зроби скріншот",
            "expected_mode": ChatMode.GOAL_SETTING,
            "description": "Ukrainian task request",
        },
        {
            "input": "як справи?",
            "expected_mode": ChatMode.STATUS_CHECK,
            "description": "Ukrainian status check",
        },
        {
            "input": "налаштування системи",
            "expected_mode": ChatMode.CONFIGURATION,
            "description": "Ukrainian configuration request",
        },
    ]

    print("1. Testing translation to English:")
    for case in test_cases:
        # Translate to English first
        translation_result = translator.translate_to_english(case["input"])
        translated = (
            translation_result.text
            if hasattr(translation_result, "text")
            else str(translation_result)
        )
        print(f"   {case['description']}: '{case['input']}' → '{translated}'")

        # Analyze the translated English text
        context = manager.analyze_message(translated)
        print(
            f"   Detected mode: {context.mode.value} (confidence: {context.confidence:.2f})"
        )

        # Verify it's the expected mode
        if context.mode == case["expected_mode"]:
            print("   ✅ PASS\n")
        else:
            print(f"   ❌ FAIL - Expected {case['expected_mode'].value}\n")

    print("2. Testing keywords are English-only:")
    # Check that all keywords in patterns are English
    for mode, patterns in manager.mode_patterns.items():
        print(f"   Mode: {mode.value}")
        keywords = patterns.get("keywords", [])

        # Check for non-English characters
        non_english_found = False
        for keyword in keywords:
            if any(ord(char) > 127 for char in keyword):
                print(f"   ❌ Non-English keyword found: '{keyword}'")
                non_english_found = True

        if not non_english_found:
            print("   ✅ All keywords are English")
        print()

    print("3. Testing pattern matching on English text:")
    english_test_cases = [
        "help me with Atlas",
        "what tools are available",
        "take a screenshot",
        "how are things",
        "change settings",
    ]

    for english_msg in english_test_cases:
        context = manager.analyze_message(english_msg)
        print(
            f"   '{english_msg}' → {context.mode.value} (confidence: {context.confidence:.2f})"
        )

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_english_only_processing()
