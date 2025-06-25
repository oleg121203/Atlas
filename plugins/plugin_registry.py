from typing import Dict, Type, Optional, List, Set, Any
from pathlib import Path
import importlib.util
import inspect
import sys
import logging
from plugins.base import PluginBase

logger = logging.getLogger(__name__)

class PluginRegistry:
    """Registry for managing Atlas plugins.

    Attributes:
        plugins: Dictionary of loaded plugins
        active_plugins: Set of active plugin names
        plugin_dir: Path to plugins directory
    """

    def __init__(self):
        """Initialize the plugin registry."""
        self.plugins: Dict[str, Type[PluginBase]] = {}
        self.active_plugins: Set[str] = set()
        self.plugin_dir: Path = Path(__file__).parent
        self._load_plugins()

    def _load_plugins(self) -> None:
        """Load all plugins from the plugins directory.

        This method scans the plugins directory for Python files and attempts to
        load any classes that inherit from PluginBase.
        """
        try:
            for plugin_file in self.plugin_dir.glob('*.py'):
                if plugin_file.name == '__init__.py':
                    continue

                module_name = plugin_file.stem
                module_path = str(plugin_file)

                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        for name, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and 
                                issubclass(obj, PluginBase) and 
                                obj != PluginBase):
                                plugin = obj()
                                self._validate_plugin(plugin)
                                self.plugins[plugin.metadata.name] = plugin
                                logger.info(f"Loaded plugin: {plugin.metadata.name}")
                except Exception as e:
                    logger.error(f"Error loading plugin {module_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error scanning plugins directory: {str(e)}")

    def _validate_plugin(self, plugin: PluginBase) -> None:
        """Validate plugin metadata and compatibility.

        Args:
            plugin: Plugin instance to validate

        Raises:
            ValueError: If plugin validation fails
        """
        metadata = plugin.metadata
        
        if not metadata.name:
            raise ValueError("Plugin must have a name")
        
        if not metadata.version:
            raise ValueError("Plugin must have a version")
        
        if not metadata.author:
            raise ValueError("Plugin must have an author")
        
        if not metadata.min_app_version:
            raise ValueError("Plugin must specify minimum app version")
        
        # Additional validation can be added here

    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Optional[PluginBase]: Plugin instance or None
        """
        return self.plugins.get(name)

    def activate_plugin(self, name: str) -> bool:
        """Activate a plugin.

        Args:
            name: Plugin name

        Returns:
            bool: True if activation was successful
        """
        plugin = self.get_plugin(name)
        if not plugin:
            logger.error(f"Plugin {name} not found")
            return False

        try:
            plugin.activate()
            self.active_plugins.add(name)
            logger.info(f"Activated plugin: {name}")
            return True
        except Exception as e:
            logger.error(f"Error activating plugin {name}: {str(e)}")
            return False

    def deactivate_plugin(self, name: str) -> bool:
        """Deactivate a plugin.

        Args:
            name: Plugin name

        Returns:
            bool: True if deactivation was successful
        """
        plugin = self.get_plugin(name)
        if not plugin:
            logger.error(f"Plugin {name} not found")
            return False

        try:
            plugin.deactivate()
            self.active_plugins.discard(name)
            logger.info(f"Deactivated plugin: {name}")
            return True
        except Exception as e:
            logger.error(f"Error deactivating plugin {name}: {str(e)}")
            return False

    def reload_all_plugins(self) -> None:
        """Reload all plugins.

        This method clears the current plugins and reloads them from disk.
        """
        try:
            self.plugins.clear()
            self.active_plugins.clear()
            self._load_plugins()
            logger.info("All plugins reloaded")
        except Exception as e:
            logger.error(f"Error reloading plugins: {str(e)}")

    def list_plugins(self) -> List[PluginBase]:
        """Get list of all loaded plugins.

        Returns:
            List[PluginBase]: List of plugin instances
        """
        return list(self.plugins.values())

    def get_active_plugins(self) -> List[PluginBase]:
        """Get list of active plugins.

        Returns:
            List[PluginBase]: List of active plugin instances
        """
        return [self.plugins[name] for name in self.active_plugins if name in self.plugins]

    def get_plugin_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a plugin.

        Args:
            name: Plugin name

        Returns:
            Dict[str, Any]: Plugin information
        """
        plugin = self.get_plugin(name)
        if not plugin:
            return {}
        return plugin.info()
