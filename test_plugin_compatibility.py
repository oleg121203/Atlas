#!/usr/bin/env python3
"""
Plugin Compatibility Test

This script tests the compatibility between plugins and tools,
identifying duplications and conflicts.
"""

import json
import logging
import sys
import os
from typing import Dict, List, Set

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
    """Mock provider for testing."""
    
    def __init__(self, name="TestProvider"):
        self.name = name
        self.config = {"api_key": "test_key"}
    
    def __str__(self):
        return f"MockProvider({self.name})"

def analyze_duplications():
    """Analyze duplications between plugins and tools."""
    print("=" * 60)
    print("PLUGIN AND TOOL DUPLICATION ANALYSIS")
    print("=" * 60)
    
    # Define known duplications
    duplications = {
        "browser_automation": {
            "components": [
                "plugins/browser_plugin.py",
                "plugins/web_browsing/plugin.py", 
                "tools/real_browser_tool.py",
                "tools/web_browser_tool.py"
            ],
            "functionality": [
                "open_browser",
                "navigate_to_url", 
                "get_page_title",
                "close_browser",
                "execute_javascript",
                "gmail_integration"
            ],
            "severity": "HIGH"
        },
        "gmail_integration": {
            "components": [
                "plugins/gmail_plugin.py",
                "tools/gmail_tool.py"
            ],
            "functionality": [
                "search_emails",
                "get_email_content",
                "authenticate",
                "search_security_emails"
            ],
            "severity": "MEDIUM"
        }
    }
    
    print("\nDetected Duplications:")
    print("-" * 40)
    
    for category, info in duplications.items():
        print(f"\n{category.upper()} ({info['severity']} severity):")
        print(f"  Components: {len(info['components'])}")
        for component in info['components']:
            print(f"    - {component}")
        print(f"  Functionality: {len(info['functionality'])}")
        for func in info['functionality']:
            print(f"    - {func}")
    
    return duplications

