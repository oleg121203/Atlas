#!/usr/bin/env python3
"""
Test script for intuitive adaptive system
"""

import time

import customtkinter as ctk
from modules.agents.hierarchical_plan_manager import HierarchicalPlanManager
from modules.agents.token_tracker import TokenTracker

from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


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


def test_intuitive_complexity_assessment():
    """Test the new intuitive complexity assessment system."""
    print("🧠 Testing Intuitive Adaptive System")
    print("=" * 60)

    # Create hierarchical plan manager
    llm_manager = create_mock_llm_manager()
    strategic_planner, tactical_planner, operational_planner = create_mock_planners()

    plan_manager = HierarchicalPlanManager(
        llm_manager=llm_manager,
        strategic_planner=strategic_planner,
        tactical_planner=tactical_planner,
        operational_planner=operational_planner,
    )

    # Test different types of goals
    test_goals = [
        # Simple goals (should create 1-5 processes)
        "Take a screenshot",
        "Click on the login button",
        "Copy text to clipboard",
        # Medium goals (should create 6-15 processes)
        "Зайди в мою почту через браузер сафарі, вона мала би бути вже залогінена. Найди всі листи що стосуються безпеки гугл екаунта на одній сторінці джмайл іі виведи мені в чаті по часовому пріоритету з коротким описом всі листи, що стосуються даного запиту.",
        "Search for important emails in Gmail",
        "Open Safari and navigate to a website",
        # Complex goals (should create 16-30 processes)
        "Analyze all security emails from the last year, create a detailed report with recommendations, and send it to the team",
        "Comprehensive system analysis with multiple browser operations and data processing",
        "Build a complete automation workflow for email management and reporting",
    ]

    for i, goal in enumerate(test_goals, 1):
        print(f"\n🎯 Test {i}: {goal[:80]}{'...' if len(goal) > 80 else ''}")
        print("-" * 80)

        try:
            # Test complexity assessment
            print("📊 Analyzing complexity...")
            complexity = plan_manager._analyze_goal_complexity(goal)

            print(f"   Level: {complexity['level']}")
            print(f"   Phases: {complexity['phases']}")
            print(f"   Tasks per phase: {complexity['tasks_per_phase']}")
            print(f"   Actions per task: {complexity['actions_per_task']}")
            print(f"   Total processes: {complexity['total_processes']}")
            print(f"   Method: {complexity['assessment_method']}")
            print(f"   Reasoning: {complexity['reasoning']}")

            # Validate complexity assessment
            total_processes = complexity["total_processes"]
            level = complexity["level"]

            if level == "simple" and total_processes > 5:
                print(
                    f"   ⚠️ WARNING: Simple goal created {total_processes} processes (should be 1-5)"
                )
            elif level == "medium" and (total_processes < 6 or total_processes > 15):
                print(
                    f"   ⚠️ WARNING: Medium goal created {total_processes} processes (should be 6-15)"
                )
            elif level == "complex" and total_processes < 16:
                print(
                    f"   ⚠️ WARNING: Complex goal created {total_processes} processes (should be 16-30)"
                )
            else:
                print("   ✅ Complexity assessment looks appropriate")

            # Test plan creation
            print("📋 Creating hierarchical plan...")
            context = {"prompt": "Test execution", "options": {"cyclic": False}}
            plan = plan_manager.create_hierarchical_plan(goal, context)

            if not plan:
                print("   ❌ Failed to create plan")
                continue

            # Analyze plan structure
            all_tasks = plan_manager.get_all_tasks()
            operational_tasks = [t for t in all_tasks if t.level.value == "operational"]

            print(
                f"   📊 Plan created: {len(all_tasks)} total tasks, {len(operational_tasks)} operational"
            )

            # Check tool assignment quality
            print("   🛠️ Tool assignment analysis:")
            browser_tasks = 0
            search_tasks = 0
            generic_tasks = 0

            for task in operational_tasks:
                tools = task.tools
                if "web_browser_tool" in tools:
                    browser_tasks += 1
                elif "search_tool" in tools:
                    search_tasks += 1
                elif "generic_executor" in tools:
                    generic_tasks += 1

                # Check for obvious mismatches
                if "browser" in task.title.lower() and "web_browser_tool" not in tools:
                    print(f"     ⚠️ Browser task missing web_browser_tool: {task.title}")
                if "search" in task.title.lower() and "search_tool" not in tools:
                    print(f"     ⚠️ Search task missing search_tool: {task.title}")

            print(f"     Browser tasks: {browser_tasks}")
            print(f"     Search tasks: {search_tasks}")
            print(f"     Generic tasks: {generic_tasks}")

            # Overall assessment
            if total_processes <= 5 and len(all_tasks) <= 5:
                print("   ✅ Simple goal handled appropriately")
            elif 6 <= total_processes <= 15 and 6 <= len(all_tasks) <= 15:
                print("   ✅ Medium goal handled appropriately")
            elif total_processes >= 16 and len(all_tasks) >= 16:
                print("   ✅ Complex goal handled appropriately")
            else:
                print("   ⚠️ Goal complexity doesn't match plan size")

        except Exception as e:
            print(f"   ❌ Error testing goal: {e}")
            import traceback

            traceback.print_exc()


def test_ui_display():
    """Test UI display with intuitive adaptive system."""
    print("\n🖥️ Testing UI Display with Adaptive System...")

    # Create test window
    root = ctk.CTk()
    root.title("Intuitive Adaptive System Test")
    root.geometry("1200x800")

    # Create hierarchical task view
    from ui.hierarchical_task_view import HierarchicalTaskView

    task_view = HierarchicalTaskView(root)
    task_view.pack(fill="both", expand=True, padx=10, pady=10)

    # Create test plan data showing adaptive complexity
    test_plan_data = {
        "goal": "Зайди в мою почту через браузер сафарі, вона мала би бути вже залогінена. Найди всі листи що стосуються безпеки гугл екаунта на одній сторінці джмайл іі виведи мені в чаті по часовому пріоритету з коротким описом всі листи, що стосуються даного запиту.",
        "root_task_id": "strategic_1",
        "total_tasks": 8,  # Reduced from 33 to 8 (adaptive)
        "complexity_assessment": {
            "level": "medium",
            "phases": 2,
            "tasks_per_phase": 2,
            "actions_per_task": 2,
            "total_processes": 8,
            "reasoning": "LLM-based assessment: Email security analysis requires browser access and search operations",
            "assessment_method": "llm_intuitive",
        },
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
                "completed_at": time.time() - 50,
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
                "completed_at": time.time() - 200,
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
                "completed_at": time.time() - 260,
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
                "completed_at": time.time() - 200,
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
                "completed_at": None,
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
                "completed_at": time.time() - 180,
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
                "completed_at": None,
            },
        ],
    }

    # Update the view with test data
    task_view.update_plan(test_plan_data)

    print("✅ Test window opened. Check that:")
    print("  1. Plan shows adaptive complexity (8 tasks instead of 33)")
    print("  2. Tools are properly assigned (web_browser_tool, search_tool)")
    print("  3. Complexity assessment is shown in task details")
    print("  4. UI remains responsive with fewer tasks")

    # Run the window
    root.mainloop()


def main():
    """Main test function."""
    print("🧠 Intuitive Adaptive System Test")
    print("=" * 60)

    # Test intuitive complexity assessment
    test_intuitive_complexity_assessment()

    # Test UI display
    test_ui_display()

    print("\n✅ Intuitive adaptive system test completed!")


if __name__ == "__main__":
    main()
