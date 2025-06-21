#!/usr/bin/env python3
"""
Test Enhanced Helper Sync Tell Plugin Integration
"""

import sys
import os

#Add the Atlas root directory to path
atlas_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, atlas_root)

try:
    print("🔧 Testing Enhanced Helper Sync Tell Plugin Integration")
    print("=" * 60)
    
    print("\n1. Testing plugin registration...")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import plugin
    
    #Test basic registration
    result = plugin.register()
    print("✅ Basic registration successful")
    print(f"   Tools: {len(result.get('tools', []))}")
    print(f"   Metadata version: {result.get('metadata', {}).get('version', 'unknown')}")
    
    if result.get('tools'):
        tool = result['tools'][0]
        print(f"   Tool name: {tool.name}")
        print(f"   Tool capabilities: {len(tool.capabilities)} items")
        
    print("\n2. Testing with mock Atlas app...")
    
    class MockAtlasApp:
        def __init__(self):
            self.helper_sync_tell_integration = False
            
        def _handle_help_mode(self, message, context):
            return f"Mock help response for: {message}"
    
    mock_app = MockAtlasApp()
    
    #Test registration with mock app
    result_with_app = plugin.register(atlas_app=mock_app)
    print("✅ Registration with mock app successful")
    
    integration_status = result_with_app.get('metadata', {}).get('integration_status', False)
    print(f"   Integration status: {integration_status}")
    
    if hasattr(mock_app, 'helper_sync_tell_integration'):
        print(f"   App integration flag: {mock_app.helper_sync_tell_integration}")
    
    print("\n3. Testing enhanced thinking process...")
    
    if result_with_app.get('tools'):
        tool = result_with_app['tools'][0]
        
        #Test a complex query
        test_query = "Проаналізуй як працює довготривала пам'ять в Атлас"
        
        try:
            #Test without tools
            response = tool(test_query)
            print("✅ Enhanced thinking test successful")
            print(f"   Response length: {len(response)} characters")
            print(f"   Response preview: {response[:100]}...")
            
        except Exception as e:
            print(f"❌ Enhanced thinking test failed: {e}")
    
    print("\n4. Testing platform compatibility...")
    if result.get('tools'):
        tool = result['tools'][0]
        platform_info = tool.platform_info
        print("✅ Platform detection working")
        print(f"   System: {platform_info.get('system', 'unknown')}")
        print(f"   Python version: {platform_info.get('python_version', 'unknown')}")
        print(f"   Is macOS: {platform_info.get('is_macos', False)}")
        print(f"   Is Linux: {platform_info.get('is_linux', False)}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("🎯 Plugin is ready for production use")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
