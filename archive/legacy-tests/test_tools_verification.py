#!/usr/bin/env python3
"""
Test script for tools and plugins verification in hierarchical planning
"""

import customtkinter as ctk
import threading
import time
from agents.hierarchical_plan_manager import HierarchicalPlanManager
from utils.llm_manager import LLMManager
from utils.config_manager import ConfigManager
from agents.task_aware_master_agent import TaskAwareMasterAgent

def create_mock_llm_manager():
    """Create a mock LLM manager for testing."""
    config_manager = ConfigManager()
    from agents.token_tracker import TokenTracker
    token_tracker = TokenTracker()
    return LLMManager(token_tracker=token_tracker, config_manager=config_manager)

def create_mock_planners():
    """Create mock planners for testing."""
    class MockPlanner:
        def plan(self, *args, **kwargs):
            return ["Mock plan step"]
    
    return MockPlanner(), MockPlanner(), MockPlanner()

def test_tools_assignment():
    """Test that tools are properly assigned to tasks."""
    print("🔧 Testing tools assignment...")
    
    # Create hierarchical plan manager
    llm_manager = create_mock_llm_manager()
    strategic_planner, tactical_planner, operational_planner = create_mock_planners()
    
    plan_manager = HierarchicalPlanManager(
        llm_manager=llm_manager,
        strategic_planner=strategic_planner,
        tactical_planner=tactical_planner,
        operational_planner=operational_planner
    )
    
    # Test different goals to see tool assignment
    test_goals = [
        "Take a screenshot of my email inbox",
        "Open Safari and search for security emails in Gmail",
        "Click on the login button and type my password",
        "Copy the text from the screen and paste it into a file",
        "Execute terminal command to check system status"
    ]
    
    for goal in test_goals:
        print(f"\n🎯 Testing goal: {goal}")
        
        try:
            # Create hierarchical plan
            context = {"prompt": "Test execution", "options": {"cyclic": False}}
            plan = plan_manager.create_hierarchical_plan(goal, context)
            
            if not plan:
                print("❌ Failed to create plan")
                continue
                
            # Check tool assignment
            all_tasks = plan_manager.get_all_tasks()
            operational_tasks = [t for t in all_tasks if t.level.value == "operational"]
            
            print(f"📊 Found {len(operational_tasks)} operational tasks")
            
            for task in operational_tasks:
                tools = task.tools
                print(f"  ⚡ Task: {task.title}")
                print(f"    🛠️ Tools: {tools}")
                
                # Check if specific tools are assigned
                if "screenshot" in task.title.lower() and "screenshot_tool" not in tools:
                    print("    ⚠️ Warning: Screenshot task missing screenshot_tool")
                    
                if "browser" in task.title.lower() and "web_browser_tool" not in tools:
                    print("    ⚠️ Warning: Browser task missing web_browser_tool")
                    
                if "search" in task.title.lower() and "search_tool" not in tools:
                    print("    ⚠️ Warning: Search task missing search_tool")
                    
                if "click" in task.title.lower() and "mouse_keyboard_tool" not in tools:
                    print("    ⚠️ Warning: Click task missing mouse_keyboard_tool")
                    
        except Exception as e:
            print(f"❌ Error testing goal '{goal}': {e}")

def test_ui_display():
    """Test UI display of tools and plugins."""
    print("\n🖥️ Testing UI display...")
    
    # Create test window
    root = ctk.CTk()
    root.title("Tools Verification Test")
    root.geometry("800x600")
    
    # Create hierarchical task view
    from ui.hierarchical_task_view import HierarchicalTaskView
    
    task_view = HierarchicalTaskView(root)
    task_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create test plan data with tools
    test_plan_data = {
        "goal": "Test email security analysis",
        "root_task_id": "strategic_1",
        "total_tasks": 6,
        "tasks": [
            {
                "id": "strategic_1",
                "title": "Email Security Analysis",
                "description": "Analyze email security settings",
                "level": "strategic",
                "status": "completed",
                "progress": 1.0,
                "parent_id": None,
                "children": ["tactical_1", "tactical_2"],
                "tools": [],
                "plugins": [],
                "created_at": time.time() - 300,
                "started_at": time.time() - 280,
                "completed_at": time.time() - 50
            },
            {
                "id": "tactical_1",
                "title": "Access Email System",
                "description": "Open browser and navigate to Gmail",
                "level": "tactical",
                "status": "completed",
                "progress": 1.0,
                "parent_id": "strategic_1",
                "children": ["operational_1", "operational_2"],
                "tools": ["web_browser_tool"],
                "plugins": ["unified_browser"],
                "created_at": time.time() - 280,
                "started_at": time.time() - 270,
                "completed_at": time.time() - 200
            },
            {
                "id": "operational_1",
                "title": "Open Safari Browser",
                "description": "Launch Safari browser application",
                "level": "operational",
                "status": "completed",
                "progress": 1.0,
                "parent_id": "tactical_1",
                "children": [],
                "tools": ["web_browser_tool"],
                "plugins": ["unified_browser"],
                "created_at": time.time() - 270,
                "started_at": time.time() - 265,
                "completed_at": time.time() - 260
            },
            {
                "id": "operational_2",
                "title": "Navigate to Gmail",
                "description": "Go to Gmail website and login",
                "level": "operational",
                "status": "completed",
                "progress": 1.0,
                "parent_id": "tactical_1",
                "children": [],
                "tools": ["web_browser_tool", "mouse_keyboard_tool"],
                "plugins": ["unified_browser"],
                "created_at": time.time() - 260,
                "started_at": time.time() - 255,
                "completed_at": time.time() - 200
            },
            {
                "id": "tactical_2",
                "title": "Search Security Emails",
                "description": "Find and analyze security-related emails",
                "level": "tactical",
                "status": "running",
                "progress": 0.6,
                "parent_id": "strategic_1",
                "children": ["operational_3", "operational_4"],
                "tools": ["search_tool", "screenshot_tool"],
                "plugins": ["unified_browser"],
                "created_at": time.time() - 200,
                "started_at": time.time() - 190,
                "completed_at": None
            },
            {
                "id": "operational_3",
                "title": "Search for Security Emails",
                "description": "Use Gmail search to find security emails",
                "level": "operational",
                "status": "completed",
                "progress": 1.0,
                "parent_id": "tactical_2",
                "children": [],
                "tools": ["search_tool"],
                "plugins": ["web_browsing"],
                "created_at": time.time() - 190,
                "started_at": time.time() - 185,
                "completed_at": time.time() - 180
            },
            {
                "id": "operational_4",
                "title": "Take Screenshot of Results",
                "description": "Capture screenshot of search results",
                "level": "operational",
                "status": "running",
                "progress": 0.6,
                "parent_id": "tactical_2",
                "children": [],
                "tools": ["screenshot_tool"],
                "plugins": [],
                "created_at": time.time() - 180,
                "started_at": time.time() - 175,
                "completed_at": None
            }
        ]
    }
    
    # Update the view with test data
    task_view.update_plan(test_plan_data)
    
    print("✅ Test window opened. Check that:")
    print("  1. Tools are displayed in task details")
    print("  2. Plugins are shown for each task")
    print("  3. Specific tools match task content")
    print("  4. UI remains responsive during loading")
    
    # Run the window
    root.mainloop()

def main():
    """Main test function."""
    print("🔍 Tools and Plugins Verification Test")
    print("=" * 50)
    
    # Test tools assignment
    test_tools_assignment()
    
    # Test UI display
    test_ui_display()
    
    print("\n✅ Verification test completed!")

if __name__ == "__main__":
    main() 