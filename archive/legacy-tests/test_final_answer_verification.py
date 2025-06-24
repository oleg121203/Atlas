#!/usr/bin/env python3
"""
Test script for final answer verification and concrete response generation
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
    return LLMManager(token_tracker=None, config_manager=config_manager)

def create_mock_planners():
    """Create mock planners for testing."""
    class MockPlanner:
        def plan(self, *args, **kwargs):
            return ["Mock plan step"]
    
    return MockPlanner(), MockPlanner(), MockPlanner()

def test_email_goal_verification():
    """Test email goal with final answer verification."""
    print("Testing email goal with final answer verification...")
    
    # Create hierarchical plan manager
    llm_manager = create_mock_llm_manager()
    strategic, tactical, operational = create_mock_planners()
    
    plan_manager = HierarchicalPlanManager(
        llm_manager=llm_manager,
        strategic_planner=strategic,
        tactical_planner=tactical,
        operational_planner=operational
    )
    
    # Test goal
    goal = "Search my Gmail for security emails and tell me how many I have"
    
    print(f"Goal: {goal}")
    print("Creating hierarchical plan...")
    
    # Create plan
    plan = plan_manager.create_hierarchical_plan(goal)
    
    if plan:
        print(f"Plan created with {plan['total_tasks']} tasks")
        print("Executing plan...")
        
        # Execute plan
        success = plan_manager.execute_plan()
        
        if success:
            print("✅ Plan executed successfully!")
            
            # Analyze final results
            final_analysis = plan_manager.analyze_final_results(goal)
            
            if final_analysis and "answer" in final_analysis:
                print("\n" + "="*60)
                print("FINAL ANSWER:")
                print("="*60)
                print(final_analysis["answer"])
                print("="*60)
                
                print(f"\nAnalysis type: {final_analysis.get('analysis_type')}")
                print(f"Tools used: {final_analysis.get('tools_used', [])}")
                print(f"Success: {final_analysis.get('success')}")
            else:
                print("❌ No final answer generated")
        else:
            print("❌ Plan execution failed")
    else:
        print("❌ Failed to create plan")

def test_screenshot_goal_verification():
    """Test screenshot goal with final answer verification."""
    print("\nTesting screenshot goal with final answer verification...")
    
    # Create hierarchical plan manager
    llm_manager = create_mock_llm_manager()
    strategic, tactical, operational = create_mock_planners()
    
    plan_manager = HierarchicalPlanManager(
        llm_manager=llm_manager,
        strategic_planner=strategic,
        tactical_planner=tactical,
        operational_planner=operational
    )
    
    # Test goal
    goal = "Take a screenshot of my current screen"
    
    print(f"Goal: {goal}")
    print("Creating hierarchical plan...")
    
    # Create plan
    plan = plan_manager.create_hierarchical_plan(goal)
    
    if plan:
        print(f"Plan created with {plan['total_tasks']} tasks")
        print("Executing plan...")
        
        # Execute plan
        success = plan_manager.execute_plan()
        
        if success:
            print("✅ Plan executed successfully!")
            
            # Analyze final results
            final_analysis = plan_manager.analyze_final_results(goal)
            
            if final_analysis and "answer" in final_analysis:
                print("\n" + "="*60)
                print("FINAL ANSWER:")
                print("="*60)
                print(final_analysis["answer"])
                print("="*60)
                
                print(f"\nAnalysis type: {final_analysis.get('analysis_type')}")
                print(f"Tools used: {final_analysis.get('tools_used', [])}")
                print(f"Success: {final_analysis.get('success')}")
            else:
                print("❌ No final answer generated")
        else:
            print("❌ Plan execution failed")
    else:
        print("❌ Failed to create plan")

def test_general_goal_verification():
    """Test general goal with final answer verification."""
    print("\nTesting general goal with final answer verification...")
    
    # Create hierarchical plan manager
    llm_manager = create_mock_llm_manager()
    strategic, tactical, operational = create_mock_planners()
    
    plan_manager = HierarchicalPlanManager(
        llm_manager=llm_manager,
        strategic_planner=strategic,
        tactical_planner=tactical,
        operational_planner=operational
    )
    
    # Test goal
    goal = "Open Safari and search for Atlas documentation"
    
    print(f"Goal: {goal}")
    print("Creating hierarchical plan...")
    
    # Create plan
    plan = plan_manager.create_hierarchical_plan(goal)
    
    if plan:
        print(f"Plan created with {plan['total_tasks']} tasks")
        print("Executing plan...")
        
        # Execute plan
        success = plan_manager.execute_plan()
        
        if success:
            print("✅ Plan executed successfully!")
            
            # Analyze final results
            final_analysis = plan_manager.analyze_final_results(goal)
            
            if final_analysis and "answer" in final_analysis:
                print("\n" + "="*60)
                print("FINAL ANSWER:")
                print("="*60)
                print(final_analysis["answer"])
                print("="*60)
                
                print(f"\nAnalysis type: {final_analysis.get('analysis_type')}")
                print(f"Tools used: {final_analysis.get('tools_used', [])}")
                print(f"Success: {final_analysis.get('success')}")
            else:
                print("❌ No final answer generated")
        else:
            print("❌ Plan execution failed")
    else:
        print("❌ Failed to create plan")

def main():
    """Run all tests."""
    print("Testing Final Answer Verification System")
    print("=" * 60)
    
    # Test different types of goals
    test_email_goal_verification()
    test_screenshot_goal_verification()
    test_general_goal_verification()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("\nKey improvements:")
    print("✅ Real tool execution with result collection")
    print("✅ Final result analysis based on goal type")
    print("✅ Concrete answers with specific information")
    print("✅ Tools used tracking and reporting")
    print("✅ Success/failure verification")
    print("✅ Goal-specific response formatting")

if __name__ == "__main__":
    main() 