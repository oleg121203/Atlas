#!/usr/bin/env python3
"""
Test script for Tool Registry functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.tool_registry import tool_registry

def test_tool_registry():
    """Test Tool Registry functionality."""
    
    print("🧪 Testing Tool Registry...")
    print("=" * 50)
    
    # Test 1: Check if tools are registered
    print("\n1. Checking registered tools:")
    all_tools = tool_registry.list_all_tools()
    for category, tools in all_tools.items():
        print(f"   {category}: {tools}")
    
    # Test 2: Test tool assignment for email tasks
    print("\n2. Testing email task tool assignment:")
    email_tasks = [
        "Search for security emails in Gmail",
        "Find Google account security emails",
        "Access Gmail and search for security",
        "Open Gmail and find security emails"
    ]
    
    for task in email_tasks:
        tool = tool_registry.get_tool_for_task(task)
        print(f"   Task: '{task}' -> Tool: {tool}")
    
    # Test 3: Test tool assignment for browser tasks
    print("\n3. Testing browser task tool assignment:")
    browser_tasks = [
        "Open Safari browser",
        "Navigate to website",
        "Open browser and go to Gmail"
    ]
    
    for task in browser_tasks:
        tool = tool_registry.get_tool_for_task(task)
        print(f"   Task: '{task}' -> Tool: {tool}")
    
    # Test 4: Test tool assignment for screenshot tasks
    print("\n4. Testing screenshot task tool assignment:")
    screenshot_tasks = [
        "Capture screen",
        "Take screenshot",
        "Capture image"
    ]
    
    for task in screenshot_tasks:
        tool = tool_registry.get_tool_for_task(task)
        print(f"   Task: '{task}' -> Tool: {tool}")
    
    # Test 5: Test tool validation
    print("\n5. Testing tool validation:")
    test_tools = ["EmailFilter", "BrowserTool", "screenshot_tool", "nonexistent_tool"]
    for tool in test_tools:
        exists = tool_registry.validate_tool_exists(tool)
        print(f"   Tool '{tool}' exists: {exists}")
    
    # Test 6: Test tool info
    print("\n6. Testing tool info:")
    for tool in ["EmailFilter", "BrowserTool"]:
        info = tool_registry.get_tool_info(tool)
        if info:
            print(f"   {tool}: {info['description']}")
    
    print("\n✅ Tool Registry test completed!")

if __name__ == "__main__":
    test_tool_registry() 