def test_plugin_system():
    """Test the plugin system functionality."""
    print("\n" + "=" * 60)
    print("PLUGIN SYSTEM FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Initialize plugin system
    mock_provider = MockProvider("TestProvider")
    set_active_provider(mock_provider)
    register_builtin_plugins()
    
    manager = get_plugin_manager()
    plugins = manager.get_available_plugins()
    
    print(f"Available plugins: {plugins}")
    
    # Test each plugin
    for plugin_name in plugins:
        print(f"\nTesting plugin: {plugin_name}")
        print("-" * 30)
        
        plugin = manager.plugins[plugin_name]
        
        # Test initialization
        try:
            init_result = manager.initialize_plugin(plugin_name)
            print(f"  Initialization: {'✓' if init_result else '✗'}")
        except Exception as e:
            print(f"  Initialization: ✗ Error: {e}")
        
        # Test help
        try:
            help_text = plugin.get_help()
            print(f"  Help: ✓ ({len(help_text)} chars)")
        except Exception as e:
            print(f"  Help: ✗ Error: {e}")
        
        # Test commands
        try:
            commands = plugin.get_commands()
            print(f"  Commands: ✓ {len(commands)} commands")
            for cmd in commands[:3]:  # Show first 3
                print(f"    - {cmd}")
        except Exception as e:
            print(f"  Commands: ✗ Error: {e}")

def test_tool_compatibility():
    """Test compatibility with existing tools."""
    print("\n" + "=" * 60)
    print("TOOL COMPATIBILITY TEST")
    print("=" * 60)
    
    # Test if tools can be imported
    tools_to_test = [
        "tools.plugin_tool",
        "tools.real_browser_tool", 
        "tools.gmail_tool",
        "tools.web_browser_tool"
    ]
    
    for tool_name in tools_to_test:
        print(f"\nTesting tool: {tool_name}")
        print("-" * 30)
        
        try:
            module = __import__(tool_name, fromlist=[''])
            print("  Import: ✓ Success")
            
            # Check for main functions
            if hasattr(module, 'register_plugin_tools'):
                print("  Plugin tools: ✓ Available")
            else:
                print("  Plugin tools: ✗ Not available")
                
        except ImportError as e:
            print(f"  Import: ✗ Failed: {e}")
        except Exception as e:
            print(f"  Import: ✗ Error: {e}")

def test_command_conflicts():
    """Test for command name conflicts."""
    print("\n" + "=" * 60)
    print("COMMAND CONFLICT ANALYSIS")
    print("=" * 60)
    
    # Get all commands from plugins
    manager = get_plugin_manager()
    all_commands = {}
    
    for plugin_name, plugin in manager.plugins.items():
        try:
            commands = plugin.get_commands()
            for cmd in commands:
                if cmd not in all_commands:
                    all_commands[cmd] = []
                all_commands[cmd].append(plugin_name)
        except Exception as e:
            print(f"Error getting commands from {plugin_name}: {e}")
    
    # Find conflicts
    conflicts = {cmd: plugins for cmd, plugins in all_commands.items() if len(plugins) > 1}
    
    if conflicts:
        print("Command conflicts found:")
        for cmd, plugins in conflicts.items():
            print(f"  '{cmd}' used by: {', '.join(plugins)}")
    else:
        print("No command conflicts found ✓")
    
    return conflicts

def generate_recommendations():
    """Generate recommendations for resolving duplications."""
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    recommendations = [
        {
            "priority": "HIGH",
            "action": "Create unified browser plugin",
            "description": "Combine browser_plugin.py, web_browsing/plugin.py, real_browser_tool.py, and web_browser_tool.py into a single unified plugin",
            "benefits": [
                "Eliminate 4 duplicate components",
                "Single point of entry for browser functionality",
                "Better maintainability",
                "Reduced complexity"
            ],
            "steps": [
                "Create plugins/unified_browser_plugin.py",
                "Integrate functionality from all browser components",
                "Update tools/plugin_tool.py to use unified plugin",
                "Remove duplicate files",
                "Update documentation"
            ]
        },
        {
            "priority": "MEDIUM", 
            "action": "Consolidate Gmail integration",
            "description": "Use gmail_plugin.py as primary, keep gmail_tool.py for backward compatibility",
            "benefits": [
                "Eliminate 2 duplicate components",
                "Provider-aware execution",
                "Better error handling",
                "Standardized interface"
            ],
            "steps": [
                "Update tools/plugin_tool.py to use Gmail plugin",
                "Add fallback to gmail_tool.py",
                "Test backward compatibility",
                "Update documentation"
            ]
        },
        {
            "priority": "LOW",
            "action": "Update documentation",
            "description": "Update all documentation to reflect the new unified architecture",
            "benefits": [
                "Clear user guidance",
                "Reduced confusion",
                "Better developer experience"
            ],
            "steps": [
                "Update docs/PLUGIN_SYSTEM.md",
                "Create migration guide",
                "Update README files",
                "Create examples"
            ]
        }
    ]
    
    for rec in recommendations:
        print(f"\n{rec['priority']} PRIORITY: {rec['action']}")
        print(f"Description: {rec['description']}")
        print("Benefits:")
        for benefit in rec['benefits']:
            print(f"  ✓ {benefit}")
        print("Steps:")
        for step in rec['steps']:
            print(f"  - {step}")

def main():
    """Main compatibility test function."""
    try:
        print("ATLAS PLUGIN COMPATIBILITY TEST")
        print("This test analyzes compatibility and duplications between plugins and tools.")
        
        # Run analysis
        duplications = analyze_duplications()
        
        # Test functionality
        test_plugin_system()
        
        # Test tool compatibility
        test_tool_compatibility()
        
        # Test command conflicts
        conflicts = test_command_conflicts()
        
        # Generate recommendations
        generate_recommendations()
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        total_duplications = sum(len(info['components']) for info in duplications.values())
        total_conflicts = len(conflicts)
        
        print(f"Total duplicate components: {total_duplications}")
        print(f"Total command conflicts: {total_conflicts}")
        print(f"Duplication categories: {len(duplications)}")
        
        if total_duplications > 0:
            print("\n⚠️  DUPLICATIONS DETECTED")
            print("Recommendation: Follow the recommendations above to resolve duplications.")
        else:
            print("\n✓ NO DUPLICATIONS DETECTED")
        
        if total_conflicts > 0:
            print("\n⚠️  COMMAND CONFLICTS DETECTED")
            print("Recommendation: Rename conflicting commands to avoid conflicts.")
        else:
            print("\n✓ NO COMMAND CONFLICTS DETECTED")
        
        print("\n" + "=" * 60)
        print("COMPATIBILITY TEST COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Compatibility test failed: {e}")
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 