#!/usr/bin/env python3
"""
Test script for Safari Professional Tool integration with email system.
Tests the fallback mechanism when regular browser tool fails.
"""

import logging
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.agents.adaptive_execution_manager import AdaptiveExecutionManager
from modules.agents.email_strategy_manager import EmailStrategyManager
from modules.agents.hierarchical_plan_manager import HierarchicalPlanManager
from modules.agents.tool_registry import ToolRegistry

from tools.safari_professional_tool import SafariProfessionalTool


def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                f"test_safari_professional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            ),
        ],
    )


def test_safari_professional_tool_direct():
    """Test Safari Professional Tool directly."""
    print("\n" + "=" * 60)
    print("TESTING SAFARI PROFESSIONAL TOOL DIRECTLY")
    print("=" * 60)

    try:
        safari_tool = SafariProfessionalTool()

        # Test professional email task execution
        result = safari_tool.execute_email_task_professional(
            "Find security emails in Gmail"
        )

        print("Direct Safari Professional Tool Result:")
        print(f"Success: {result.get('success')}")
        print(f"Method: {result.get('method')}")
        print(f"Emails Found: {result.get('emails_found', 0)}")
        print(f"Message: {result.get('message', 'No message')}")

        if result.get("emails"):
            print("\nEmails found:")
            for i, email in enumerate(result["emails"][:3], 1):  # Show first 3 emails
                print(f"{i}. From: {email.get('sender')}")
                print(f"   Subject: {email.get('subject')}")
                print(f"   Priority: {email.get('priority')}")
                print(f"   Date: {email.get('date')}")
                print()

        # Close browser
        safari_tool.close_browser()

        return result.get("success", False) and result.get("emails_found", 0) > 0

    except Exception as e:
        print(f"Error testing Safari Professional Tool directly: {e}")
        return False


def test_email_strategy_with_safari_fallback():
    """Test Email Strategy Manager with Safari Professional fallback."""
    print("\n" + "=" * 60)
    print("TESTING EMAIL STRATEGY WITH SAFARI PROFESSIONAL FALLBACK")
    print("=" * 60)

    try:
        # Initialize Email Strategy Manager
        email_strategy = EmailStrategyManager()

        # Test email task execution
        result = email_strategy.execute_email_task(
            "Come to my mailbox through the Safari browser, it should already be logged in. "
            "Find all emails related to Google account security on one page in Gmail and "
            "send me a list in the chat with a brief description of all emails related to this request, "
            "sorted by chronological priority."
        )

        print("Email Strategy Manager Result:")
        print(f"Success: {result.get('success')}")
        print(f"Method: {result.get('method')}")
        print(f"Message: {result.get('message', 'No message')}")

        if result.get("data", {}).get("emails"):
            emails = result["data"]["emails"]
            print(f"\nEmails found ({len(emails)}):")
            for i, email in enumerate(emails[:3], 1):  # Show first 3 emails
                print(f"{i}. From: {email.get('sender')}")
                print(f"   Subject: {email.get('subject')}")
                print(f"   Priority: {email.get('priority')}")
                print(f"   Date: {email.get('date')}")
                print()

        return (
            result.get("success", False)
            and result.get("data", {}).get("emails_found", 0) > 0
        )

    except Exception as e:
        print(f"Error testing Email Strategy with Safari fallback: {e}")
        return False


def test_hierarchical_planning_with_safari():
    """Test Hierarchical Plan Manager with Safari Professional integration."""
    print("\n" + "=" * 60)
    print("TESTING HIERARCHICAL PLAN MANAGER WITH SAFARI PROFESSIONAL")
    print("=" * 60)

    try:
        # Initialize components
        ToolRegistry()
        EmailStrategyManager()
        AdaptiveExecutionManager()

        # Create mock components for HierarchicalPlanManager
        class MockLLMManager:
            def __init__(self):
                pass

        class MockStrategicPlanner:
            def __init__(self):
                pass

        class MockTacticalPlanner:
            def __init__(self):
                pass

        class MockOperationalPlanner:
            def __init__(self):
                pass

        # Create hierarchical plan manager with mock components
        plan_manager = HierarchicalPlanManager(
            llm_manager=MockLLMManager(),
            strategic_planner=MockStrategicPlanner(),
            tactical_planner=MockTacticalPlanner(),
            operational_planner=MockOperationalPlanner(),
        )

        # Test task
        task = {
            "goal": "Come to my mailbox through the Safari browser, it should already be logged in. "
            "Find all emails related to Google account security on one page in Gmail and "
            "send me a list in the chat with a brief description of all emails related to this request, "
            "sorted by chronological priority.",
            "priority": "high",
            "deadline": "immediate",
        }

        # Execute plan
        result = plan_manager.execute_plan(task)

        print("Hierarchical Plan Manager Result:")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message', 'No message')}")
        print(f"Adaptation History: {result.get('adaptation_history', [])}")

        if result.get("data", {}).get("emails"):
            emails = result["data"]["emails"]
            print(f"\nFinal emails found ({len(emails)}):")
            for i, email in enumerate(emails[:3], 1):  # Show first 3 emails
                print(f"{i}. From: {email.get('sender')}")
                print(f"   Subject: {email.get('subject')}")
                print(f"   Priority: {email.get('priority')}")
                print(f"   Date: {email.get('date')}")
                print()

        return result.get("success", False)

    except Exception as e:
        print(f"Error testing Hierarchical Plan Manager with Safari: {e}")
        return False


def main():
    """Main test function."""
    print("SAFARI PROFESSIONAL TOOL INTEGRATION TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")

    # Setup logging
    setup_logging()

    # Test results
    test_results = []

    # Test 1: Direct Safari Professional Tool
    print("\n1. Testing Safari Professional Tool directly...")
    result1 = test_safari_professional_tool_direct()
    test_results.append(("Direct Safari Professional Tool", result1))

    # Test 2: Email Strategy with Safari fallback
    print("\n2. Testing Email Strategy with Safari fallback...")
    result2 = test_email_strategy_with_safari_fallback()
    test_results.append(("Email Strategy with Safari Fallback", result2))

    # Test 3: Hierarchical Planning with Safari
    print("\n3. Testing Hierarchical Planning with Safari...")
    result3 = test_hierarchical_planning_with_safari()
    test_results.append(("Hierarchical Planning with Safari", result3))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print(
        f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
    )
    print(f"Test completed at: {datetime.now()}")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
