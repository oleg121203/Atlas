import importlib
import importlib.util
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class PluginManager:
    """Manager for discovering, loading, and handling plugins in Atlas."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.plugins: Dict[str, Any] = {}
        self.plugin_dir = Path(self.config.get("plugin_dir", "plugins"))
        self.initialize()

    def initialize(self) -> None:
        """Initialize the plugin manager and create plugin directory if needed."""
        self.logger.info("Initializing Plugin Manager")
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(parents=True)
            self.logger.info("Created plugin directory: %s", self.plugin_dir)

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugin directory.

        Returns:
            List[str]: List of plugin names discovered.
        """
        self.logger.info("Discovering plugins in %s", self.plugin_dir)
        plugin_names = []

        for item in self.plugin_dir.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                plugin_names.append(item.name)
                self.logger.debug("Found plugin: %s", item.name)
            elif item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                plugin_names.append(item.stem)
                self.logger.info("Found plugin: %s", item.stem)

        self.logger.info("Discovered %d plugins", len(plugin_names))
        return plugin_names

    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin by name."""
        self.logger.info("Loading plugin: %s", plugin_name)
        try:
            if plugin_name in self.plugins:
                self.logger.info("Plugin %s already loaded", plugin_name)
                return True

            plugin_path = self.plugin_dir / plugin_name
            if not plugin_path.exists():
                plugin_path = self.plugin_dir / f"{plugin_name}.py"
                if not plugin_path.exists():
                    self.logger.error(
                        "Plugin %s not found in %s", plugin_name, self.plugin_dir
                    )
                    return False

            # Handle directory-based plugins
            if plugin_path.is_dir():
                module_name = f"plugins.{plugin_name}"
                spec = importlib.util.spec_from_file_location(
                    module_name, str(plugin_path / "__init__.py")
                )
            # Handle file-based plugins
            else:
                module_name = f"plugins.{plugin_name}"
                spec = importlib.util.spec_from_file_location(
                    module_name, str(plugin_path)
                )

            if spec is None or spec.loader is None:
                self.logger.error("Failed to create spec for plugin %s", plugin_name)
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Look for a Plugin class or main entry point
            plugin_class = getattr(module, "Plugin", None) or getattr(
                module, f"{plugin_name.capitalize()}Plugin", None
            )
            if plugin_class:
                self.plugins[plugin_name] = plugin_class()
            else:
                self.plugins[plugin_name] = module

            self.logger.info("Successfully loaded plugin: %s", plugin_name)
            return True

        except Exception as e:
            self.logger.error("Error loading plugin %s: %s", plugin_name, str(e))
            return False

    def load_all_plugins(self) -> Dict[str, bool]:
        """Load all discovered plugins."""
        self.logger.info("Loading all plugins")
        results = {}
        plugin_names = self.discover_plugins()
        for plugin_name in plugin_names:
            results[plugin_name] = self.load_plugin(plugin_name)
        return results

    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """Get a loaded plugin by name."""
        return self.plugins.get(plugin_name)

    def list_loaded_plugins(self) -> List[str]:
        """List all loaded plugins."""
        return list(self.plugins.keys())

    def register_plugin(self, plugin_name: str, plugin_instance: Any) -> None:
        """Register a plugin instance manually."""
        self.plugins[plugin_name] = plugin_instance
        self.logger.info("Manually registered plugin: %s", plugin_name)

    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin."""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            self.logger.info("Unregistered plugin: %s", plugin_name)
            return True
        return False

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin."""
        if plugin_name in self.plugins:
            self.unregister_plugin(plugin_name)
        return self.load_plugin(plugin_name)

    def execute_plugin_function(
        self, plugin_name: str, function_name: str, *args, **kwargs
    ) -> Any:
        """Execute a function from a specific plugin."""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            self.logger.error("Plugin not found: %s", plugin_name)
            raise ValueError(f"Plugin {plugin_name} not found")

        func = getattr(plugin, function_name, None)
        if not func:
            self.logger.error(
                "Function %s not found in plugin %s", function_name, plugin_name
            )
            raise ValueError(
                f"Function {function_name} not found in plugin {plugin_name}"
            )

        self.logger.info(
            "Executing function %s from plugin %s", function_name, plugin_name
        )
        return func(*args, **kwargs)

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plugin."""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return None

        info = {
            "name": plugin_name,
            "path": str(self.plugin_dir / plugin_name),
            "version": getattr(plugin, "__version__", "unknown"),
            "description": getattr(
                plugin, "__description__", "No description available"
            ),
        }
        return info
