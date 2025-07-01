#!/usr/bin/env python3
"""
Test Script for Plugin System

This script demonstrates the plugin system functionality,
showing how plugins integrate with the active provider.
"""

import json
import logging
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins import execute_plugin_command
from tools.plugin_tool import (
    browser_navigate_to_url,
    get_plugin_help,
    gmail_search_emails,
    initialize_plugin_system,
    list_plugins,
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


def test_plugin_system():
    """Test the plugin system functionality."""
    print("=" * 60)
    print("ATLAS PLUGIN SYSTEM TEST")
    print("=" * 60)

    # Create a mock provider
    mock_provider = MockProvider("TestProvider")
    print(f"Created mock provider: {mock_provider}")

    # Test 1: Initialize plugin system
    print("\n1. Testing Plugin System Initialization")
    print("-" * 40)

    init_result = initialize_plugin_system(mock_provider)
    print(f"Initialization result: {json.dumps(init_result, indent=2)}")

    # Test 2: List available plugins
    print("\n2. Testing Plugin Listing")
    print("-" * 40)

    plugins_result = list_plugins()
    plugins_data = json.loads(plugins_result)
    print(f"Available plugins: {json.dumps(plugins_data, indent=2)}")

    # Test 3: Get plugin help
    print("\n3. Testing Plugin Help")
    print("-" * 40)

    for plugin_name in ["gmail", "browser"]:
        help_result = get_plugin_help(plugin_name)
        help_data = json.loads(help_result)
        print(f"\nHelp for {plugin_name}:")
        print(help_data.get("help", "No help available"))

    # Test 4: Test Gmail plugin (without credentials)
    print("\n4. Testing Gmail Plugin (Authentication Test)")
    print("-" * 40)

    # Test authentication status
    auth_result = execute_plugin_command("gmail", "authenticate")
    print(
        f"Gmail authentication status: {
            json.dumps(
                {
                    'success': auth_result.success,
                    'data': auth_result.data,
                    'error': auth_result.error,
                },
                indent=2,
            )
        }"
    )

    # Test 5: Test Browser plugin
    print("\n5. Testing Browser Plugin")
    print("-" * 40)

    # Test browser operations
    browser_tests = [
        ("get_page_title", {}),
        ("open_browser", {"browser_name": "Safari"}),
        ("navigate_to_url", {"url": "https://www.google.com"}),
        ("get_page_title", {}),
        ("close_browser", {}),
    ]

    for command, kwargs in browser_tests:
        print(f"\nTesting browser command: {command}")
        try:
            result = execute_plugin_command("browser", command, **kwargs)
            print(
                f"Result: {
                    json.dumps(
                        {
                            'success': result.success,
                            'data': result.data,
                            'error': result.error,
                            'metadata': result.metadata,
                        },
                        indent=2,
                    )
                }"
            )
        except Exception as e:
            print(f"Error: {e}")

    # Test 6: Test plugin tool functions
    print("\n6. Testing Plugin Tool Functions")
    print("-" * 40)

    # Test Gmail search (will fail without credentials, but shows the interface)
    print("\nTesting Gmail search tool:")
    gmail_result = gmail_search_emails("test", max_results=5)
    print(f"Gmail search result: {gmail_result}")

    # Test browser navigation tool
    print("\nTesting browser navigation tool:")
    nav_result = browser_navigate_to_url("https://www.example.com")
    print(f"Browser navigation result: {nav_result}")

    print("\n" + "=" * 60)
    print("PLUGIN SYSTEM TEST COMPLETED")
    print("=" * 60)


def test_plugin_creation():
    """Test creating a custom plugin."""
    print("\n" + "=" * 60)
    print("CUSTOM PLUGIN CREATION TEST")
    print("=" * 60)

    from plugins.base_plugin import BasePlugin, PluginMetadata, PluginResult

    class TestPlugin(BasePlugin):
        """A simple test plugin."""

        def get_metadata(self) -> PluginMetadata:
            return PluginMetadata(
                name="test_plugin",
                version="1.0.0",
                description="A simple test plugin",
                author="Test Author",
                category="test",
                tags=["test", "demo"],
            )

        def initialize(self, provider) -> bool:
            self.active_provider = provider
            self.logger.info(f"Test plugin initialized with provider: {provider}")
            return True

        def execute(self, command: str, **kwargs) -> PluginResult:
            if command == "hello":
                return PluginResult(
                    success=True,
                    data={
                        "message": f"Hello from test plugin! Provider: {self.active_provider}"
                    },
                    metadata={"command": command},
                )
            elif command == "echo":
                message = kwargs.get("message", "No message provided")
                return PluginResult(
                    success=True, data={"echo": message}, metadata={"command": command}
                )
            else:
                return PluginResult(success=False, error=f"Unknown command: {command}")

        def get_commands(self):
            return ["hello", "echo"]

    # Create and register the test plugin
    test_plugin = TestPlugin()
    from plugins.base_plugin import register_plugin

    register_plugin(test_plugin)

    # Test the custom plugin
    print("Testing custom plugin:")

    # Test hello command
    hello_result = execute_plugin_command("test_plugin", "hello")
    print(
        f"Hello command result: {
            json.dumps(
                {
                    'success': hello_result.success,
                    'data': hello_result.data,
                    'error': hello_result.error,
                },
                indent=2,
            )
        }"
    )

    # Test echo command
    echo_result = execute_plugin_command("test_plugin", "echo", message="Test message")
    print(
        f"Echo command result: {
            json.dumps(
                {
                    'success': echo_result.success,
                    'data': echo_result.data,
                    'error': echo_result.error,
                },
                indent=2,
            )
        }"
    )

    # Test unknown command
    unknown_result = execute_plugin_command("test_plugin", "unknown")
    print(
        f"Unknown command result: {
            json.dumps(
                {
                    'success': unknown_result.success,
                    'data': unknown_result.data,
                    'error': unknown_result.error,
                },
                indent=2,
            )
        }"
    )


def main():
    """Main test function."""
    try:
        test_plugin_system()
        test_plugin_creation()

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
