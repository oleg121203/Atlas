#!/usr/bin/env python3
"""
Enhanced test for the Helper Sync Tell plugin.
"""

import sys


def test_enhanced_plugin():
    """Test the enhanced plugin functionality."""
    print("🧪 Testing Enhanced Helper Sync Tell Plugin")
    print("=" * 50)

    try:
        #Import the plugin
        import plugin
        print("✓ Plugin imported successfully")

        #Test registration
        registration = plugin.register()
        print(f"✓ Registration successful: {len(registration['tools'])} tools")

        if not registration["tools"]:
            print("❌ No tools registered")
            return False

        #Get the tool
        tool = registration["tools"][0]
        print(f"✓ Tool created: {tool.name} v{getattr(tool, 'version', '1.0')}")
        print(f"✓ Platform: {tool.platform_info.get('system', 'Unknown')}")
        print(f"✓ Capabilities: {len(getattr(tool, 'capabilities', {}))} features")

        #Test basic functionality
        test_query = "How does memory management work in software systems?"
        print(f"\n🎯 Testing with query: {test_query}")

        #Mock tools for testing
        mock_tools = {
            "code_search": lambda q: f"Code search found relevant functions for: {q}",
            "documentation": lambda q: f"Documentation shows key concepts for: {q}",
        }

        response = tool(test_query, mock_tools)
        print(f"✓ Tool responded with {len(response)} characters")
        print(f"✓ Response preview: {response[:100]}...")

        #Test performance stats if available
        if hasattr(tool, "get_performance_stats"):
            stats = tool.get_performance_stats()
            print(f"✓ Performance stats available: {stats.get('queries_processed', 0)} queries")

        print("\n✅ All tests passed! Enhanced plugin is working correctly.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_plugin()
    print(f"\n{'🎉 SUCCESS' if success else '💥 FAILURE'}")
    sys.exit(0 if success else 1)
