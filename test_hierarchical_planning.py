#!/usr/bin/env python3
"""
Test script for the hierarchical planning system.
This demonstrates the three-level planning structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hierarchical_plan_manager import HierarchicalPlanManager, TaskLevel, TaskStatus, HierarchicalTask
from utils.logger import get_logger

def test_hierarchical_structure():
    """Test the hierarchical task structure creation."""
    print("🧪 Testing Hierarchical Task Structure")
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
    test_goal = "Create a comprehensive project documentation"
    
    print(f"🎯 Goal: {test_goal}")
    print("\n📋 Creating manual hierarchical structure...")
    
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
        strategic_tasks = []
        phases = [
            "Research and gather information",
            "Analyze and process data", 
            "Execute main actions",
            "Validate and finalize"
        ]
        
        for i, phase in enumerate(phases, 1):
            strategic_task = HierarchicalTask(
                title=f"Phase {i}: {phase}",
                description=phase,
                level=TaskLevel.STRATEGIC,
                parent_id=root_task.id
            )
            plan_manager.tasks[strategic_task.id] = strategic_task
            root_task.children.append(strategic_task.id)
            strategic_tasks.append(strategic_task)
            print(f"🎯 Created Phase {i}: {phase}")
            
            # Create tactical level (tasks) for each phase
            tactical_tasks = []
            tasks = [
                f"Execute {phase.lower()}",
                f"Validate {phase.lower()} results"
            ]
            
            for j, task in enumerate(tasks, 1):
                tactical_task = HierarchicalTask(
                    title=f"Task {i}.{j}: {task}",
                    description=task,
                    level=TaskLevel.TACTICAL,
                    parent_id=strategic_task.id
                )
                plan_manager.tasks[tactical_task.id] = tactical_task
                strategic_task.children.append(tactical_task.id)
                tactical_tasks.append(tactical_task)
                print(f"  📝 Created Task {i}.{j}: {task}")
                
                # Create operational level (actions) for each task
                actions = [
                    f"Use tool A for {task.lower()}",
                    f"Use tool B for {task.lower()}"
                ]
                
                for k, action in enumerate(actions, 1):
                    operational_task = HierarchicalTask(
                        title=f"Action {i}.{j}.{k}: {action}",
                        description=f"Execute: {action}",
                        level=TaskLevel.OPERATIONAL,
                        parent_id=tactical_task.id,
                        tools=[f"tool_{chr(64+k)}"],  # tool_A, tool_B, etc.
                        metadata={"tool_args": {"action": action}}
                    )
                    plan_manager.tasks[operational_task.id] = operational_task
                    tactical_task.children.append(operational_task.id)
                    print(f"    ⚙️ Created Action {i}.{j}.{k}: {action}")
        
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
        
        print("\n✅ Hierarchical structure created successfully!")
        print("📊 Structure Statistics:")
        print(f"   • Total tasks: {plan_manager.current_plan['total_tasks']}")
        print(f"   • Strategic phases: {plan_manager.current_plan['strategic_tasks']}")
        print(f"   • Tactical tasks: {plan_manager.current_plan['tactical_tasks']}")
        print(f"   • Operational actions: {plan_manager.current_plan['operational_tasks']}")
        
        # Display task hierarchy
        print("\n🌳 Task Hierarchy:")
        display_task_hierarchy(plan_manager, plan_manager.root_task_id)
        
        # Test task operations
        print("\n🔧 Testing Task Operations:")
        test_task_operations(plan_manager)
        
        print("\n✅ All tests completed successfully!")
        
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
    
    print(f"{indent}{emoji} {level_icon} {task.title} ({task.status.value})")
    
    # Display children
    for child_id in task.children:
        display_task_hierarchy(plan_manager, child_id, level + 1)

def test_task_operations(plan_manager):
    """Test various task operations."""
    # Get first operational task
    operational_tasks = [t for t in plan_manager.tasks.values() if t.level == TaskLevel.OPERATIONAL]
    
    if not operational_tasks:
        print("   ⚠️ No operational tasks found for testing")
        return
        
    test_task = operational_tasks[0]
    print(f"   🧪 Testing operations on: {test_task.title}")
    
    # Test status updates
    print(f"   📊 Current status: {test_task.status.value}")
    
    # Test starting a task
    plan_manager.update_task_status(test_task.id, TaskStatus.RUNNING)
    print(f"   ▶️ Started task: {test_task.status.value}")
    
    # Test progress update
    plan_manager.update_task_progress(test_task.id, 0.5)
    print(f"   📈 Progress updated: {test_task.progress:.1%}")
    
    # Test completing a task
    plan_manager.update_task_status(test_task.id, TaskStatus.COMPLETED)
    print(f"   ✅ Completed task: {test_task.status.value}")

if __name__ == "__main__":
    import time
    test_hierarchical_structure() 