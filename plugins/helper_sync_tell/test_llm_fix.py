#!/usr/bin/env python3
"""
Quick test for LLM integration fix
"""

import sys
import os

# Add the Atlas root directory to path
atlas_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, atlas_root)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing LLM integration fix...")

try:
    import plugin
    
    # Mock LLM Manager that returns correct structure
    class MockLLMManager:
        def chat(self, messages):
            content = messages[0]["content"]
            if "Analysis:" in content:
                return type('Response', (), {'content': f"Mock analysis for the question in the prompt"})
            elif "Comprehensive response:" in content:
                return type('Response', (), {'content': f"Mock comprehensive response based on analyses"})
            else:
                return type('Response', (), {'content': f"Mock response to: {content[:50]}..."})
    
    # Mock Atlas app
    class MockAtlasApp:
        def __init__(self):
            self.helper_sync_tell_integration = False
            
        def _handle_help_mode(self, message, context):
            return f"Mock help response for: {message}"
    
    mock_llm = MockLLMManager()
    mock_app = MockAtlasApp()
    
    # Test registration with mock LLM
    result = plugin.register(llm_manager=mock_llm, atlas_app=mock_app)
    print("✅ Registration with mock LLM successful")
    
    if result.get('tools'):
        tool = result['tools'][0]
        
        # Test complex query
        test_query = "Як ти бачиш вдосконалення памяті?"
        
        response = tool(test_query)
        print("✅ Complex query processing successful")
        print(f"Response preview: {response[:200]}...")
        
        if "Mock" in response:
            print("✅ LLM integration working correctly")
        else:
            print("❌ LLM integration may have issues")
    
    print("\n✅ LLM integration fix test completed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
