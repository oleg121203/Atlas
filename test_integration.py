#!/usr/bin/env python3
"""
Integration test script for Atlas core systems.

This script tests the integration between:
- AtlasApplication
- PluginSystem
- ToolManager
- Event system
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the Atlas root to Python path
atlas_root = Path(__file__).parent
sys.path.insert(0, str(atlas_root))

from core.application import AtlasApplication

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_atlas_integration():
    """Test Atlas systems integration."""
    logger.info("Starting Atlas integration test...")

    try:
        # Initialize the Atlas application
        logger.info("Initializing Atlas application...")
        app = AtlasApplication()

        # Initialize all systems
        logger.info("Starting Atlas application...")
        app.start()

        # Test plugin system
        logger.info("Testing plugin system...")
        plugin_system = app.plugin_system
        if plugin_system:
            logger.info(
                f"Plugin system available: {len(plugin_system.list_plugins())} plugins loaded"
            )

            # List discovered plugins
            discovered = plugin_system.registry.discover_plugins()
            logger.info(f"Discovered plugins: {discovered}")

            # Test loading a plugin
            if discovered:
                test_plugin = discovered[0]
                logger.info(f"Testing plugin: {test_plugin}")

                if plugin_system.load_plugin(test_plugin):
                    logger.info(f"✓ Plugin {test_plugin} loaded successfully")

                    if plugin_system.activate_plugin(test_plugin):
                        logger.info(f"✓ Plugin {test_plugin} activated successfully")

                        # Get plugin status
                        status = plugin_system.get_plugin_status(test_plugin)
                        logger.info(f"Plugin status: {status}")

                        # Deactivate plugin
                        if plugin_system.deactivate_plugin(test_plugin):
                            logger.info(
                                f"✓ Plugin {test_plugin} deactivated successfully"
                            )
                    else:
                        logger.error(f"✗ Failed to activate plugin {test_plugin}")
                else:
                    logger.error(f"✗ Failed to load plugin {test_plugin}")
        else:
            logger.warning("Plugin system not available")

        # Test tool manager
        logger.info("Testing tool manager...")
        tool_manager = app.tool_manager
        if tool_manager:
            logger.info(
                f"Tool manager available: {len(tool_manager.list_tools())} tools loaded"
            )

            # Initialize all tools
            tool_manager.initialize_all_tools()
            logger.info(
                f"After initialization: {len(tool_manager.list_tools())} tools loaded"
            )

            # List tool categories
            categories = tool_manager.list_categories()
            logger.info(f"Tool categories: {list(categories.keys())}")
        else:
            logger.warning("Tool manager not available")

        # Test event system
        logger.info("Testing event system...")
        event_bus = app.event_bus
        if event_bus:
            # Test event publishing and subscribing
            test_events = []

            def test_handler(data):
                test_events.append(data)
                logger.info(f"Received test event: {data}")

            event_bus.subscribe("test_event", test_handler)
            event_bus.publish("test_event", {"message": "Hello from test!"})

            # Give event some time to process
            await asyncio.sleep(0.1)

            if test_events:
                logger.info("✓ Event system working correctly")
            else:
                logger.error("✗ Event system not working")
        else:
            logger.warning("Event bus not available")  # Test configuration
        logger.info("Testing configuration...")
        config = app.config
        if config:
            logger.info(f"Configuration loaded with {len(config._config)} settings")

            # Test setting and getting values
            config.set("test.integration", "success")
            value = config.get("test.integration")
            if value == "success":
                logger.info("✓ Configuration system working correctly")
            else:
                logger.error("✗ Configuration system not working")
        else:
            logger.warning("Configuration not available")

        logger.info("Integration test completed successfully!")

        # Shutdown
        logger.info("Shutting down Atlas application...")
        app.shutdown()

        return True

    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_atlas_integration())
    sys.exit(0 if success else 1)
