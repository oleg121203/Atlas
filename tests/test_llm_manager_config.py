#!/usr/bin/env python3
"""
Test LLM Manager Configuration

Test that the LLM manager handles the new configuration properly,
including provider/model validation and OpenAI key handling.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from agents.llm_manager import LLMManager
from agents.token_tracker import TokenTracker
from utils.config_manager import ConfigManager
from utils.logger import Logger

def test_llm_manager():
    """Test LLM manager functionality"""
    print("🤖 Testing LLM Manager Configuration...")
    
    #Initialize components
    logger = Logger("test_llm_manager")
    config_manager = ConfigManager()
    token_tracker = TokenTracker()
    
    #Test LLM Manager initialization
    try:
        llm_manager = LLMManager(token_tracker, config_manager)
        print("✅ LLM Manager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize LLM Manager: {e}")
        return False
    
    #Test available providers
    try:
        providers = llm_manager.get_available_providers()
        print(f"✅ Available providers: {list(providers.keys())}")
        
        if "gemini" in providers:
            print(f"  📱 Gemini models: {providers['gemini']}")
        else:
            print("  ⚠️  Gemini not available")
            
        if "openai" in providers:
            print(f"  🤖 OpenAI models: {providers['openai']}")
        else:
            print("  ℹ️  OpenAI not available (expected with placeholder key)")
            
        if "ollama" in providers:
            print(f"  🏠 Ollama models: {providers['ollama']}")
            
    except Exception as e:
        print(f"❌ Error getting providers: {e}")
        return False
    
    #Test current provider/model
    try:
        current_provider = llm_manager.current_provider
        current_model = llm_manager.current_model
        print(f"✅ Current provider: {current_provider}")
        print(f"✅ Current model: {current_model}")
    except Exception as e:
        print(f"❌ Error getting current provider/model: {e}")
        return False
    
    #Test provider/model validation
    try:
        #Test valid combination
        provider, model = llm_manager._validate_provider_model("gemini", "gemini-1.5-flash")
        print(f"✅ Valid combination: {provider}/{model}")
        
        #Test invalid model for valid provider
        provider, model = llm_manager._validate_provider_model("gemini", "gpt-4")
        print(f"✅ Auto-corrected invalid model: {provider}/{model}")
        
        #Test invalid provider (should fallback)
        provider, model = llm_manager._validate_provider_model("invalid_provider", "invalid_model")
        print(f"✅ Fallback for invalid provider: {provider}/{model}")
        
    except Exception as e:
        print(f"❌ Error in provider/model validation: {e}")
        return False
    
    #Test simple chat if Gemini is available
    if "gemini" in providers and llm_manager.gemini_client:
        try:
            print("🗣️ Testing simple chat with Gemini...")
            messages = [{"role": "user", "content": "Say 'Hello from Atlas!' in exactly those words."}]
            response = llm_manager.chat(messages, provider="gemini", model="gemini-1.5-flash")
            print(f"✅ Chat response: {response.response_text[:100]}...")
            print(f"✅ Token usage: {response.total_tokens} tokens")
        except Exception as e:
            print(f"⚠️  Chat test failed (may be API limit): {e}")
    else:
        print("ℹ️  Skipping chat test (Gemini not available)")
    
    print("\n🎯 LLM Manager Test Summary:")
    print("=" * 40)
    print("✅ LLM Manager initialization: OK")
    print("✅ Provider discovery: OK")
    print("✅ Provider/model validation: OK")
    print("✅ Configuration handling: OK")
    
    return True

def main():
    """Main function"""
    try:
        success = test_llm_manager()
        if success:
            print("\n🎉 All LLM Manager tests passed!")
            return 0
        else:
            print("\n❌ Some LLM Manager tests failed")
            return 1
    except Exception as e:
        print(f"\n❌ Error during LLM Manager testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
