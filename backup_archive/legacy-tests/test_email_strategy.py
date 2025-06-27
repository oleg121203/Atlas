#!/usr/bin/env python3
"""
Test script for Email Strategy Manager
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.agents.email_strategy_manager import email_strategy_manager


def test_email_strategy():
    """Test Email Strategy Manager functionality."""

    print("🧪 Testing Email Strategy Manager...")
    print("=" * 50)

    # Test 1: Check availability
    print("\n1. Checking email access methods availability:")
    print(f"   Gmail API available: {email_strategy_manager.gmail_api_available}")
    print(
        f"   Browser automation available: {email_strategy_manager.browser_available}"
    )

    # Test 2: Test method selection for different tasks
    print("\n2. Testing method selection:")
    test_tasks = [
        "Search for security emails in Gmail",
        "Open Safari browser and go to Gmail",
        "Find Google account security emails",
        "Navigate to Gmail in browser",
        "Search emails for security alerts",
    ]

    for task in test_tasks:
        method = email_strategy_manager.select_access_method(task)
        if method:
            tool = email_strategy_manager.get_tool_for_method(method)
            print(f"   Task: '{task}'")
            print(f"      Method: {method.value}")
            print(f"      Tool: {tool}")
        else:
            print(f"   Task: '{task}' -> No method available")

    # Test 3: Test tool arguments generation
    print("\n3. Testing tool arguments generation:")
    for task in test_tasks[:3]:  # Test first 3 tasks
        method = email_strategy_manager.select_access_method(task)
        if method:
            args = email_strategy_manager.get_tool_arguments(method, task)
            print(f"   Task: '{task}'")
            print(f"      Method: {method.value}")
            print(f"      Arguments: {args}")

    # Test 4: Test task execution
    print("\n4. Testing task execution:")
    test_execution_tasks = ["Search for security emails", "Open Gmail in browser"]

    for task in test_execution_tasks:
        print(f"   Executing: '{task}'")
        result = email_strategy_manager.execute_email_task(task)
        print(f"      Success: {result.get('success', False)}")
        print(f"      Method: {result.get('method', 'unknown')}")
        if result.get("success"):
            print(f"      Message: {result.get('message', 'N/A')}")
        else:
            print(f"      Error: {result.get('error', 'N/A')}")

    print("\n✅ Email Strategy Manager test completed!")


if __name__ == "__main__":
    test_email_strategy()
