#!/usr/bin/env python3
"""Simple test to verify the plugin works."""

print("Starting plugin test...")

try:
    # Import the plugin
    import plugin
    print("✓ Plugin imported")
    
    # Test registration
    result = plugin.register()
    print(f"✓ Registration returned: {len(result['tools'])} tools")
    
    # Test tool creation
    if result['tools']:
        tool = result['tools'][0]
        print(f"✓ Tool name: {tool.name}")
        print(f"✓ Tool platform: {tool.platform_info}")
        
        # Test basic functionality
        response = tool("How does Atlas work?")
        print(f"✓ Tool response: {len(response)} characters")
        
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")
