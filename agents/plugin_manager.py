"""Manages the loading and registration of dynamic plugins."""
from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from agents.agent_manager import AgentManager
    from agents.llm_manager import LLMManager

from utils.logger import get_logger


class PluginManager:
    """Discovers, loads, and manages plugins from the plugins directory."""

    def __init__(self, agent_manager: AgentManager, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.agent_manager = agent_manager
        #The plugins dict stores all metadata, including the loaded tools for each plugin
        #Structure: { "plugin_folder_name": { "manifest": {...}, "module": <module>, "tools": [...] } }
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger()

    def discover_plugins(self, llm_manager: LLMManager, atlas_app=None):
        """Finds and loads all valid plugins and their tools."""
        self.logger.info(f"Discovering plugins in '{self.plugin_dir}'...")
        for plugin_path in self.plugin_dir.iterdir():
            if not plugin_path.is_dir():
                continue

            plugin_name = plugin_path.name
            manifest_path = plugin_path / "plugin.json"
            plugin_file_path = plugin_path / "plugin.py"

            if not manifest_path.exists() or not plugin_file_path.exists():
                self.logger.warning(
                    f"Skipping '{plugin_name}' as it lacks a manifest or plugin file."
                )
                continue

            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)

                spec = importlib.util.spec_from_file_location(
                    manifest.get("entry_point", plugin_name),
                    plugin_file_path,
                )
                if not spec or not spec.loader:
                    self.logger.error(f"Could not create module spec for {plugin_name}")
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                tools = []
                agents = []
                if hasattr(module, "register") and callable(module.register):
                    try:
                        sig = inspect.signature(module.register)
                        #Enhanced parameter detection for better plugin integration
                        param_names = list(sig.parameters.keys())
                        
                        #Prepare arguments based on plugin requirements
                        call_args = {}
                        if 'llm_manager' in param_names:
                            call_args['llm_manager'] = llm_manager
                        if 'atlas_app' in param_names:
                            call_args['atlas_app'] = atlas_app
                        if 'agent_manager' in param_names:
                            call_args['agent_manager'] = self.agent_manager
                        
                        #Call with appropriate arguments
                        if len(sig.parameters) > 0:
                            if call_args:
                                registration_data = module.register(**call_args)
                            else:
                                #Fallback to positional arguments for backward compatibility
                                registration_data = module.register(llm_manager)
                        else:
                            registration_data = module.register()
                            
                    except Exception as e:
                        self.logger.error(f"Error calling register() for plugin '{plugin_name}': {e}")
                        continue
                    if isinstance(registration_data, dict):
                        tools = registration_data.get("tools", [])
                        agents = registration_data.get("agents", [])
                    elif isinstance(registration_data, list):
                        #For backward compatibility with plugins returning only a list of tools
                        tools = registration_data
                    
                    self.logger.info(
                        f"Plugin '{plugin_name}' registered {len(tools)} tools and {len(agents)} agents."
                    )

                self.plugins[plugin_name] = {
                    "manifest": manifest,
                    "module": module,
                    "tools": tools,
                    "agents": agents,
                }

                #Auto-enable the plugin after successful discovery
                self.enable_plugin(plugin_name)

            except Exception as e:
                self.logger.error(
                    f"Failed to load plugin '{plugin_name}': {e}", exc_info=True
                )

    def get_all_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Returns a dictionary of all discovered plugins and their data."""
        return self.plugins

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin by registering its tools and agents."""
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin '{plugin_name}' not found")
            return False
            
        try:
            plugin_data = self.plugins[plugin_name]
            tools = plugin_data.get("tools", [])
            agents = plugin_data.get("agents", [])
            
            #Register tools
            for tool in tools:
                if hasattr(tool, '__name__'):
                    tool_name = tool.__name__
                    self.agent_manager.add_tool(tool_name, tool, getattr(tool, '__doc__', ''))
                    
            #Register agents (if any)
            for agent in agents:
                if hasattr(agent, 'name'):
                    self.agent_manager.add_agent(agent.name, agent)
                    
            self.logger.info(f"Plugin '{plugin_name}' enabled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable plugin '{plugin_name}': {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin by unregistering its tools and agents."""
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin '{plugin_name}' not found")
            return False
            
        try:
            plugin_data = self.plugins[plugin_name]
            tools = plugin_data.get("tools", [])
            agents = plugin_data.get("agents", [])
            
            #Unregister tools
            for tool in tools:
                if hasattr(tool, '__name__'):
                    tool_name = tool.__name__
                    if hasattr(self.agent_manager, 'remove_tool'):
                        self.agent_manager.remove_tool(tool_name)
                    elif hasattr(self.agent_manager, '_tools') and tool_name in self.agent_manager._tools:
                        del self.agent_manager._tools[tool_name]
                        
            #Unregister agents (if any)
            for agent in agents:
                if hasattr(agent, 'name') and hasattr(self.agent_manager, 'remove_agent'):
                    self.agent_manager.remove_agent(agent.name)
                    
            self.logger.info(f"Plugin '{plugin_name}' disabled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disable plugin '{plugin_name}': {e}")
            return False

    def get_plugin_status(self, plugin_name: str) -> Dict[str, Any]:
        """Get the current status of a plugin."""
        if plugin_name not in self.plugins:
            return {"exists": False, "enabled": False}
            
        plugin_data = self.plugins[plugin_name]
        tools = plugin_data.get("tools", [])
        
        #Check if plugin tools are registered
        enabled = False
        if tools and hasattr(self.agent_manager, '_tools'):
            for tool in tools:
                if hasattr(tool, '__name__') and tool.__name__ in self.agent_manager._tools:
                    enabled = True
                    break
                    
        return {
            "exists": True,
            "enabled": enabled,
            "manifest": plugin_data.get("manifest", {}),
            "tool_count": len(tools),
            "agent_count": len(plugin_data.get("agents", []))
        }
