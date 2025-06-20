#!/usr/bin/env python3
"""
Simple test for Helper Sync Tell plugin registration.
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    print("Testing plugin registration...")
    import plugin
    
    result = plugin.register()
    
    print("✅ Registration successful!")
    print(f"Result type: {type(result)}")
    
    if isinstance(result, dict):
        print(f"Keys: {list(result.keys())}")
        
        if 'tools' in result and result['tools']:
            tool = result['tools'][0]
            print(f"Tool name: {tool.name}")
            print(f"Tool version: {tool.version}")
            print(f"Tool capabilities: {list(tool.capabilities.keys())}")
        
        if 'metadata' in result:
            print(f"Metadata version: {result['metadata'].get('version', 'unknown')}")
    
    print("✅ Plugin test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
