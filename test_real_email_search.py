#!/usr/bin/env python3
"""
Real Email Search Test for Atlas

This script demonstrates the real Gmail integration functionality.
It shows how Atlas can now perform actual email searches instead of simulations.
"""

import json
import time
import sys
import os

# Add Atlas to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_real_email_search():
    """Test real email search functionality."""
    print("🔍 Testing Real Email Search Functionality")
    print("=" * 60)
    
    try:
        # Test Gmail tool
        print("\n1. Testing Gmail API Tool...")
        from tools.gmail_tool import get_gmail_tool
        
        gmail_tool = get_gmail_tool()
        
        # Test authentication
        print("   🔐 Testing authentication...")
        auth_result = gmail_tool.authenticate()
        
        if auth_result["success"]:
            print(f"   ✅ {auth_result['message']}")
            
            # Test security email search
            print("\n2. Testing security email search...")
            search_result = gmail_tool.search_security_emails(days_back=30)
            
            if search_result["success"]:
                email_count = search_result["count"]
                print(f"   ✅ Found {email_count} security emails")
                
                # Show email details
                if search_result["results"]:
                    print("\n   📧 Recent Security Emails:")
                    for i, email in enumerate(search_result["results"][:5], 1):
                        print(f"   {i}. {email['subject']}")
                        print(f"      📅 {email['date']} | 📧 {email['from']}")
                        print(f"      📝 {email['snippet'][:80]}...")
                        print()
                
                return True
            else:
                print(f"   ❌ Search failed: {search_result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Authentication failed: {auth_result.get('error', 'Unknown error')}")
            print("   💡 Make sure you have set up Gmail API credentials")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Run: ./scripts/setup_gmail_integration.sh")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_real_browser_integration():
    """Test real browser integration."""
    print("\n3. Testing Real Browser Integration...")
    
    try:
        from tools.real_browser_tool import get_real_browser_tool
        
        browser_tool = get_real_browser_tool()
        
        # Test Safari opening
        print("   🌐 Testing Safari browser...")
        safari_result = browser_tool.open_safari()
        
        if safari_result["success"]:
            print(f"   ✅ {safari_result['message']}")
            
            # Test Gmail navigation
            print("   📧 Testing Gmail navigation...")
            gmail_result = browser_tool.open_gmail()
            
            if gmail_result["success"]:
                print(f"   ✅ {gmail_result['message']}")
                
                # Wait a bit and get page title
                time.sleep(3)
                title_result = browser_tool.get_page_title()
                
                if title_result["success"]:
                    print(f"   📄 Page title: {title_result['title']}")
                
                return True
            else:
                print(f"   ❌ Gmail navigation failed: {gmail_result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Safari failed: {safari_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Browser error: {e}")
        return False

def test_hierarchical_planning_with_real_tools():
    """Test hierarchical planning with real tools."""
    print("\n4. Testing Hierarchical Planning with Real Tools...")
    
    try:
        from agents.hierarchical_plan_manager import HierarchicalPlanManager
        from utils.llm_manager import LLMManager
        
        # Create mock planners (for testing)
        class MockPlanner:
            def create_plan(self, goal, context=None):
                return ["Access and navigate", "Search and analyze"]
        
        # Create plan manager
        llm_manager = LLMManager()
        plan_manager = HierarchicalPlanManager(
            llm_manager=llm_manager,
            strategic_planner=MockPlanner(),
            tactical_planner=MockPlanner(),
            operational_planner=MockPlanner()
        )
        
        # Test goal
        goal = "Search my Gmail for security emails and show me the results"
        
        print(f"   🎯 Goal: {goal}")
        
        # Create plan
        plan = plan_manager.create_hierarchical_plan(goal)
        
        if plan:
            print(f"   ✅ Plan created with {plan['total_tasks']} tasks")
            
            # Show plan structure
            print("   📋 Plan Structure:")
            for task in plan['tasks']:
                level_icon = "🎯" if task['level'] == 'strategic' else "📝" if task['level'] == 'tactical' else "⚙️"
                print(f"   {level_icon} {task['title']} ({task['level']})")
                if task['tools']:
                    print(f"      🛠️ Tools: {', '.join(task['tools'])}")
            
            return True
        else:
            print("   ❌ Failed to create plan")
            return False
            
    except Exception as e:
        print(f"   ❌ Planning error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Atlas Real Email Search Integration Test")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Gmail API
    if test_real_email_search():
        success_count += 1
    
    # Test 2: Browser integration
    if test_real_browser_integration():
        success_count += 1
    
    # Test 3: Hierarchical planning
    if test_hierarchical_planning_with_real_tools():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"✅ Passed: {success_count}/{total_tests}")
    print(f"❌ Failed: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 All tests passed! Atlas is ready for real email search.")
        print("\n📋 What this means:")
        print("   • Atlas can now perform real Gmail API searches")
        print("   • Browser automation works with actual Safari")
        print("   • Hierarchical planning uses real tools")
        print("   • No more simulations - real data and actions!")
    else:
        print("\n⚠️ Some tests failed. Check the setup:")
        print("   • Run: ./scripts/setup_gmail_integration.sh")
        print("   • Follow: docs/GMAIL_API_SETUP.md")
        print("   • Ensure Gmail API credentials are configured")
    
    print("\n🔧 Next Steps:")
    print("   1. Configure Gmail API credentials")
    print("   2. Run Atlas and try: 'Search my Gmail for security emails'")
    print("   3. Watch real browser automation and email analysis!")

if __name__ == "__main__":
    main() 