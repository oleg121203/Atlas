#!/usr/bin/env python3
"""
Demo: Plugin System vs Simulation

This script demonstrates the difference between the old simulation
approach and the new plugin system approach.
"""

import logging
import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins import (
    get_plugin_manager,
    set_active_provider,
    execute_plugin_command,
    register_builtin_plugins
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockProvider:
    """Mock provider for demonstration."""
    
    def __init__(self, name="DemoProvider"):
        self.name = name
        self.config = {"api_key": "demo_key"}
    
    def __str__(self):
        return f"MockProvider({self.name})"

def old_simulation_approach():
    """Demonstrate the old simulation approach."""
    print("=" * 60)
    print("OLD SIMULATION APPROACH")
    print("=" * 60)
    
    print("\n1. Simulating Gmail Search")
    print("-" * 40)
    
    # Old way - hardcoded simulation
    simulated_emails = [
        {
            "id": "sim_001",
            "subject": "Security Alert - New Login Detected",
            "from": "security@google.com",
            "date": "2024-01-15 10:30",
            "snippet": "We detected a new login to your Google Account..."
        },
        {
            "id": "sim_002", 
            "subject": "Password Reset Request",
            "from": "noreply@accounts.google.com",
            "date": "2024-01-14 15:45",
            "snippet": "You requested a password reset for your account..."
        },
        {
            "id": "sim_003",
            "subject": "Two-Factor Authentication Setup",
            "from": "security@google.com", 
            "date": "2024-01-13 09:20",
            "snippet": "Please complete your two-factor authentication setup..."
        }
    ]
    
    print("Simulated Gmail search results:")
    for email in simulated_emails:
        print(f"  - {email['subject']} (from {email['from']})")
    
    print("\n2. Simulating Browser Actions")
    print("-" * 40)
    
    # Old way - fake browser actions
    print("Simulating browser actions:")
    print("  - Opening Safari... (simulated)")
    print("  - Navigating to Gmail... (simulated)")
    print("  - Searching for 'security'... (simulated)")
    print("  - Displaying results... (simulated)")
    
    print("\n3. Simulated Analysis")
    print("-" * 40)
    
    # Old way - fake analysis
    analysis = {
        "total_emails": len(simulated_emails),
        "security_emails": 3,
        "recommendations": [
            "Enable two-factor authentication",
            "Review recent login activity",
            "Update password regularly"
        ],
        "risk_level": "Medium"
    }
    
    print("Simulated analysis results:")
    print(f"  - Total emails found: {analysis['total_emails']}")
    print(f"  - Security-related emails: {analysis['security_emails']}")
    print(f"  - Risk level: {analysis['risk_level']}")
    print("  - Recommendations:")
    for rec in analysis['recommendations']:
        print(f"    * {rec}")
    
    return simulated_emails, analysis

def new_plugin_approach():
    """Demonstrate the new plugin system approach."""
    print("\n" + "=" * 60)
    print("NEW PLUGIN SYSTEM APPROACH")
    print("=" * 60)
    
    # Initialize plugin system
    mock_provider = MockProvider("DemoProvider")
    set_active_provider(mock_provider)
    register_builtin_plugins()
    
    print(f"\nInitialized with provider: {mock_provider}")
    
    print("\n1. Real Gmail Plugin Integration")
    print("-" * 40)
    
    # New way - real Gmail plugin
    try:
        # Test Gmail authentication
        auth_result = execute_plugin_command("gmail", "authenticate")
        print(f"Gmail authentication: {'Success' if auth_result.success else 'Failed'}")
        
        if auth_result.success:
            # Real Gmail search
            search_result = execute_plugin_command("gmail", "search_security_emails", days_back=30)
            if search_result.success:
                emails = search_result.data.get("emails", [])
                print(f"Real Gmail search found {len(emails)} security emails")
                for email in emails[:3]:  # Show first 3
                    print(f"  - {email['subject']} (from {email['from']})")
            else:
                print(f"Gmail search failed: {search_result.error}")
        else:
            print("Gmail not authenticated - using demo mode")
            
    except Exception as e:
        print(f"Gmail plugin error: {e}")
    
    print("\n2. Real Browser Plugin Integration")
    print("-" * 40)
    
    # New way - real browser plugin
    try:
        # Test browser operations
        browser_tests = [
            ("get_page_title", "Getting current page title"),
            ("open_browser", "Opening Safari browser"),
            ("navigate_to_url", "Navigating to Gmail", {"url": "https://gmail.com"}),
            ("get_page_title", "Getting Gmail page title")
        ]
        
        for command, description, *args in browser_tests:
            kwargs = args[0] if args else {}
            print(f"  {description}...")
            
            try:
                result = execute_plugin_command("browser", command, **kwargs)
                if result.success:
                    print(f"    ✓ Success: {result.metadata.get('message', 'Command executed')}")
                else:
                    print(f"    ✗ Failed: {result.error}")
            except Exception as e:
                print(f"    ✗ Error: {e}")
            
            time.sleep(1)  # Small delay for demo
        
        # Close browser
        close_result = execute_plugin_command("browser", "close_browser")
        if close_result.success:
            print("  ✓ Browser closed successfully")
        
    except Exception as e:
        print(f"Browser plugin error: {e}")
    
    print("\n3. Plugin System Benefits")
    print("-" * 40)
    
    # Show plugin system capabilities
    manager = get_plugin_manager()
    plugins = manager.get_available_plugins()
    
    print("Available plugins:")
    for plugin_name in plugins:
        plugin = manager.plugins[plugin_name]
        print(f"  - {plugin_name}: {plugin.metadata.description}")
        print(f"    Commands: {', '.join(plugin.get_commands())}")
    
    print("\nPlugin system advantages:")
    advantages = [
        "Real integration with actual services",
        "Modular and extensible architecture", 
        "Provider-aware execution",
        "Standardized interface",
        "Error handling and logging",
        "Configuration management",
        "Easy to add new plugins"
    ]
    
    for i, advantage in enumerate(advantages, 1):
        print(f"  {i}. {advantage}")

def compare_approaches():
    """Compare the old and new approaches."""
    print("\n" + "=" * 60)
    print("COMPARISON: OLD vs NEW APPROACH")
    print("=" * 60)
    
    comparison = {
        "old_simulation": {
            "pros": [
                "Simple to implement",
                "Fast execution",
                "No external dependencies",
                "Predictable results"
            ],
            "cons": [
                "Not real functionality",
                "Hardcoded responses",
                "No actual integration",
                "Limited extensibility",
                "Misleading to users"
            ]
        },
        "new_plugins": {
            "pros": [
                "Real functionality",
                "Actual service integration",
                "Modular architecture",
                "Extensible system",
                "Provider integration",
                "Standardized interface",
                "Error handling"
            ],
            "cons": [
                "More complex setup",
                "Requires credentials",
                "External dependencies",
                "Potential failures"
            ]
        }
    }
    
    print("\nOLD SIMULATION APPROACH:")
    print("Pros:")
    for pro in comparison["old_simulation"]["pros"]:
        print(f"  ✓ {pro}")
    print("Cons:")
    for con in comparison["old_simulation"]["cons"]:
        print(f"  ✗ {con}")
    
    print("\nNEW PLUGIN SYSTEM APPROACH:")
    print("Pros:")
    for pro in comparison["new_plugins"]["pros"]:
        print(f"  ✓ {pro}")
    print("Cons:")
    for con in comparison["new_plugins"]["cons"]:
        print(f"  ✗ {con}")
    
    print("\nRECOMMENDATION:")
    print("The new plugin system approach is superior because it provides")
    print("real functionality and actual integration with services, making")
    print("Atlas a truly useful tool rather than just a simulation.")

def main():
    """Main demonstration function."""
    try:
        print("ATLAS: PLUGIN SYSTEM vs SIMULATION DEMO")
        print("This demo shows the difference between the old simulation")
        print("approach and the new plugin system approach.")
        
        # Run old simulation approach
        old_simulation_approach()
        
        # Run new plugin approach
        new_plugin_approach()
        
        # Compare approaches
        compare_approaches()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 