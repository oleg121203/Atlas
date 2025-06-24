#!/usr/bin/env python3
"""
Test script for enhanced email system with proper goal achievement checking.
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.hierarchical_plan_manager import HierarchicalPlanManager
from agents.adaptive_execution_manager import AdaptiveExecutionManager
from agents.tool_registry import ToolRegistry
from agents.email_strategy_manager import EmailStrategyManager

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'test_enhanced_email_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )

def test_enhanced_email_system():
    """Test the enhanced email system with proper goal achievement checking."""
    logger = logging.getLogger(__name__)
    
    # Test goal
    goal = "Зайди в мою почту через браузер сафарі, вона мала би бути вже залогінена. Найди всі листи що стосуються безпеки гугл екаунта на одній сторінці джмайл іі виведи мені в чаті по часовому пріоритету з коротким описом всі листи, що стосуються даного запиту."
    
    logger.info("=" * 80)
    logger.info("TESTING ENHANCED EMAIL SYSTEM WITH PROPER GOAL ACHIEVEMENT")
    logger.info("=" * 80)
    logger.info(f"Goal: {goal}")
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        
        # Create mock components for testing
        class MockLLMManager:
            def get_response(self, prompt):
                return "Mock response"
        
        class MockPlanner:
            def create_plan(self, goal):
                return {"goal": goal, "steps": []}
        
        # Initialize managers
        tool_registry = ToolRegistry()
        email_strategy_manager = EmailStrategyManager()
        adaptive_execution_manager = AdaptiveExecutionManager(max_attempts=3)
        
        hierarchical_plan_manager = HierarchicalPlanManager(
            llm_manager=MockLLMManager(),
            strategic_planner=MockPlanner(),
            tactical_planner=MockPlanner(),
            operational_planner=MockPlanner()
        )
        
        logger.info("Components initialized successfully")
        
        # Create plan first
        logger.info("Creating hierarchical plan...")
        plan = hierarchical_plan_manager.create_hierarchical_plan(goal)
        
        if not plan:
            logger.error("Failed to create plan")
            return {"success": False, "error": "Failed to create plan"}
        
        # Execute the plan
        logger.info("Executing hierarchical plan...")
        
        result = hierarchical_plan_manager.execute_plan(plan)
        
        # Analyze the result
        logger.info("=" * 50)
        logger.info("EXECUTION RESULT ANALYSIS")
        logger.info("=" * 50)
        
        if result.get("success"):
            logger.info("✅ Plan execution completed successfully")
            
            # Check if we actually achieved the user's goal
            data = result.get("data", {})
            emails = data.get("emails", [])
            emails_found = data.get("emails_found", 0)
            
            logger.info(f"📧 Emails found: {emails_found}")
            
            if emails_found > 0:
                logger.info("✅ REAL SUCCESS: User received email results")
                logger.info("📋 Email list:")
                
                for i, email in enumerate(emails, 1):
                    logger.info(f"  {i}. [{email.get('priority', 'unknown')}] {email.get('sender', 'Unknown')}")
                    logger.info(f"     Subject: {email.get('subject', 'No subject')}")
                    logger.info(f"     Date: {email.get('date', 'Unknown date')}")
                    logger.info(f"     Snippet: {email.get('snippet', 'No snippet')[:100]}...")
                    logger.info("")
            else:
                logger.warning("⚠️  FALSE SUCCESS: No emails found despite successful execution")
                
        else:
            logger.error("❌ Plan execution failed")
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
        
        # Check adaptation history
        adaptation_history = result.get("adaptation_history", [])
        logger.info(f"🔄 Adaptation attempts: {len(adaptation_history)}")
        
        for i, adaptation in enumerate(adaptation_history):
            logger.info(f"  Attempt {i+1}: {adaptation.get('status', 'unknown')}")
            if adaptation.get('error'):
                logger.info(f"    Error: {adaptation['error']}")
        
        logger.info("=" * 80)
        logger.info("TEST COMPLETED")
        logger.info("=" * 80)
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    setup_logging()
    test_enhanced_email_system() 