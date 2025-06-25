#!/usr/bin/env python3
"""
Test script for the adaptive hierarchical planning system.
This demonstrates how the system adapts task complexity based on goal analysis.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hierarchical_plan_manager import HierarchicalPlanManager, TaskLevel, TaskStatus

def test_adaptive_planning():
    """Test the adaptive hierarchical planning system."""
    print("🧪 Testing Adaptive Hierarchical Planning System")
    print("=" * 60)
    
    # Create a simple hierarchical plan manager without LLM dependencies
    plan_manager = HierarchicalPlanManager(
        llm_manager=None,
        strategic_planner=None,
        tactical_planner=None,
        operational_planner=None,
        status_callback=lambda msg: print(f"📢 {msg.get('content', '')}")
    )
    
    # Test with the user's specific goal
    user_goal = "Зайди в мою почту через браузер сафарі, вона мала би бути уже залогінена. Найди всі листи що стосуються безпеки гугл екаунта на одній сторінці джмайл іі виведи мені в чаті по часовому пріоритету з коротким описом всі листи, що стосуються даного запиту."
    
    print(f"🎯 Testing Goal: {user_goal}")
    print("-" * 60)
    
    # Analyze complexity
    complexity = plan_manager._analyze_goal_complexity(user_goal)
    print("📊 Complexity Analysis:")
    print(f"   • Level: {complexity['level']}")
    print(f"   • Phases: {complexity['phases']}")
    print(f"   • Tasks per phase: {complexity['tasks_per_phase']}")
    print(f"   • Actions per task: {complexity['actions_per_task']}")
    print(f"   • Simple keywords: {complexity['simple_keywords']}")
    print(f"   • Medium keywords: {complexity['medium_keywords']}")
    print(f"   • Complex keywords: {complexity['complex_keywords']}")
    print()
    
    # Create plan
    plan = plan_manager.create_hierarchical_plan(user_goal)
    
    if plan:
        print("✅ Plan created successfully!")
        print("📊 Plan Statistics:")
        print(f"   • Total tasks: {plan['total_tasks']}")
        print(f"   • Strategic phases: {plan['strategic_tasks']}")
        print(f"   • Tactical tasks: {plan['tactical_tasks']}")
        print(f"   • Operational actions: {plan['operational_tasks']}")
        print()
        
        # Show task hierarchy
        print("🌳 Task Hierarchy:")
        root_task = plan_manager.get_task(plan['root_task_id'])
        if root_task:
            _print_task_hierarchy(root_task, plan_manager, 0)
    else:
        print("❌ Failed to create plan")

def _print_task_hierarchy(task, plan_manager, level):
    """Print the task hierarchy recursively."""
    indent = "  " * level
    status_emoji = {
        TaskStatus.PENDING: "⏳",
        TaskStatus.RUNNING: "▶️",
        TaskStatus.COMPLETED: "✅",
        TaskStatus.FAILED: "❌"
    }
    
    level_emoji = {
        TaskLevel.STRATEGIC: "🎯",
        TaskLevel.TACTICAL: "📝",
        TaskLevel.OPERATIONAL: "⚙️"
    }
    
    emoji = status_emoji.get(task.status, "⏳")
    level_icon = level_emoji.get(task.level, "📋")
    
    print(f"{indent}{emoji} {level_icon} {task.title} ({task.status.value})")
    
    # Print children
    for child_id in task.children:
        child_task = plan_manager.get_task(child_id)
        if child_task:
            _print_task_hierarchy(child_task, plan_manager, level + 1)

def test_complexity_levels():
    """Test different complexity levels."""
    print("\n🧪 Testing Different Complexity Levels")
    print("=" * 60)
    
    plan_manager = HierarchicalPlanManager(
        llm_manager=None,
        strategic_planner=None,
        tactical_planner=None,
        operational_planner=None,
        status_callback=lambda msg: None
    )
    
    test_goals = [
        ("Simple goal", "Take a screenshot"),
        ("Medium goal", "Search for files and organize them by date"),
        ("Complex goal", "Create a comprehensive automation system that monitors system performance and generates detailed reports")
    ]
    
    for goal_name, goal_text in test_goals:
        print(f"\n🎯 {goal_name}: {goal_text}")
        complexity = plan_manager._analyze_goal_complexity(goal_text)
        print(f"   • Complexity: {complexity['level']}")
        print(f"   • Expected tasks: {complexity['phases']} × {complexity['tasks_per_phase']} × {complexity['actions_per_task']} = {complexity['phases'] * complexity['tasks_per_phase'] * complexity['actions_per_task']}")

if __name__ == "__main__":
    test_adaptive_planning()
    test_complexity_levels() 