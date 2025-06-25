#!/usr/bin/env python3
"""
Test Groq Settings Loading

This script tests that Atlas correctly loads and applies Groq settings.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager
from modules.agents.token_tracker import TokenTracker

def test_groq_settings():
    """Test that Groq settings are loaded and applied correctly."""
    
    print("🧪 Testing Groq Settings Loading...")
    print("=" * 50)
    
    # Test 1: Load configuration
    print("\n1. Loading configuration...")
    config_manager = ConfigManager()
    settings = config_manager.load()
    
    if not settings:
        print("❌ Failed to load settings")
        return False
    
    current_provider = settings.get("current_provider", "unknown")
    current_model = settings.get("current_model", "unknown")
    
    print(f"   Current provider: {current_provider}")
    print(f"   Current model: {current_model}")
    
    if current_provider != "groq":
        print("❌ Provider is not set to 'groq'")
        return False
    
    print("✅ Configuration loaded correctly")
    
    # Test 2: Initialize LLM Manager
    print("\n2. Initializing LLM Manager...")
    token_tracker = TokenTracker()
    llm_manager = LLMManager(token_tracker, config_manager)
    
    # Test 3: Check LLM Manager settings
    print("\n3. Checking LLM Manager settings...")
    actual_provider = llm_manager.current_provider
    actual_model = llm_manager.current_model
    
    print(f"   LLM Manager provider: {actual_provider}")
    print(f"   LLM Manager model: {actual_model}")
    
    if actual_provider != "groq":
        print("❌ LLM Manager provider is not 'groq'")
        return False
    
    print("✅ LLM Manager initialized with correct settings")
    
    # Test 4: Test provider availability
    print("\n4. Testing provider availability...")
    is_available = llm_manager.is_provider_available("groq")
    print(f"   Groq provider available: {is_available}")
    
    if not is_available:
        print("⚠️  Groq provider not available (API key may be missing)")
        print("   This is expected if you haven't added your Groq API key yet")
    
    # Test 5: Check API key
    print("\n5. Checking API key...")
    groq_api_key = settings.get("api_keys", {}).get("groq", "")
    if groq_api_key:
        print(f"   Groq API key: {groq_api_key[:10]}...")
    else:
        print("   Groq API key: Not set")
        print("   ⚠️  You need to add your Groq API key to use Groq")
    
    print("\n" + "=" * 50)
    print("✅ Groq Settings Test Completed Successfully!")
    print("\n📋 Summary:")
    print(f"   • Configuration provider: {current_provider}")
    print(f"   • Configuration model: {current_model}")
    print(f"   • LLM Manager provider: {actual_provider}")
    print(f"   • LLM Manager model: {actual_model}")
    print(f"   • Groq provider available: {is_available}")
    
    if not groq_api_key:
        print("\n🔑 Next Steps:")
        print("1. Add your Groq API key to ~/.atlas/config.yaml")
        print("2. Restart Atlas")
        print("3. Verify Groq is working in the chat")
    
    return True

if __name__ == "__main__":
    test_groq_settings() 