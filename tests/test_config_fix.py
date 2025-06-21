#!/usr/bin/env python3
"""
Швидкий тест для перевірки LLM конфігурації
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_config_manager():
    """Test the ConfigManager fix"""
    print("🧪 Testing ConfigManager...")
    
    try:
        from config_manager import ConfigManager
        config_mgr = ConfigManager()
        
        #Test the new method
        result = config_mgr.set_llm_provider_and_model("gemini", "gemini-1.5-flash")
        if result:
            print("✅ ConfigManager.set_llm_provider_and_model() works!")
        else:
            print("❌ ConfigManager.set_llm_provider_and_model() failed!")
            return False
            
        #Test getting current settings
        provider = config_mgr.get_current_provider()
        model = config_mgr.get_current_model()
        print(f"✅ Current provider: {provider}")
        print(f"✅ Current model: {model}")
        
        return True
        
    except Exception as e:
        print(f"❌ ConfigManager test failed: {e}")
        return False

def test_utils_config_manager():
    """Test the utils ConfigManager fix"""
    print("\n🧪 Testing utils ConfigManager...")
    
    try:
        from utils.config_manager import config_manager
        
        #Test the new method
        result = config_manager.set_llm_provider_and_model("gemini", "gemini-1.5-flash")
        if result:
            print("✅ utils ConfigManager.set_llm_provider_and_model() works!")
        else:
            print("❌ utils ConfigManager.set_llm_provider_and_model() failed!")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ utils ConfigManager test failed: {e}")
        return False

def test_llm_manager():
    """Test LLM Manager with Gemini"""
    print("\n🧪 Testing LLM Manager...")
    
    try:
        #Import necessary modules
        from agents.token_tracker import TokenTracker
        from utils.llm_manager import LLMManager
        
        #Create instances
        token_tracker = TokenTracker()
        llm_manager = LLMManager(token_tracker)
        
        print("✅ LLM Manager initialized")
        print(f"✅ Current provider: {llm_manager.current_provider}")
        
        #Test basic chat with a simple message
        messages = [{"role": "user", "content": "Привіт! Як справи?"}]
        
        print("🔍 Testing Gemini chat...")
        try:
            result = llm_manager._chat_gemini(messages, model="gemini-1.5-flash")
            if result and result.response_text:
                print(f"✅ Gemini response: {result.response_text[:100]}...")
                return True
            else:
                print("❌ No response from Gemini")
                return False
        except Exception as e:
            print(f"❌ Gemini chat failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ LLM Manager test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Atlas Configuration Tests...")
    print("=" * 50)
    
    success = True
    
    #Test ConfigManager
    if not test_config_manager():
        success = False
    
    #Test utils ConfigManager
    if not test_utils_config_manager():
        success = False
    
    #Test LLM Manager
    if not test_llm_manager():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Configuration is working correctly.")
        print("\n🚀 You can now start Atlas with: python3 main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
