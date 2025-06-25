"""
Helper Sync Tell Demonstration Script

This script demonstrates how the Helper Sync Tell tool works with a few example queries.
Run this script to see the tool in action with sample complex queries.
"""

import logging
import sys
from pathlib import Path

#Add the Atlas root directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

#Import Atlas components
try:
    #Import the HelperSyncTellTool from the plugin
    from plugin import HelperSyncTellTool

    from modules.agents.enhanced_memory_manager import (
        EnhancedMemoryManager,
        MemoryScope,
        MemoryType,
    )
    from config_manager import ConfigManager
    from utils.llm_manager import LLMManager
    from utils.platform_utils import get_platform_info
except ImportError as e:
    print(f"Error importing Atlas components: {e}")
    print("Please run this script from the plugins/helper_sync_tell directory.")
    sys.exit(1)

def simulate_tool(query):
    """Simulate a tool that provides information based on a query."""
    return f"Tool simulation result for: {query}"

def main():
    """Run a demonstration of the Helper Sync Tell tool."""
    print("=" * 80)
    print("Helper Sync Tell Demonstration")
    print("=" * 80)

    #Display platform information
    platform_info = get_platform_info()
    print(f"\nRunning on: {platform_info['system']} ({platform_info['release']})")
    print(f"Python version: {platform_info['python_version']}")
    print(f"Headless mode: {platform_info['is_headless']}")

    print("\nInitializing components...")

    #Try to initialize Atlas components if available
    try:
        config_manager = ConfigManager()
        llm_manager = LLMManager(config_manager)
        memory_manager = EnhancedMemoryManager(llm_manager, config_manager)

        #Create the Helper Sync Tell tool
        helper_tool = HelperSyncTellTool(
            llm_manager=llm_manager,
            memory_manager=memory_manager,
        )

        print("✓ Successfully initialized Atlas components")
    except Exception as e:
        print(f"Warning: Could not initialize Atlas components: {e}")
        print("Running in simplified demonstration mode without LLM or memory...")

        #Create a simplified tool without real components
        helper_tool = HelperSyncTellTool()

    #Create mock available tools
    available_tools = {
        "code_search": lambda q: f"Code search results for '{q}'",
        "memory_query": lambda q: f"Memory query results for '{q}'",
        "system_info": lambda q: f"System info related to '{q}'",
    }

    #Example complex queries
    example_queries = [
        "How does memory work in Atlas and how could it be improved?",
        "Compare the Linux development environment with the macOS target environment in Atlas",
        "What tools are available in Atlas and how do they integrate with the plugin system?",
    ]

    #Process each example query
    for i, query in enumerate(example_queries):
        print("\n" + "=" * 80)
        print(f"Example {i+1}: {query}")
        print("-" * 80)

        try:
            #Process the query using the Helper Sync Tell tool
            response = helper_tool(query, available_tools)

            print("\nResponse:")
            print(response)
        except Exception as e:
            print(f"Error processing query: {e}")

    print("\n" + "=" * 80)
    print("Demonstration complete!")

if __name__ == "__main__":
    main()
