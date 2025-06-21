"""
Enhanced Plugin Manager with memory isolation and better organization
"""

import importlib.util
import inspect
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

if TYPE_CHECKING:
    from agents.agent_manager import AgentManager
    from utils.llm_manager import LLMManager

from agents.enhanced_memory_manager import (
    EnhancedMemoryManager,
    MemoryScope,
    MemoryType,
)
from utils.config_manager import ConfigManager
from utils.logger import get_logger


class EnhancedPluginManager:
    """
    Enhanced Plugin Manager with memory isolation and structured organization.
    
    Features:
    - Memory isolation per plugin
    - Plugin configuration persistence
    - Enhanced error handling
    - Plugin dependencies tracking
    - Version management
    """

    def __init__(self, agent_manager: "AgentManager", plugin_dir: str = "plugins",
                 memory_manager: Optional[EnhancedMemoryManager] = None):
        self.plugin_dir = Path(plugin_dir)
        self.agent_manager = agent_manager
        self.memory_manager = memory_manager or EnhancedMemoryManager()
        self.config_manager = ConfigManager()
        self.logger = get_logger()

        #Plugin state tracking
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self.enabled_plugins: Set[str] = set()
        self.plugin_dependencies: Dict[str, List[str]] = {}
        self.plugin_memory_scopes: Dict[str, MemoryScope] = {}

        #Load plugin configuration
        self._load_plugin_config()

    def _load_plugin_config(self):
        """Load plugin configuration and enabled state."""
        try:
            config = self.config_manager.load()
            plugin_config = config.get("plugins", {})

            self.enabled_plugins = set(plugin_config.get("enabled", []))
            self.plugin_dependencies = plugin_config.get("dependencies", {})

            self.logger.info(f"Loaded plugin configuration: {len(self.enabled_plugins)} enabled")
        except Exception as e:
            self.logger.error(f"Failed to load plugin configuration: {e}")

    def _save_plugin_config(self):
        """Save plugin configuration."""
        try:
            config = self.config_manager.load()
            config["plugins"] = {
                "enabled": list(self.enabled_plugins),
                "dependencies": self.plugin_dependencies,
                "memory_scopes": {name: scope.value for name, scope in self.plugin_memory_scopes.items()},
            }
            self.config_manager.save(config)
            self.logger.info("Plugin configuration saved")
        except Exception as e:
            self.logger.error(f"Failed to save plugin configuration: {e}")

    def discover_plugins(self, llm_manager: "LLMManager"):
        """Discover and load plugins with enhanced memory isolation."""
        self.logger.info(f"Discovering plugins in '{self.plugin_dir}'...")

        for plugin_path in self.plugin_dir.iterdir():
            if not plugin_path.is_dir():
                continue

            plugin_name = plugin_path.name
            if plugin_name.startswith(".") or plugin_name == "__pycache__":
                continue

            try:
                self._load_plugin(plugin_name, plugin_path, llm_manager)
            except Exception as e:
                self.logger.error(f"Failed to load plugin '{plugin_name}': {e}", exc_info=True)

        #Save updated configuration
        self._save_plugin_config()

    def _load_plugin(self, plugin_name: str, plugin_path: Path, llm_manager: "LLMManager"):
        """Load a single plugin with memory isolation."""
        manifest_path = plugin_path / "plugin.json"
        plugin_file_path = plugin_path / "plugin.py"

        if not manifest_path.exists() or not plugin_file_path.exists():
            self.logger.warning(f"Skipping '{plugin_name}' - missing manifest or plugin file")
            return

        #Load manifest
        with open(manifest_path) as f:
            manifest = json.load(f)

        #Validate manifest
        if not self._validate_manifest(manifest, plugin_name):
            return

        #Create plugin memory scope
        plugin_scope = self._create_plugin_memory_scope(plugin_name)
        self.plugin_memory_scopes[plugin_name] = plugin_scope

        #Load plugin module
        spec = importlib.util.spec_from_file_location(
            manifest.get("entry_point", plugin_name),
            plugin_file_path,
        )
        if not spec or not spec.loader:
            self.logger.error(f"Could not create module spec for {plugin_name}")
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        #Register plugin with memory isolation
        tools, agents = self._register_plugin(module, plugin_name, llm_manager, plugin_scope)

        #Store plugin information
        self.plugins[plugin_name] = {
            "manifest": manifest,
            "module": module,
            "tools": tools,
            "agents": agents,
            "memory_scope": plugin_scope,
            "loaded_at": time.time(),
            "version": manifest.get("version", "1.0.0"),
            "dependencies": manifest.get("dependencies", []),
        }

        #Track dependencies
        self.plugin_dependencies[plugin_name] = manifest.get("dependencies", [])

        #Store plugin metadata in memory
        self._store_plugin_metadata(plugin_name, manifest, tools, agents)

        #Auto-enable if configured
        if plugin_name in self.enabled_plugins or manifest.get("auto_enable", False):
            self.enable_plugin(plugin_name)

        self.logger.info(f"Plugin '{plugin_name}' loaded: {len(tools)} tools, {len(agents)} agents")

    def _validate_manifest(self, manifest: Dict, plugin_name: str) -> bool:
        """Validate plugin manifest."""
        required_fields = ["name", "version", "description"]
        for field in required_fields:
            if field not in manifest:
                self.logger.error(f"Plugin '{plugin_name}' manifest missing required field: {field}")
                return False
        return True

    def _create_plugin_memory_scope(self, plugin_name: str) -> MemoryScope:
        """Create a dedicated memory scope for a plugin."""
        #For now, use USER_DATA scope with plugin prefix
        #In future, could extend MemoryScope enum dynamically
        return MemoryScope.USER_DATA

    def _register_plugin(self, module, plugin_name: str, llm_manager: "LLMManager",
                        memory_scope: MemoryScope) -> tuple[List, List]:
        """Register plugin with memory-aware context."""
        tools = []
        agents = []

        if hasattr(module, "register") and callable(module.register):
            try:
                #Create plugin context with memory isolation
                plugin_context = {
                    "memory_manager": self.memory_manager,
                    "memory_scope": memory_scope,
                    "plugin_name": plugin_name,
                    "llm_manager": llm_manager,
                    "config_manager": self.config_manager,
                }

                #Check register function signature
                sig = inspect.signature(module.register)
                if len(sig.parameters) > 1:
                    #Enhanced registration with context
                    registration_data = module.register(llm_manager, plugin_context)
                elif len(sig.parameters) == 1:
                    #Standard registration
                    registration_data = module.register(llm_manager)
                else:
                    #No parameters
                    registration_data = module.register()

                #Process registration data
                if isinstance(registration_data, dict):
                    tools = registration_data.get("tools", [])
                    agents = registration_data.get("agents", [])
                elif isinstance(registration_data, list):
                    tools = registration_data

            except Exception as e:
                self.logger.error(f"Error registering plugin '{plugin_name}': {e}", exc_info=True)

        return tools, agents

    def _store_plugin_metadata(self, plugin_name: str, manifest: Dict, tools: List, agents: List):
        """Store plugin metadata in memory for tracking."""
        metadata = {
            "plugin_name": plugin_name,
            "version": manifest.get("version", "1.0.0"),
            "description": manifest.get("description", ""),
            "tools_count": len(tools),
            "agents_count": len(agents),
            "loaded_at": time.time(),
            "dependencies": manifest.get("dependencies", []),
        }

        #Store in memory with plugin-specific scope
        self.memory_manager.store_memory(
            agent_name=f"plugin_{plugin_name}",
            memory_type=MemoryType.KNOWLEDGE,
            content=f"Plugin {plugin_name} metadata",
            metadata=metadata,
            ttl_days=365,  #Keep plugin metadata for a year
        )

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name not in self.plugins:
            self.logger.error(f"Cannot enable unknown plugin: {plugin_name}")
            return False

        #Check dependencies
        if not self._check_dependencies(plugin_name):
            return False

        #Enable plugin
        self.enabled_plugins.add(plugin_name)

        #Store enable event in memory
        self._store_plugin_event(plugin_name, "enabled")

        self.logger.info(f"Plugin '{plugin_name}' enabled")
        return True

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name not in self.enabled_plugins:
            return False

        #Check if other plugins depend on this one
        dependents = [name for name, deps in self.plugin_dependencies.items()
                     if plugin_name in deps and name in self.enabled_plugins]

        if dependents:
            self.logger.warning(f"Cannot disable '{plugin_name}' - required by: {dependents}")
            return False

        #Disable plugin
        self.enabled_plugins.discard(plugin_name)

        #Store disable event in memory
        self._store_plugin_event(plugin_name, "disabled")

        self.logger.info(f"Plugin '{plugin_name}' disabled")
        return True

    def _check_dependencies(self, plugin_name: str) -> bool:
        """Check if plugin dependencies are satisfied."""
        dependencies = self.plugin_dependencies.get(plugin_name, [])

        for dep in dependencies:
            if dep not in self.enabled_plugins:
                self.logger.error(f"Plugin '{plugin_name}' requires '{dep}' to be enabled")
                return False

        return True

    def _store_plugin_event(self, plugin_name: str, event: str):
        """Store plugin lifecycle events in memory."""
        metadata = {
            "plugin_name": plugin_name,
            "event": event,
            "timestamp": time.time(),
        }

        self.memory_manager.store_memory(
            agent_name=f"plugin_{plugin_name}",
            memory_type=MemoryType.SESSION,
            content=f"Plugin {plugin_name} {event}",
            metadata=metadata,
            ttl_days=30,
        )

    def get_plugin_memory_context(self, plugin_name: str, query: str, limit: int = 10) -> List[Dict]:
        """Get memory context for a specific plugin."""
        if plugin_name not in self.plugins:
            return []

        return self.memory_manager.retrieve_memories(
            agent_name=f"plugin_{plugin_name}",
            memory_type=MemoryType.KNOWLEDGE,
            query=query,
            limit=limit,
        )

    def get_all_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Get all discovered plugins with enhanced info."""
        enhanced_plugins = {}

        for name, plugin_data in self.plugins.items():
            enhanced_plugins[name] = {
                **plugin_data,
                "enabled": name in self.enabled_plugins,
                "memory_scope": plugin_data["memory_scope"].value,
                "has_dependencies": len(self.plugin_dependencies.get(name, [])) > 0,
                "dependents": [p for p, deps in self.plugin_dependencies.items() if name in deps],
            }

        return enhanced_plugins

    def get_enabled_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Get only enabled plugins."""
        return {name: data for name, data in self.get_all_plugins().items()
                if data["enabled"]}

    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get plugin system statistics."""
        total_plugins = len(self.plugins)
        enabled_count = len(self.enabled_plugins)
        total_tools = sum(len(p["tools"]) for p in self.plugins.values())
        total_agents = sum(len(p["agents"]) for p in self.plugins.values())

        return {
            "total_plugins": total_plugins,
            "enabled_plugins": enabled_count,
            "disabled_plugins": total_plugins - enabled_count,
            "total_tools": total_tools,
            "total_agents": total_agents,
            "memory_scopes": len(set(self.plugin_memory_scopes.values())),
            "with_dependencies": len([p for p in self.plugin_dependencies.values() if p]),
        }

    def cleanup_plugin_memory(self, plugin_name: str, days_old: int = 30):
        """Clean up old memory entries for a plugin."""
        if plugin_name not in self.plugins:
            return

        #This would be handled by the memory manager's TTL system
        #But we can trigger manual cleanup if needed
        self.logger.info(f"Memory cleanup for plugin '{plugin_name}' is handled by TTL system")

    def reload_plugin(self, plugin_name: str, llm_manager: "LLMManager") -> bool:
        """Reload a plugin (useful for development)."""
        if plugin_name not in self.plugins:
            self.logger.error(f"Cannot reload unknown plugin: {plugin_name}")
            return False

        #Store reload event
        self._store_plugin_event(plugin_name, "reloading")

        #Disable first
        was_enabled = plugin_name in self.enabled_plugins
        if was_enabled:
            self.disable_plugin(plugin_name)

        #Remove from plugins
        plugin_path = self.plugin_dir / plugin_name
        del self.plugins[plugin_name]

        try:
            #Reload
            self._load_plugin(plugin_name, plugin_path, llm_manager)

            #Re-enable if it was enabled
            if was_enabled:
                self.enable_plugin(plugin_name)

            self._store_plugin_event(plugin_name, "reloaded")
            self.logger.info(f"Plugin '{plugin_name}' reloaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to reload plugin '{plugin_name}': {e}")
            self._store_plugin_event(plugin_name, "reload_failed")
            return False
