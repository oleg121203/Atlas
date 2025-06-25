#!/usr/bin/env python3
"""
Test script for Adaptive Execution Manager

Tests the adaptive execution system with self-diagnosis and strategy adaptation.
"""

import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.adaptive_execution_manager import adaptive_execution_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_email_task_adaptation():
    """Test adaptive execution for email tasks."""
    print("🧪 Testing Email Task Adaptation")
    print("=" * 50)
    
    task_description = "Find all emails related to Google account security in Gmail"
    goal_criteria = {
        "emails": True,
        "security_emails": True
    }
    
    print(f"Task: {task_description}")
    print(f"Goal Criteria: {goal_criteria}")
    print()
    
    # Execute with adaptation
    result = adaptive_execution_manager.execute_with_adaptation(
        task_description=task_description,
        goal_criteria=goal_criteria
    )
    
    # Display results
    print("📊 Execution Results:")
    print(f"Success: {result.get('success')}")
    print(f"Attempts Used: {result.get('attempts_used', 0)}")
    print(f"Final Strategy: {result.get('final_strategy', 'N/A')}")
    print(f"Total Execution Time: {result.get('total_execution_time', 0):.2f}s")
    print(f"Message: {result.get('message', 'N/A')}")
    
    # Display adaptation history
    if result.get('adaptation_history'):
        print("\n🔄 Adaptation History:")
        for i, adaptation in enumerate(result['adaptation_history'], 1):
            print(f"  {i}. Attempt {adaptation['attempt_num']}: {adaptation['adaptation_reason']}")
            if 'diagnosis' in adaptation:
                issues = adaptation['diagnosis'].get('issues_found', [])
                if issues:
                    print(f"     Issues: {', '.join(issues)}")
    
    # Display diagnostics if failed
    if not result.get('success') and 'diagnostics' in result:
        print("\n🔍 Failure Diagnostics:")
        for attempt in result['diagnostics']['all_attempts']:
            print(f"  Strategy: {attempt['strategy']}")
            print(f"  Status: {attempt['status']}")
            if attempt['error']:
                print(f"  Error: {attempt['error']}")
            if attempt['diagnostics']:
                print(f"  Diagnostics: {attempt['diagnostics']}")
    
    print("\n" + "=" * 50)
    return result

def test_browser_task_adaptation():
    """Test adaptive execution for browser tasks."""
    print("🧪 Testing Browser Task Adaptation")
    print("=" * 50)
    
    task_description = "Navigate to Gmail using Safari browser and search for security emails"
    goal_criteria = {
        "navigation": True,
        "search": True
    }
    
    print(f"Task: {task_description}")
    print(f"Goal Criteria: {goal_criteria}")
    print()
    
    # Execute with adaptation
    result = adaptive_execution_manager.execute_with_adaptation(
        task_description=task_description,
        goal_criteria=goal_criteria
    )
    
    # Display results
    print("📊 Execution Results:")
    print(f"Success: {result.get('success')}")
    print(f"Attempts Used: {result.get('attempts_used', 0)}")
    print(f"Final Strategy: {result.get('final_strategy', 'N/A')}")
    print(f"Total Execution Time: {result.get('total_execution_time', 0):.2f}s")
    print(f"Message: {result.get('message', 'N/A')}")
    
    print("\n" + "=" * 50)
    return result

def test_adaptive_strategy_generation():
    """Test adaptive strategy generation."""
    print("🧪 Testing Adaptive Strategy Generation")
    print("=" * 50)
    
    # Test different task types
    tasks = [
        "Send email via API",
        "Browse website with automation",
        "Process files manually",
        "Unknown task type"
    ]
    
    for task in tasks:
        strategies = adaptive_execution_manager._get_strategies_for_task(task)
        print(f"Task: {task}")
        print(f"Strategies: {[s.value for s in strategies]}")
        print()
    
    print("=" * 50)

def test_goal_achievement_detection():
    """Test goal achievement detection."""
    print("🧪 Testing Goal Achievement Detection")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "result": {"success": True, "data": {"emails": [{"subject": "Security Alert"}]}},
            "criteria": {"emails": True, "security_emails": True},
            "expected": True
        },
        {
            "result": {"success": True, "data": {"emails": []}},
            "criteria": {"emails": True},
            "expected": False
        },
        {
            "result": {"success": False},
            "criteria": {"emails": True},
            "expected": False
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        result = adaptive_execution_manager._is_goal_achieved(case["result"], case["criteria"])
        print(f"Test {i}: Expected {case['expected']}, Got {result}")
        print(f"  Result: {case['result']}")
        print(f"  Criteria: {case['criteria']}")
        print()
    
    print("=" * 50)

def main():
    """Run all tests."""
    print("🚀 Starting Adaptive Execution Manager Tests")
    print("=" * 60)
    
    try:
        # Test strategy generation
        test_adaptive_strategy_generation()
        
        # Test goal achievement detection
        test_goal_achievement_detection()
        
        # Test email task adaptation
        email_result = test_email_task_adaptation()
        
        # Test browser task adaptation
        browser_result = test_browser_task_adaptation()
        
        # Summary
        print("📋 Test Summary")
        print("=" * 60)
        print(f"Email Task Success: {email_result.get('success')}")
        print(f"Browser Task Success: {browser_result.get('success')}")
        
        total_adaptations = len(email_result.get('adaptation_history', [])) + len(browser_result.get('adaptation_history', []))
        print(f"Total Adaptations Made: {total_adaptations}")
        
        if total_adaptations > 0:
            print("✅ Adaptive execution system is working - strategies are being adapted!")
        else:
            print("ℹ️  No adaptations needed - all tasks succeeded on first attempt")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Adaptive Execution Manager Tests Completed!")

if __name__ == "__main__":
    main() 