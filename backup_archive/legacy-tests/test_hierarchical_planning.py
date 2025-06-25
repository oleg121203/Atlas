#!/usr/bin/env python3
"""
Test script for Hierarchical Planning with email tasks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.agents.hierarchical_plan_manager import HierarchicalPlanManager
from modules.agents.tool_registry import tool_registry

def test_hierarchical_planning():
    """Test hierarchical planning with email tasks."""
    
    print("🧪 Testing Hierarchical Planning...")
    print("=" * 50)
    
    # Create a mock LLM manager for testing
    class MockLLMManager:
        def get_response(self, prompt):
            return "Mock response"
    
    # Create a mock strategic planner
    class MockStrategicPlanner:
        def create_plan(self, goal, context=None):
            return ["Phase 1: Access Gmail", "Phase 2: Search emails"]
    
    # Create a mock tactical planner
    class MockTacticalPlanner:
        def create_plan(self, objective, context=None):
            return [
                {"sub_goal": "Access Gmail account", "description": "Open Gmail"},
                {"sub_goal": "Search for security emails", "description": "Find security emails"}
            ]
    
    # Create a mock operational planner
    class MockOperationalPlanner:
        def create_plan(self, sub_goal, context=None):
            return [
                {"tool_name": "EmailFilter", "arguments": {"action": "search_emails"}}
            ]
    
    # Create hierarchical plan manager
    plan_manager = HierarchicalPlanManager(
        llm_manager=MockLLMManager(),
        strategic_planner=MockStrategicPlanner(),
        tactical_planner=MockTacticalPlanner(),
        operational_planner=MockOperationalPlanner()
    )
    
    # Test 1: Create plan for email task
    print("\n1. Creating plan for email task:")
    email_goal = "Зайди в мою почту через браузер сафарі, вона мала би бути уже залогінена. Найди всі листи що стосуються безпеки гугл екаунта на одній сторінці джмайл іі виведи мені в чаті по часовому пріоритету з коротким описом всі  листи, що стосуються даного запиту."
    
    plan = plan_manager.create_hierarchical_plan(email_goal)
    
    if plan:
        print("   ✅ Plan created successfully!")
        print(f"   📊 Plan summary: {plan.get('summary', 'N/A')}")
        
        # Show tasks
        tasks = plan_manager.get_all_tasks()
        print(f"   📋 Total tasks: {len(tasks)}")
        
        for task in tasks:
            print(f"      - {task.title} ({task.level.value})")
    else:
        print("   ❌ Failed to create plan")
    
    # Test 2: Test tool assignment for specific tasks
    print("\n2. Testing tool assignment:")
    test_tasks = [
        "Access Gmail account",
        "Search for security emails", 
        "Filter and organize results",
        "Display results in chat"
    ]
    
    for task in test_tasks:
        tool = tool_registry.get_tool_for_task(task)
        print(f"   Task: '{task}' -> Tool: {tool}")
    
    # Test 3: Test operational plan creation
    print("\n3. Testing operational plan creation:")
    for task in test_tasks:
        complexity = {"actions_per_task": 1}
        operational_steps = plan_manager._get_adaptive_operational_plan(task, complexity)
        print(f"   Task: '{task}' -> Steps: {len(operational_steps)}")
        for step in operational_steps:
            print(f"      Tool: {step.get('tool_name')}")
    
    print("\n✅ Hierarchical Planning test completed!")

if __name__ == "__main__":
    test_hierarchical_planning() 