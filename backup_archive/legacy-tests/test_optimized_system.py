#!/usr/bin/env python3
"""
Test script for optimized system with delays and token limits
"""

import customtkinter as ctk
import time
from modules.agents.hierarchical_plan_manager import HierarchicalPlanManager
from utils.llm_manager import LLMManager
from utils.config_manager import ConfigManager
from modules.agents.token_tracker import TokenTracker
from tools.delay_tool import DelayTool

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

def test_optimized_complexity_assessment():
    """Test the optimized complexity assessment with token limits."""
    print("⚡ Testing Optimized System with Token Limits")
    print("=" * 60)
    
    # Create hierarchical plan manager
    llm_manager = create_mock_llm_manager()
    strategic_planner, tactical_planner, operational_planner = create_mock_planners()
    
    plan_manager = HierarchicalPlanManager(
        llm_manager=llm_manager,
        strategic_planner=strategic_planner,
        tactical_planner=tactical_planner,
        operational_planner=operational_planner
    )
    
    # Test different types of goals with token optimization
    test_goals = [
        # Simple goals (should use minimal tokens)
        "Take a screenshot",
        "Click login button",
        "Copy text",
        
        # Medium goals (should use moderate tokens)
        "Зайди в Gmail через Safari, знайди security emails",
        "Search for important emails",
        "Open browser and navigate",
        
        # Complex goals (should use more tokens but still limited)
        "Analyze all security emails from last year, create detailed report",
        "Comprehensive system analysis with multiple operations",
        "Build complete automation workflow"
    ]
    
    for i, goal in enumerate(test_goals, 1):
        print(f"\n🎯 Test {i}: {goal[:60]}{'...' if len(goal) > 60 else ''}")
        print("-" * 80)
        
        try:
            # Test complexity assessment with token optimization
            print("📊 Analyzing complexity (optimized)...")
            complexity = plan_manager._analyze_goal_complexity(goal)
            
            print(f"   Level: {complexity['level']}")
            print(f"   Phases: {complexity['phases']}")
            print(f"   Tasks per phase: {complexity['tasks_per_phase']}")
            print(f"   Actions per task: {complexity['actions_per_task']}")
            print(f"   Total processes: {complexity['total_processes']}")
            print(f"   Method: {complexity['assessment_method']}")
            print(f"   Reasoning: {complexity['reasoning'][:50]}...")
            
            # Test plan creation with delays
            print("📋 Creating hierarchical plan with delays...")
            context = {"prompt": "Test execution", "options": {"cyclic": False}}
            plan = plan_manager.create_hierarchical_plan(goal, context)
            
            if not plan:
                print("   ❌ Failed to create plan")
                continue
                
            # Analyze plan structure with delays
            all_tasks = plan_manager.get_all_tasks()
            operational_tasks = [t for t in all_tasks if t.level.value == "operational"]
            delay_tasks = [t for t in operational_tasks if "delay" in t.tools]
            
            print(f"   📊 Plan created: {len(all_tasks)} total tasks, {len(operational_tasks)} operational")
            print(f"   ⏱️ Delay tasks: {len(delay_tasks)}")
            
            # Check tool assignment quality with delays
            print("   🛠️ Tool assignment analysis:")
            browser_tasks = 0
            search_tasks = 0
            delay_tasks_count = 0
            generic_tasks = 0
            
            for task in operational_tasks:
                tools = task.tools
                if "web_browser_tool" in tools:
                    browser_tasks += 1
                elif "search_tool" in tools:
                    search_tasks += 1
                elif "delay_tool" in tools:
                    delay_tasks_count += 1
                elif "generic_executor" in tools:
                    generic_tasks += 1
                    
                # Check for obvious mismatches
                if "browser" in task.title.lower() and "web_browser_tool" not in tools:
                    print(f"     ⚠️ Browser task missing web_browser_tool: {task.title}")
                if "search" in task.title.lower() and "search_tool" not in tools:
                    print(f"     ⚠️ Search task missing search_tool: {task.title}")
            
            print(f"     Browser tasks: {browser_tasks}")
            print(f"     Search tasks: {search_tasks}")
            print(f"     Delay tasks: {delay_tasks_count}")
            print(f"     Generic tasks: {generic_tasks}")
            
            # Overall assessment
            total_processes = complexity['total_processes']
            if total_processes <= 5 and len(all_tasks) <= 8:
                print("   ✅ Simple goal handled appropriately with delays")
            elif 6 <= total_processes <= 15 and 8 <= len(all_tasks) <= 20:
                print("   ✅ Medium goal handled appropriately with delays")
            elif total_processes >= 16 and len(all_tasks) >= 20:
                print("   ✅ Complex goal handled appropriately with delays")
            else:
                print("   ⚠️ Goal complexity doesn't match plan size")
                
        except Exception as e:
            print(f"   ❌ Error testing goal: {e}")
            import traceback
            traceback.print_exc()

