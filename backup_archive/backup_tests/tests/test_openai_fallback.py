#!/usr/bin/env python3
"""
Test OpenAI Fallback to Gemini

Test that when OpenAI is explicitly requested but not available,
it properly falls back to Gemini without errors.
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from modules.agents.token_tracker import TokenTracker

from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


def test_openai_fallback():
    """Test OpenAI fallback functionality"""
    print("🔄 Testing OpenAI → Gemini Fallback...")

    # Initialize components

    config_manager = ConfigManager()
    token_tracker = TokenTracker()
    llm_manager = LLMManager(token_tracker, config_manager)

    # Test 1: Explicit OpenAI call should fallback to Gemini
    try:
        print("🧪 Test 1: Explicit OpenAI request with placeholder key...")
        messages = [{"role": "user", "content": "Say 'Fallback test successful!'"}]
        response = llm_manager.chat(messages, provider="openai", model="gpt-4")
        print(f"✅ Response received: {response.response_text}")
        print("✅ OpenAI → Gemini fallback works!")
    except Exception as e:
        print(f"❌ OpenAI fallback failed: {e}")
        return False

    # Test 2: Try _chat_openai directly
    try:
        print("\n🧪 Test 2: Direct _chat_openai call...")
        messages = [{"role": "user", "content": "Direct OpenAI test"}]
        response = llm_manager._chat_openai(messages, model="gpt-3.5-turbo")
        print(f"✅ Response received: {response.response_text}")
        print("✅ Direct OpenAI call fallback works!")
    except Exception as e:
        print(f"❌ Direct OpenAI call failed: {e}")
        return False

    # Test 3: Available providers check
    try:
        print("\n🧪 Test 3: Available providers...")
        providers = llm_manager.get_available_providers()
        if "openai" not in providers:
            print("✅ OpenAI correctly not listed in available providers")
        else:
            print("❌ OpenAI incorrectly listed as available")
            return False

        if "gemini" in providers:
            print("✅ Gemini correctly listed as available")
        else:
            print("❌ Gemini not available")
            return False
    except Exception as e:
        print(f"❌ Provider check failed: {e}")
        return False

    print("\n🎯 OpenAI Fallback Test Summary:")
    print("=" * 40)
    print("✅ Explicit OpenAI request → Gemini: OK")
    print("✅ Direct OpenAI call → Gemini: OK")
    print("✅ Provider availability check: OK")
    print("✅ No 'OpenAI client not initialized' errors!")

    return True


def main():
    """Main function"""
    try:
        success = test_openai_fallback()
        if success:
            print("\n🎉 All OpenAI fallback tests passed!")
            print("🔧 The 'OpenAI client not initialized' error should be fixed!")
            return 0
        print("\n❌ Some OpenAI fallback tests failed")
        return 1
    except Exception as e:
        print(f"\n❌ Error during OpenAI fallback testing: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
