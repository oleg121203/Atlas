"""
Plugin Tool for Atlas

This tool provides integration with the plugin system, allowing
the chat system to execute plugin commands and manage plugins.
"""

import json
import logging
from typing import Any, Dict

from plugins import (
    execute_plugin_command,
    get_plugin_manager,
    register_builtin_plugins,
    set_active_provider,
)

logger = logging.getLogger(__name__)


def initialize_plugin_system(provider: Any) -> Dict[str, Any]:
    """
    Initialize the plugin system with the active provider.

    Args:
        provider: The active provider from the chat system

    Returns:
        Dict with initialization status
    """
    try:
        # Register built-in plugins
        register_builtin_plugins()

        # Set the active provider
        set_active_provider(provider)

        # Get plugin manager
        manager = get_plugin_manager()

        return {
            "success": True,
            "message": "Plugin system initialized successfully",
            "available_plugins": manager.get_available_plugins(),
            "provider_set": True,
        }

    except Exception as e:
        logger.error(f"Failed to initialize plugin system: {e}")
        return {"success": False, "error": str(e)}


def execute_plugin(plugin_name: str, command: str, **kwargs) -> str:
    """
    Execute a plugin command.

    Args:
        plugin_name: Name of the plugin to execute
        command: Command to execute
        **kwargs: Additional arguments for the command

    Returns:
        JSON string with the result
    """
    try:
        result = execute_plugin_command(plugin_name, command, **kwargs)

        return json.dumps(
            {
                "success": result.success,
                "data": result.data,
                "error": result.error,
                "metadata": result.metadata,
            },
            indent=2,
        )

    except Exception as e:
        logger.error(f"Failed to execute plugin {plugin_name}: {e}")
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def list_plugins() -> str:
    """
    List all available plugins.

    Returns:
        JSON string with plugin information
    """
    try:
        manager = get_plugin_manager()
        plugins = manager.get_available_plugins()

        plugin_info = []
        for plugin_name in plugins:
            plugin = manager.plugins[plugin_name]
            plugin_info.append(
                {
                    "name": plugin_name,
                    "description": plugin.metadata.description,
                    "version": plugin.metadata.version,
                    "category": plugin.metadata.category,
                    "commands": plugin.get_commands(),
                    "initialized": plugin.is_initialized,
                }
            )

        return json.dumps(
            {"success": True, "plugins": plugin_info, "count": len(plugin_info)},
            indent=2,
        )

    except Exception as e:
        logger.error(f"Failed to list plugins: {e}")
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def get_plugin_help(plugin_name: str) -> str:
    """
    Get help information for a specific plugin.

    Args:
        plugin_name: Name of the plugin

    Returns:
        JSON string with help information
    """
    try:
        manager = get_plugin_manager()
        help_text = manager.get_plugin_help(plugin_name)

        return json.dumps(
            {"success": True, "plugin": plugin_name, "help": help_text}, indent=2
        )

    except Exception as e:
        logger.error(f"Failed to get help for plugin {plugin_name}: {e}")
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def gmail_search_emails(query: str, max_results: int = 50) -> str:
    """
    Search emails using Gmail plugin.

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        JSON string with email search results
    """
    return execute_plugin(
        "gmail", "search_emails", query=query, max_results=max_results
    )


def gmail_search_security_emails(days_back: int = 30) -> str:
    """
    Search for security-related emails using Gmail plugin.

    Args:
        days_back: Number of days to look back

    Returns:
        JSON string with security email results
    """
    return execute_plugin("gmail", "search_security_emails", days_back=days_back)


def browser_open_gmail() -> str:
    """
    Open Gmail in the browser using unified browser plugin.

    Returns:
        JSON string with browser operation result
    """
    return execute_plugin("unified_browser", "open_gmail")


def browser_search_gmail(query: str) -> str:
    """
    Search in Gmail using unified browser plugin.

    Args:
        query: Search query

    Returns:
        JSON string with browser search result
    """
    return execute_plugin("unified_browser", "search_gmail", query=query)


def browser_navigate_to_url(url: str) -> str:
    """
    Navigate to a URL using unified browser plugin.

    Args:
        url: URL to navigate to

    Returns:
        JSON string with browser navigation result
    """
    return execute_plugin("unified_browser", "navigate_to_url", url=url)


def browser_get_page_title() -> str:
    """
    Get the title of the current page using unified browser plugin.

    Returns:
        JSON string with page title
    """
    return execute_plugin("unified_browser", "get_page_title")


def browser_close_browser() -> str:
    """
    Close the browser using unified browser plugin.

    Returns:
        JSON string with browser close result
    """
    return execute_plugin("unified_browser", "close_browser")


def browser_execute_javascript(script: str) -> str:
    """
    Execute JavaScript code using unified browser plugin.

    Args:
        script: JavaScript code to execute

    Returns:
        JSON string with JavaScript execution result
    """
    return execute_plugin("unified_browser", "execute_javascript", script=script)


def register_plugin_tools():
    """
    Register plugin tools with the Atlas system.
    This function should be called during system initialization.
    """
    logger.info("Registering plugin tools...")

    # The plugin tools are now integrated into the main tool system
    # and will be available through the plugin system interface

    logger.info("Plugin tools registered successfully")


# Legacy compatibility functions
def legacy_browser_open_gmail() -> str:
    """
    Legacy function for backward compatibility.
    Now uses unified browser plugin.
    """
    return browser_open_gmail()


def legacy_browser_search_gmail(query: str) -> str:
    """
    Legacy function for backward compatibility.
    Now uses unified browser plugin.
    """
    return browser_search_gmail(query)


def legacy_browser_navigate_to_url(url: str) -> str:
    """
    Legacy function for backward compatibility.
    Now uses unified browser plugin.
    """
    return browser_navigate_to_url(url)
