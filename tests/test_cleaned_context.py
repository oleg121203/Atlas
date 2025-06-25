#!/usr/bin/env python3
"""
Test script to verify that ChatContextManager operates exclusively in English
after cleaning all Ukrainian/Russian keywords and patterns.
"""

import os
import sys

sys.path.insert(0, os.getcwd())

def test_english_only_processing():
    """Test that context manager only processes English keywords."""
    try:
        from modules.agents.chat_context_manager import ChatContextManager, ChatMode

        print("🔍 Testing English-only Chat Context Manager...")
        print("=" * 60)

        manager = ChatContextManager()

        #Test messages in English (what should come after translation)
        test_cases = [
            ("help me with atlas system", ChatMode.SYSTEM_HELP),
            ("what tools are available", ChatMode.TOOL_INQUIRY),
            ("take a screenshot", ChatMode.GOAL_SETTING),
            ("check system status", ChatMode.STATUS_CHECK),
            ("configure settings", ChatMode.CONFIGURATION),
            ("hello how are you", ChatMode.CASUAL_CHAT),
        ]

        print("Testing mode detection with English messages:")
        print("-" * 50)

        all_passed = True
        for message, expected_mode in test_cases:
            context = manager.analyze_message(message)
            detected_mode = context.mode
            confidence = context.confidence

            #Check if detection worked
            status = "✅" if detected_mode == expected_mode else "❌"
            if detected_mode != expected_mode:
                all_passed = False

            print(f"{status} '{message}'")
            print(f"    Expected: {expected_mode.value}")
            print(f"    Detected: {detected_mode.value}")
            print(f"    Confidence: {confidence:.2f}")
            print()

        #Check mode patterns for any non-English content
        print("Checking for non-English patterns/keywords:")
        print("-" * 50)

        non_english_found = False
        for mode, patterns in manager.mode_patterns.items():
            keywords = patterns.get("keywords", [])
            regex_patterns = patterns.get("patterns", [])

            #Check keywords for Cyrillic characters
            for keyword in keywords:
                if any(ord(char) > 127 for char in keyword):  #Non-ASCII characters
                    print(f"❌ Found non-English keyword in {mode.value}: '{keyword}'")
                    non_english_found = True

            #Check patterns for Cyrillic characters
            for pattern in regex_patterns:
                if any(ord(char) > 127 for char in pattern):  #Non-ASCII characters
                    print(f"❌ Found non-English pattern in {mode.value}: '{pattern}'")
                    non_english_found = True

        if not non_english_found:
            print("✅ No non-English keywords or patterns found!")

        print()
        print("=" * 60)
        if all_passed and not non_english_found:
            print("🎉 SUCCESS: Chat Context Manager is now English-only!")
            print("   ✅ All mode detection works correctly")
            print("   ✅ No Ukrainian/Russian keywords remain")
            print("   ✅ No Ukrainian/Russian patterns remain")
            print("   ✅ System ready for English-only operation after translation")
        else:
            print("❌ ISSUES FOUND:")
            if not all_passed:
                print("   - Some mode detection tests failed")
            if non_english_found:
                print("   - Non-English content still present")

        return all_passed and not non_english_found

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_english_only_processing()
    exit(0 if success else 1)
