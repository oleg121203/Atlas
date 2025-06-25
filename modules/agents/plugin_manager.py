"""Manages the loading and registration of dynamic plugins."""
from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from modules.agents.agent_manager import AgentManager
    from utils.llm_manager import LLMManager

from utils.logger import get_logger


class PluginManager:
    """Discovers, loads, and manages plugins from the plugins directory."""

    def __init__(self, agent_manager: AgentManager, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.agent_manager = agent_manager
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger()

    def discover_plugins(self, llm_manager: LLMManager, atlas_app=None):
        """Discovers plugins, loads metadata and modules, registers tools and agents.
        Auto-enables plugins after successful discovery."""
        if not self.plugin_dir.exists():
            self.logger.warning(f"Plugin directory {self.plugin_dir} does not exist")
            return

        for plugin_path in self.plugin_dir.iterdir():
            if plugin_path.is_dir():
                metadata = self._load_plugin_metadata(plugin_path)
                if metadata:
                    self.plugins[metadata['name']] = {
                        "metadata": metadata,
                        "path": plugin_path,
                        "enabled": False,
                        "modules": []
                    }
                    if self._check_dependencies(metadata):
                        self._load_plugin_modules(plugin_path, metadata['name'])
                        self.enable_plugin(metadata['name'])
                    else:
                        self.logger.warning(f"Dependencies not met for plugin {metadata['name']}")

    def _load_plugin_metadata(self, plugin_path: Path) -> Dict[str, Any]:
        """Load metadata from plugin's manifest file."""
        manifest_path = plugin_path / "manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading manifest for plugin at {plugin_path}: {e}")
        return {}

    def _check_dependencies(self, metadata: Dict[str, Any]) -> bool:
        """Check if all dependencies for a plugin are met."""
        dependencies = metadata.get('dependencies', {})
        for dep_name, dep_version in dependencies.items():
            if not self._check_dependency(dep_name, dep_version):
                self.logger.warning(f"Dependency {dep_name} version {dep_version} not met for {metadata['name']}")
                return False
        return True

    def _check_dependency(self, dep_name: str, dep_version: str) -> bool:
        """Check if a specific dependency version is met."""
        if dep_name not in self.plugins:
            return False
        installed_version = self.plugins[dep_name]['metadata'].get('version', '0.0.0')
        return self._compare_version(installed_version, dep_version)

    def _compare_version(self, installed: str, required: str) -> bool:
        """Compare version strings to check compatibility."""
        from packaging import version
        operator = ''
        if required.startswith(('>=', '<=', '==', '>', '<')):
            for op in ('>=', '<=', '==', '>', '<'):
                if required.startswith(op):
                    operator = op
                    required = required[len(op):]
                    break
        else:
            operator = '=='

        installed_ver = version.parse(installed)
        required_ver = version.parse(required)

        if operator == '>=':
            return installed_ver >= required_ver
        elif operator == '<=':
            return installed_ver <= required_ver
        elif operator == '==':
            return installed_ver == required_ver
        elif operator == '>':
            return installed_ver > required_ver
        elif operator == '<':
            return installed_ver < required_ver
        return False

    def _detect_conflicts(self) -> Dict[str, List[Dict]]:
        """Detect conflicts in plugin dependencies."""
        conflicts = {}
        for plugin_name, plugin_data in self.plugins.items():
            dependencies = plugin_data['metadata'].get('dependencies', {})
            for dep_name, dep_version in dependencies.items():
                if dep_name in self.plugins and not self._check_dependency(dep_name, dep_version):
                    if dep_name not in conflicts:
                        conflicts[dep_name] = []
                    conflicts[dep_name].append({
                        'plugin': plugin_name,
                        'required': dep_version,
                        'installed': self.plugins[dep_name]['metadata'].get('version', '0.0.0')
                    })
        return conflicts

    def _load_plugin_modules(self, plugin_path: Path, plugin_name: str):
        """Load plugin modules dynamically."""
        # Implementation for loading plugin modules
        pass

    def enable_plugin(self, plugin_name: str) -> bool:
        """Registers tools and agents with agent_manager."""
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin {plugin_name} not found")
            return False

        if self.plugins[plugin_name]["enabled"]:
            self.logger.info(f"Plugin {plugin_name} already enabled")
            return True

        if not self._check_dependencies(self.plugins[plugin_name]['metadata']):
            self.logger.error(f"Dependencies not met for plugin {plugin_name}")
            return False

        # Register tools and agents
        # Placeholder for actual implementation
        self.plugins[plugin_name]["enabled"] = True
        self.logger.info(f"Enabled plugin {plugin_name}")
        return True

    def disable_plugin(self, plugin_name: str) -> bool:
        """Unregisters tools and agents from agent_manager."""
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin {plugin_name} not found")
            return False

        if not self.plugins[plugin_name]["enabled"]:
            self.logger.info(f"Plugin {plugin_name} already disabled")
            return True

        # Check for dependent plugins
        for other_plugin, data in self.plugins.items():
            if other_plugin != plugin_name and data['enabled']:
                deps = data['metadata'].get('dependencies', {})
                if plugin_name in deps:
                    self.logger.error(f"Cannot disable {plugin_name}, required by {other_plugin}")
                    return False

        # Unregister tools and agents
        # Placeholder for actual implementation
        self.plugins[plugin_name]["enabled"] = False
        self.logger.info(f"Disabled plugin {plugin_name}")
        return True

    def get_all_plugins(self) -> Dict[str, Dict[str, Any]]:
        return self.plugins

    def get_plugin_status(self, plugin_name: str) -> Dict[str, Any]:
        """Returns status including whether tools are registered with agent_manager."""
        if plugin_name in self.plugins:
            return {
                "name": plugin_name,
                "enabled": self.plugins[plugin_name]["enabled"],
                "metadata": self.plugins[plugin_name]["metadata"]
            }
        return {}