def test_delay_tool():
    """Test the delay tool functionality."""
    print("\n⏱️ Testing Delay Tool...")
    print("-" * 60)
    
    delay_tool = DelayTool()
    
    # Test basic wait
    print("Testing basic wait (1 second)...")
    start_time = time.time()
    result = delay_tool.wait(1.0)
    end_time = time.time()
    actual_duration = end_time - start_time
    
    print(f"   Expected: 1.0s, Actual: {actual_duration:.2f}s")
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    
    # Test smart wait
    print("\nTesting smart wait for browser operation...")
    start_time = time.time()
    result = delay_tool.smart_wait("browser")
    end_time = time.time()
    actual_duration = end_time - start_time
    
    print(f"   Expected: 2.0s, Actual: {actual_duration:.2f}s")
    print(f"   Status: {result['status']}")
    
    # Test progressive wait
    print("\nTesting progressive wait...")
    for step in range(1, 4):
        start_time = time.time()
        result = delay_tool.progressive_wait(step)
        end_time = time.time()
        actual_duration = end_time - start_time
        
        expected = min(1.0 + (step - 1) * 0.5, 3.0)
        print(f"   Step {step}: Expected {expected}s, Actual {actual_duration:.2f}s")

def test_ui_display_with_delays():
    """Test UI display with optimized system and delays."""
    print("\n🖥️ Testing UI Display with Optimized System...")
    
    # Create test window
    root = ctk.CTk()
    root.title("Optimized System Test")
    root.geometry("1200x800")
    
    # Create hierarchical task view
    from ui.hierarchical_task_view import HierarchicalTaskView
    
    task_view = HierarchicalTaskView(root)
    task_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create test plan data showing optimized complexity with delays
    test_plan_data = {
        "goal": "Зайди в Gmail через Safari, знайди security emails",
        "root_task_id": "strategic_1",
        "total_tasks": 12,  # Includes delay tasks
        "optimization_info": {
            "token_limit": 1000,
            "delays_added": True,
            "complexity_assessment": "optimized"
        },
        "tasks": [
            {
                "id": "strategic_1",
                "title": "Email Security Analysis",
                "description": "Analyze Gmail for security emails",
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
                "children": ["operational_1", "operational_2", "delay_1"],
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
                "id": "delay_1",
                "title": "Wait for Browser",
                "description": "Wait for browser to fully load",
                "level": "operational",
                "status": "completed",
                "progress": 1.0,
                "parent_id": "tactical_1",
                "children": [],
                "tools": ["delay_tool"],
                "plugins": [],
                "created_at": time.time() - 260,
                "started_at": time.time() - 259,
                "completed_at": time.time() - 257
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
                "created_at": time.time() - 257,
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
                "children": ["operational_3", "operational_4", "delay_2"],
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
                "id": "delay_2",
                "title": "Wait for Search Results",
                "description": "Wait for search results to load",
                "level": "operational",
                "status": "running",
                "progress": 0.8,
                "parent_id": "tactical_2",
                "children": [],
                "tools": ["delay_tool"],
                "plugins": [],
                "created_at": time.time() - 180,
                "started_at": time.time() - 179,
                "completed_at": None
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
                "created_at": time.time() - 179,
                "started_at": time.time() - 175,
                "completed_at": None
            }
        ]
    }
    
    # Update the view with test data
    task_view.update_plan(test_plan_data)
    
    print("✅ Test window opened. Check that:")
    print("  1. Plan shows optimized complexity (12 tasks including delays)")
    print("  2. Delay tasks are properly displayed")
    print("  3. Tools are correctly assigned (web_browser_tool, search_tool, delay_tool)")
    print("  4. UI remains responsive with optimized token usage")
    
    # Run the window
    root.mainloop()

def main():
    """Main test function."""
    print("⚡ Optimized System Test with Token Limits and Delays")
    print("=" * 60)
    
    # Test optimized complexity assessment
    test_optimized_complexity_assessment()
    
    # Test delay tool
    test_delay_tool()
    
    # Test UI display
    test_ui_display_with_delays()
    
    print("\n✅ Optimized system test completed!")

if __name__ == "__main__":
    main() 