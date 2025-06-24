#!/usr/bin/env python3
"""
Test script for hierarchical plan execution.
This demonstrates the execution of the three-level planning structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hierarchical_plan_manager import HierarchicalPlanManager, TaskLevel, TaskStatus, HierarchicalTask
from utils.logger import get_logger
import time

def test_plan_execution():
    """Test the hierarchical plan execution."""
    print("🧪 Testing Hierarchical Plan Execution")
    print("=" * 50)
    
    # Create a simple hierarchical plan manager without LLM dependencies
    plan_manager = HierarchicalPlanManager(
        llm_manager=None,
        strategic_planner=None,
        tactical_planner=None,
        operational_planner=None,
        status_callback=lambda msg: print(f"📢 {msg.get('content', '')}")
    )
    
    # Test goal
    test_goal = "Open a website and take a screenshot"
    
    print(f"🎯 Goal: {test_goal}")
    print("\n📋 Creating hierarchical structure...")
    
    try:
        # Create root task
        root_task = HierarchicalTask(
            title=test_goal,
            description=f"Main goal: {test_goal}",
            level=TaskLevel.STRATEGIC,
            status=TaskStatus.PENDING
        )
        plan_manager.tasks[root_task.id] = root_task
        plan_manager.root_task_id = root_task.id
        
        # Create strategic level (phases)
        strategic_task = HierarchicalTask(
            title="Phase 1: Web Interaction",
            description="Interact with web browser",
            level=TaskLevel.STRATEGIC,
            parent_id=root_task.id
        )
        plan_manager.tasks[strategic_task.id] = strategic_task
        root_task.children.append(strategic_task.id)
        
        # Create tactical level (tasks)
        tactical_task = HierarchicalTask(
            title="Task 1.1: Open website",
            description="Open the target website",
            level=TaskLevel.TACTICAL,
            parent_id=strategic_task.id
        )
        plan_manager.tasks[tactical_task.id] = tactical_task
        strategic_task.children.append(tactical_task.id)
        
        # Create operational level (actions)
        operational_task1 = HierarchicalTask(
            title="Action 1.1.1: Open browser",
            description="Execute: Open web browser",
            level=TaskLevel.OPERATIONAL,
            parent_id=tactical_task.id,
            tools=["open_browser"],
            metadata={"tool_args": {"url": "https://www.google.com"}}
        )
        plan_manager.tasks[operational_task1.id] = operational_task1
        tactical_task.children.append(operational_task1.id)
        
        operational_task2 = HierarchicalTask(
            title="Action 1.1.2: Take screenshot",
            description="Execute: Capture screen",
            level=TaskLevel.OPERATIONAL,
            parent_id=tactical_task.id,
            tools=["capture_screen"],
            metadata={"tool_args": {"save_path": "screenshot.png"}}
        )
        plan_manager.tasks[operational_task2.id] = operational_task2
        tactical_task.children.append(operational_task2.id)
        
        # Create plan structure
        plan_manager.current_plan = {
            "goal": test_goal,
            "root_task_id": root_task.id,
            "total_tasks": len(plan_manager.tasks),
            "strategic_tasks": len([t for t in plan_manager.tasks.values() if t.level == TaskLevel.STRATEGIC]),
            "tactical_tasks": len([t for t in plan_manager.tasks.values() if t.level == TaskLevel.TACTICAL]),
            "operational_tasks": len([t for t in plan_manager.tasks.values() if t.level == TaskLevel.OPERATIONAL]),
            "created_at": time.time()
        }
        
        print("✅ Hierarchical structure created successfully!")
        print("📊 Structure Statistics:")
        print(f"   • Total tasks: {plan_manager.current_plan['total_tasks']}")
        print(f"   • Strategic phases: {plan_manager.current_plan['strategic_tasks']}")
        print(f"   • Tactical tasks: {plan_manager.current_plan['tactical_tasks']}")
        print(f"   • Operational actions: {plan_manager.current_plan['operational_tasks']}")
        
        # Display task hierarchy before execution
        print("\n🌳 Task Hierarchy (Before Execution):")
        display_task_hierarchy(plan_manager, plan_manager.root_task_id)
        
        # Execute the plan
        print("\n🚀 Executing Plan...")
        success = plan_manager.execute_plan()
        
        print(f"\n📊 Execution Result: {'✅ Success' if success else '❌ Failed'}")
        
        # Display task hierarchy after execution
        print("\n🌳 Task Hierarchy (After Execution):")
        display_task_hierarchy(plan_manager, plan_manager.root_task_id)
        
        # Validate completion
        validation_result = plan_manager.validate_goal_completion(test_goal)
        print("\n📋 Validation Result:")
        print(f"   • Success: {validation_result['success']}")
        print(f"   • Completion Rate: {validation_result['completion_rate']:.1%}")
        print(f"   • Completed Tasks: {validation_result['completed_tasks']}")
        print(f"   • Total Tasks: {validation_result['total_tasks']}")
        
        print("\n✅ Plan execution test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def display_task_hierarchy(plan_manager, root_task_id, level=0):
    """Display the task hierarchy in a tree-like format."""
    if not root_task_id:
        return
        
    task = plan_manager.get_task(root_task_id)
    if not task:
        return
        
    indent = "  " * level
    status_emoji = {
        TaskStatus.PENDING: "⏳",
        TaskStatus.RUNNING: "▶️",
        TaskStatus.COMPLETED: "✅",
        TaskStatus.FAILED: "❌",
        TaskStatus.PAUSED: "⏸️",
        TaskStatus.CANCELLED: "🚫"
    }
    
    level_emoji = {
        TaskLevel.STRATEGIC: "🎯",
        TaskLevel.TACTICAL: "📝",
        TaskLevel.OPERATIONAL: "⚙️"
    }
    
    emoji = status_emoji.get(task.status, "📋")
    level_icon = level_emoji.get(task.level, "📋")
    
    progress_text = f" ({task.progress:.1%})" if task.progress > 0 else ""
    print(f"{indent}{emoji} {level_icon} {task.title} ({task.status.value}){progress_text}")
    
    # Display children
    for child_id in task.children:
        display_task_hierarchy(plan_manager, child_id, level + 1)

if __name__ == "__main__":
    test_plan_execution() 