#!/usr/bin/env python3
"""
Test script for email security request analysis
"""

import customtkinter as ctk
import threading
import time
from agents.hierarchical_plan_manager import HierarchicalPlanManager
from utils.llm_manager import LLMManager
from utils.config_manager import ConfigManager
from agents.token_tracker import TokenTracker

def create_mock_llm_manager():
    """Create a mock LLM manager for testing."""
    config_manager = ConfigManager()
    token_tracker = TokenTracker()
    return LLMManager(token_tracker=token_tracker, config_manager=config_manager)

def create_mock_planners():
    """Create mock planners for testing."""
    class MockPlanner:
        def plan(self, *args, **kwargs):
            return ["Mock plan step"]
    
    return MockPlanner(), MockPlanner(), MockPlanner()

def test_email_security_request():
    """Test the specific email security request."""
    print("🔍 Testing Email Security Request")
    print("=" * 50)
    
    # The exact request from user
    user_request = """Зайди в мою почту через браузер сафарі, вона мала би бути вже залогінена. Найди всі листи що стосуються безпеки гугл екаунта на одній сторінці джмайл іі виведи мені в чаті по часовому пріоритету з коротким описом всі листи, що стосуються даного запиту."""
    
    print(f"🎯 User Request: {user_request}")
    print()
    
    # Create hierarchical plan manager
    llm_manager = create_mock_llm_manager()
    strategic_planner, tactical_planner, operational_planner = create_mock_planners()
    
    plan_manager = HierarchicalPlanManager(
        llm_manager=llm_manager,
        strategic_planner=strategic_planner,
        tactical_planner=tactical_planner,
        operational_planner=operational_planner
    )
    
    try:
        print("📋 Creating hierarchical plan...")
        
        # Create hierarchical plan
        context = {"prompt": "Email security analysis", "options": {"cyclic": False}}
        plan = plan_manager.create_hierarchical_plan(user_request, context)
        
        if not plan:
            print("❌ Failed to create plan")
            return
            
        print("✅ Plan created successfully!")
        print(f"📊 Root task ID: {plan.get('root_task_id')}")
        print(f"📊 Total tasks: {plan.get('total_tasks', 0)}")
        
        # Analyze the plan structure
        all_tasks = plan_manager.get_all_tasks()
        
        print("\n🏗️ Plan Structure Analysis:")
        print(f"   Total tasks: {len(all_tasks)}")
        
        strategic_tasks = [t for t in all_tasks if t.level.value == "strategic"]
        tactical_tasks = [t for t in all_tasks if t.level.value == "tactical"]
        operational_tasks = [t for t in all_tasks if t.level.value == "operational"]
        
        print(f"   Strategic tasks: {len(strategic_tasks)}")
        print(f"   Tactical tasks: {len(tactical_tasks)}")
        print(f"   Operational tasks: {len(operational_tasks)}")
        
        # Check tool assignment
        print("\n🛠️ Tool Assignment Analysis:")
        
        for task in operational_tasks:
            tools = task.tools
            print(f"   ⚡ {task.title}")
            print(f"     🛠️ Tools: {tools}")
            
            # Check if appropriate tools are assigned
            if "browser" in task.title.lower() or "safari" in task.title.lower():
                if "web_browser_tool" not in tools:
                    print("     ⚠️ WARNING: Browser task missing web_browser_tool!")
                    
            if "search" in task.title.lower() or "find" in task.title.lower():
                if "search_tool" not in tools:
                    print("     ⚠️ WARNING: Search task missing search_tool!")
                    
            if "email" in task.title.lower() or "gmail" in task.title.lower():
                if "web_browser_tool" not in tools and "search_tool" not in tools:
                    print("     ⚠️ WARNING: Email task missing appropriate tools!")
        
        # Test plan execution
        print("\n🚀 Testing Plan Execution...")
        
        def execute_plan():
            try:
                success = plan_manager.execute_plan()
                if success:
                    print("✅ Plan execution completed successfully!")
                    
                    # Analyze final results
                    results = plan_manager.analyze_final_results(user_request)
                    print("\n📊 Final Results Analysis:")
                    print(f"   Success: {results.get('success', False)}")
                    print(f"   Answer: {results.get('answer', 'No answer provided')}")
                    print(f"   Summary: {results.get('summary', 'No summary')}")
                    
                else:
                    print("❌ Plan execution failed!")
                    
            except Exception as e:
                print(f"❌ Error during plan execution: {e}")
        
        # Execute in background thread
        execution_thread = threading.Thread(target=execute_plan, daemon=True)
        execution_thread.start()
        
        # Wait for execution to complete
        execution_thread.join(timeout=30)
        
        if execution_thread.is_alive():
            print("⏰ Plan execution timed out after 30 seconds")
        
    except Exception as e:
        print(f"❌ Error testing email security request: {e}")
        import traceback
        traceback.print_exc()

