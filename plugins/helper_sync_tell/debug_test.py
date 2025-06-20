#!/usr/bin/env python3
"""
Debug test for Helper Sync Tell plugin.
"""

import sys
import os
import traceback

print("🔍 Helper Sync Tell Plugin Debug Test")
print("=" * 50)

print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}...")

print("\n1. Testing basic imports...")
try:
    import logging
    import time
    import uuid
    import json
    print("✅ Standard library imports successful")
except Exception as e:
    print(f"❌ Standard library import error: {e}")

print("\n2. Testing platform detection...")
try:
    import platform
    system = platform.system()
    print(f"✅ Platform detected: {system}")
except Exception as e:
    print(f"❌ Platform detection error: {e}")

print("\n3. Testing plugin import...")
try:
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    import plugin
    print("✅ Plugin module imported successfully")
    
    # Check if main function exists
    if hasattr(plugin, 'register_enhanced_helper_sync_tell_tool'):
        print("✅ Registration function found")
    else:
        print("❌ Registration function not found")
        print(f"Available attributes: {[attr for attr in dir(plugin) if not attr.startswith('_')]}")
        
except Exception as e:
    print(f"❌ Plugin import error: {e}")
    traceback.print_exc()

print("\n4. Testing plugin execution...")
try:
    result = plugin.register_enhanced_helper_sync_tell_tool()
    print("✅ Plugin registration executed")
    print(f"Result type: {type(result)}")
    if isinstance(result, dict):
        print(f"Result keys: {list(result.keys())}")
        if 'tools' in result:
            print(f"Tools count: {len(result['tools'])}")
        if 'metadata' in result:
            print(f"Metadata: {result['metadata']}")
except Exception as e:
    print(f"❌ Plugin execution error: {e}")
    traceback.print_exc()

print("\n5. Testing encoding...")
try:
    with open('plugin.py', 'r', encoding='utf-8') as f:
        content = f.read()
        # Check for problematic characters
        non_ascii_chars = [c for c in content if ord(c) > 127]
        if non_ascii_chars:
            unique_chars = list(set(non_ascii_chars))
            print(f"Non-ASCII characters found: {unique_chars[:10]}...")
            # Check if they are Cyrillic
            cyrillic_chars = [c for c in unique_chars if ord(c) >= 0x400 and ord(c) <= 0x4FF]
            if cyrillic_chars:
                print(f"❌ Cyrillic characters found: {cyrillic_chars}")
            else:
                print("✅ Non-ASCII characters are not Cyrillic")
        else:
            print("✅ No non-ASCII characters found")
except Exception as e:
    print(f"❌ Encoding check error: {e}")

print("\n" + "=" * 50)
print("Debug test completed!")
