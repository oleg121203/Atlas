#!/usr/bin/env python3
"""
Test LLM Manager Default Provider

Quick test to ensure LLM Manager correctly uses Gemini as default
and doesn't try to use OpenAI when it's not available.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from agents.llm_manager import LLMManager
from agents.token_tracker import TokenTracker
from config_manager import ConfigManager

def test_default_provider():
    """Test that LLM Manager uses Gemini by default"""
    print("🔧 Testing LLM Manager Default Provider...")
    
    # Initialize components
    config_manager = ConfigManager()
    token_tracker = TokenTracker()
    
    # Check config before LLM manager
    current_provider = config_manager.get_current_provider()
    current_model = config_manager.get_current_model()
    print(f"📋 Config says: provider={current_provider}, model={current_model}")
    
    # Initialize LLM Manager
    llm_manager = LLMManager(token_tracker, config_manager)
    
    # Check what LLM Manager is using
    print(f"🤖 LLM Manager: provider={llm_manager.current_provider}, model={llm_manager.current_model}")
    print(f"🔌 OpenAI client: {'Available' if llm_manager.is_provider_available('openai') else 'Not available'}")
    print(f"💎 Gemini client: {'Available' if llm_manager.gemini_client else 'Not available'}")
    
    # Test simple chat to ensure it works
    if llm_manager.gemini_client and llm_manager.current_provider == "gemini":
        try:
            print("💬 Testing simple Gemini chat...")
            messages = [{"role": "user", "content": "Respond with exactly 'Test successful'"}]
            response = llm_manager.chat(messages)
            print(f"✅ Chat response: {response.response_text}")
            print(f"📊 Tokens used: {response.total_tokens}")
            return True
        except Exception as e:
            print(f"❌ Chat test failed: {e}")
            return False
    else:
        print("❌ Gemini not available or not set as current provider")
        return False

def main():
    """Main function"""
    try:
        success = test_default_provider()
        if success:
            print("\n✅ LLM Manager is correctly using Gemini as default!")
            return 0
        else:
            print("\n❌ LLM Manager has configuration issues")
            return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