def test_ui_display():
    """Test UI display for the email security request."""
    print("\n🖥️ Testing UI Display...")
    
    # Create test window
    root = ctk.CTk()
    root.title("Email Security Request Test")
    root.geometry("1000x700")
    
    # Create hierarchical task view
    from ui.hierarchical_task_view import HierarchicalTaskView
    
    task_view = HierarchicalTaskView(root)
    task_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create test plan data for email security request
    test_plan_data = {
        "goal": "Зайди в мою почту через браузер сафарі, вона мала би бути вже залогінена. Найди всі листи що стосуються безпеки гугл екаунта на одній сторінці джмайл іі виведи мені в чаті по часовому пріоритету з коротким описом всі листи, що стосуються даного запиту.",
        "root_task_id": "strategic_1",
        "total_tasks": 6,
        "tasks": [
            {
                "id": "strategic_1",
                "title": "Email Security Analysis",
                "description": "Analyze Gmail for Google account security emails",
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
                "title": "Access Gmail via Safari",
                "description": "Open Safari and navigate to Gmail",
                "level": "tactical",
                "status": "completed",
                "progress": 1.0,
                "parent_id": "strategic_1",
                "children": ["operational_1", "operational_2"],
                "tools": ["web_browser_tool"],
                "plugins": ["web_browsing"],
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
                "plugins": ["web_browsing"],
                "created_at": time.time() - 270,
                "started_at": time.time() - 265,
                "completed_at": time.time() - 260
            },
            {
                "id": "operational_2",
                "title": "Navigate to Gmail",
                "description": "Go to Gmail website and ensure login",
                "level": "operational",
                "status": "completed",
                "progress": 1.0,
                "parent_id": "tactical_1",
                "children": [],
                "tools": ["web_browser_tool"],
                "plugins": ["web_browsing"],
                "created_at": time.time() - 260,
                "started_at": time.time() - 255,
                "completed_at": time.time() - 200
            },
            {
                "id": "tactical_2",
                "title": "Search Security Emails",
                "description": "Find Google account security emails",
                "level": "tactical",
                "status": "running",
                "progress": 0.7,
                "parent_id": "strategic_1",
                "children": ["operational_3", "operational_4"],
                "tools": ["search_tool"],
                "plugins": ["web_browsing"],
                "created_at": time.time() - 200,
                "started_at": time.time() - 190,
                "completed_at": None
            },
            {
                "id": "operational_3",
                "title": "Search for Security Emails",
                "description": "Use Gmail search to find security-related emails",
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
                "title": "Extract Email Details",
                "description": "Get subject, date, and content from security emails",
                "level": "operational",
                "status": "running",
                "progress": 0.7,
                "parent_id": "tactical_2",
                "children": [],
                "tools": ["web_browser_tool", "search_tool"],
                "plugins": ["web_browsing"],
                "created_at": time.time() - 180,
                "started_at": time.time() - 175,
                "completed_at": None
            }
        ]
    }
    
    # Update the view with test data
    task_view.update_plan(test_plan_data)
    
    print("✅ Test window opened. Check that:")
    print("  1. Email security tasks are properly displayed")
    print("  2. Browser and search tools are assigned correctly")
    print("  3. Progress shows realistic execution")
    print("  4. Task details show appropriate tools and plugins")
    
    # Run the window
    root.mainloop()

def main():
    """Main test function."""
    print("🔍 Email Security Request Analysis")
    print("=" * 60)
    
    # Test the specific request
    test_email_security_request()
    
    # Test UI display
    test_ui_display()
    
    print("\n✅ Email security request analysis completed!")

if __name__ == "__main__":
    main() 