"""
Plugin Tool for Atlas

This tool provides integration with the plugin system, allowing
the chat system to execute plugin commands and manage plugins.
"""

import logging
from typing import Any, Dict

from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class PluginTool(BaseTool):
    """Tool for managing and interacting with plugins."""

    def __init__(self):
        super().__init__()
        self.plugin_system = None  # Will be injected by tool manager

    def set_plugin_system(self, plugin_system):
        """Set the plugin system reference."""
        self.plugin_system = plugin_system

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute plugin-related actions.

        Args:
            action: The action to perform (list, load, activate, deactivate, etc.)
            **kwargs: Additional parameters for the action

        Returns:
            Dict with action results
        """
        if not self.plugin_system:
            return {"error": "Plugin system not available", "success": False}

        try:
            if action == "list":
                return await self._list_plugins()
            elif action == "load":
                plugin_name = kwargs.get("plugin_name")
                if not plugin_name:
                    return {"error": "plugin_name is required", "success": False}
                return await self._load_plugin(plugin_name)
            elif action == "activate":
                plugin_name = kwargs.get("plugin_name")
                if not plugin_name:
                    return {"error": "plugin_name is required", "success": False}
                return await self._activate_plugin(plugin_name)
            elif action == "deactivate":
                plugin_name = kwargs.get("plugin_name")
                if not plugin_name:
                    return {"error": "plugin_name is required", "success": False}
                return await self._deactivate_plugin(plugin_name)
            elif action == "status":
                plugin_name = kwargs.get("plugin_name")
                if not plugin_name:
                    return {"error": "plugin_name is required", "success": False}
                return await self._get_plugin_status(plugin_name)
            else:
                return {"error": f"Unknown action: {action}", "success": False}

        except Exception as e:
            logger.error(f"Error executing plugin action '{action}': {e}")
            return {"error": str(e), "success": False}

    async def _list_plugins(self) -> Dict[str, Any]:
        """List all available plugins."""
        try:
            plugins = self.plugin_system.list_plugins()
            active_plugins = self.plugin_system.list_active_plugins()

            result = {
                "success": True,
                "plugins": [],
                "count": len(plugins),
                "active_count": len(active_plugins),
            }

            for plugin_name in plugins:
                plugin_info = {
                    "name": plugin_name,
                    "active": plugin_name in active_plugins,
                    "loaded": plugin_name in self.plugin_system.loaded_plugins,
                }

                # Get plugin metadata if available
                plugin_instance = self.plugin_system.get_plugin(plugin_name)
                if plugin_instance:
                    try:
                        metadata = plugin_instance.get_metadata()
                        plugin_info.update(metadata)
                    except Exception as e:
                        logger.warning(f"Could not get metadata for {plugin_name}: {e}")

                result["plugins"].append(plugin_info)

            return result

        except Exception as e:
            logger.error(f"Error listing plugins: {e}")
            return {"error": str(e), "success": False}

    async def _load_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Load a plugin."""
        try:
            success = self.plugin_system.load_plugin(plugin_name)
            return {
                "success": success,
                "plugin_name": plugin_name,
                "action": "load",
                "message": f"Plugin {plugin_name} {'loaded' if success else 'failed to load'}",
            }
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e}")
            return {"error": str(e), "success": False}

    async def _activate_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Activate a plugin."""
        try:
            success = self.plugin_system.activate_plugin(plugin_name)
            return {
                "success": success,
                "plugin_name": plugin_name,
                "action": "activate",
                "message": f"Plugin {plugin_name} {'activated' if success else 'failed to activate'}",
            }
        except Exception as e:
            logger.error(f"Error activating plugin {plugin_name}: {e}")
            return {"error": str(e), "success": False}

    async def _deactivate_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Deactivate a plugin."""
        try:
            success = self.plugin_system.deactivate_plugin(plugin_name)
            return {
                "success": success,
                "plugin_name": plugin_name,
                "action": "deactivate",
                "message": f"Plugin {plugin_name} {'deactivated' if success else 'failed to deactivate'}",
            }
        except Exception as e:
            logger.error(f"Error deactivating plugin {plugin_name}: {e}")
            return {"error": str(e), "success": False}

    async def _get_plugin_status(self, plugin_name: str) -> Dict[str, Any]:
        """Get the status of a specific plugin."""
        try:
            plugins = self.plugin_system.list_plugins()
            active_plugins = self.plugin_system.list_active_plugins()

            if plugin_name not in plugins:
                return {"success": False, "error": f"Plugin {plugin_name} not found"}

            plugin_instance = self.plugin_system.get_plugin(plugin_name)
            status = {
                "success": True,
                "plugin_name": plugin_name,
                "exists": True,
                "loaded": plugin_name in self.plugin_system.loaded_plugins,
                "active": plugin_name in active_plugins,
            }

            # Get metadata if plugin is loaded
            if plugin_instance:
                try:
                    metadata = plugin_instance.get_metadata()
                    status.update(metadata)
                except Exception as e:
                    logger.warning(f"Could not get metadata for {plugin_name}: {e}")

            return status

        except Exception as e:
            logger.error(f"Error getting plugin status for {plugin_name}: {e}")
            return {"error": str(e), "success": False}

    def get_name(self) -> str:
        return "plugin_manager"

    def get_description(self) -> str:
        return "Manage and interact with Atlas plugins"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "description": "Action to perform: list, load, activate, deactivate, status",
                "required": True,
                "enum": ["list", "load", "activate", "deactivate", "status"],
            },
            "plugin_name": {
                "type": "string",
                "description": "Name of the plugin (required for load, activate, deactivate, status actions)",
                "required": False,
            },
        }
