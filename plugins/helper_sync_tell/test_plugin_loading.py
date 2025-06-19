#!/usr/bin/env python3
"""
Test script to verify the Helper Sync Tell plugin loads correctly.
Run this from the Atlas root directory to test the plugin.
"""

import sys
import os
from pathlib import Path

# Add Atlas root to path
atlas_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(atlas_root))

def test_plugin_loading():
    """Test that the plugin can be loaded without errors."""
    print("Testing Helper Sync Tell plugin loading...")
    
    try:
        # Add plugin directory to path
        plugin_dir = Path(__file__).parent
        sys.path.insert(0, str(plugin_dir))
        
        # Import the plugin module
        import plugin
        
        print("✓ Plugin module imported successfully")
        
        # Test tool creation
        tool = plugin.HelperSyncTellTool()
        print(f"✓ Tool created: {tool.name}")
        print(f"✓ Platform info: {tool.platform_info}")
        
        # Test registration function
        registration_data = plugin.register()
        print(f"✓ Registration successful: {len(registration_data['tools'])} tools, {len(registration_data['agents'])} agents")
        
        # Test basic functionality
        test_query = "How does memory work in Atlas?"
        response = tool(test_query, {})
        print(f"✓ Basic functionality test completed")
        print(f"  Query: {test_query}")
        print(f"  Response length: {len(response)} characters")
        
        print("\n✅ All tests passed! Plugin is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Plugin test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_plugin_loading()
    sys.exit(0 if success else 1)
