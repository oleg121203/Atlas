"""Plugin Manager for Atlas."""

import importlib
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, Slot

from .plugin_interface import PluginInterface


class PluginManager(QObject):
    """Manager for loading, initializing, and managing plugins in Atlas."""

    plugins_loaded = Signal(list)
    plugin_status_changed = Signal(str, str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.plugins_directory = os.path.join(os.path.dirname(__file__), "")
        self.plugins: Dict[str, PluginInterface] = {}
        self.logger.info("PluginManager initialized")

    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory.

        Returns:
            List[str]: List of discovered plugin IDs.
        """
        plugin_ids = []
        plugins_path = self.plugins_directory
        self.logger.debug(f"Discovering plugins in {plugins_path}")

        if not os.path.exists(plugins_path):
            self.logger.warning(f"Plugins directory does not exist: {plugins_path}")
            return plugin_ids

        # Add plugins directory to sys.path if not already there
        if plugins_path not in sys.path:
            sys.path.append(plugins_path)
            self.logger.debug(f"Added {plugins_path} to sys.path")

        for entry in os.scandir(plugins_path):
            if entry.is_dir() and not entry.name.startswith("__"):
                plugin_id = entry.name
                plugin_ids.append(plugin_id)
                self.logger.debug(f"Discovered plugin: {plugin_id}")

        self.logger.info(f"Discovered {len(plugin_ids)} plugins")
        return plugin_ids

    def load_plugins(self, plugin_ids: Optional[List[str]] = None) -> None:
        """Load specified plugins or all discovered plugins if none specified.

        Args:
            plugin_ids (Optional[List[str]]): List of plugin IDs to load. If None, discovers all.
        """
        if plugin_ids is None:
            plugin_ids = self.discover_plugins()

        self.logger.info(f"Loading {len(plugin_ids)} plugins")
        loaded_plugin_metadata = []

        for plugin_id in plugin_ids:
            try:
                # Import the plugin module
                plugin_module_name = f"plugins.{plugin_id}.main"
                self.logger.debug(f"Importing plugin module: {plugin_module_name}")
                plugin_module = importlib.import_module(plugin_module_name)

                # Get the plugin class from the module
                plugin_class = getattr(plugin_module, "AtlasPlugin", None)
                if plugin_class is None:
                    self.logger.error(f"No AtlasPlugin class found in {plugin_module_name}")
                    continue

                # Create plugin instance
                plugin_instance = plugin_class(plugin_id)
                if not isinstance(plugin_instance, PluginInterface):
                    self.logger.error(f"Plugin {plugin_id} does not inherit from PluginInterface")
                    continue

                # Store plugin
                self.plugins[plugin_id] = plugin_instance
                self.logger.info(f"Loaded plugin: {plugin_id}")

                # Connect plugin status signal
                def create_status_handler(pid: str):
                    return lambda status: self.plugin_status_changed.emit(pid, status)

                plugin_instance.status_changed.connect(create_status_handler(plugin_id))

                # Get metadata
                metadata = plugin_instance.get_metadata()
                metadata["id"] = plugin_id
                loaded_plugin_metadata.append(metadata)

            except ImportError as e:
                self.logger.error(f"Failed to import plugin {plugin_id}: {str(e)}")
            except Exception as e:
                self.logger.error(f"Error loading plugin {plugin_id}: {str(e)}")

        self.plugins_loaded.emit(loaded_plugin_metadata)
        self.logger.info(f"Completed loading plugins. Total loaded: {len(self.plugins)}")

    def initialize_plugins(self) -> None:
        """Initialize all loaded plugins."""
        self.logger.info("Initializing all plugins")
        for plugin_id, plugin in self.plugins.items():
            try:
                if not plugin.initialize():
                    self.logger.error(f"Failed to initialize plugin: {plugin_id}")
            except Exception as e:
                self.logger.error(f"Error initializing plugin {plugin_id}: {str(e)}")
        self.logger.info("Completed initializing plugins")

    def shutdown_plugins(self) -> None:
        """Shut down all loaded plugins."""
        self.logger.info("Shutting down all plugins")
        for plugin_id, plugin in self.plugins.items():
            try:
                plugin.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down plugin {plugin_id}: {str(e)}")
        self.logger.info("Completed shutting down plugins")

    def get_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """Get a specific plugin by ID.

        Args:
            plugin_id (str): The ID of the plugin.

        Returns:
            Optional[PluginInterface]: The plugin instance or None if not found.
        """
        return self.plugins.get(plugin_id)

    def get_all_plugins(self) -> List[PluginInterface]:
        """Get a list of all loaded plugins.

        Returns:
            List[PluginInterface]: List of plugin instances.
        """
        return list(self.plugins.values())

    def get_plugin_metadata(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific plugin.

        Args:
            plugin_id (str): The ID of the plugin.

        Returns:
            Optional[Dict[str, Any]]: Metadata dictionary or None if plugin not found.
        """
        plugin = self.plugins.get(plugin_id)
        if plugin:
            metadata = plugin.get_metadata()
            metadata["id"] = plugin_id
            return metadata
        return None

    def get_all_plugin_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all loaded plugins.

        Returns:
            List[Dict[str, Any]]: List of metadata dictionaries for all plugins.
        """
        metadata_list = []
        for plugin_id, plugin in self.plugins.items():
            metadata = plugin.get_metadata()
            metadata["id"] = plugin_id
            metadata_list.append(metadata)
        return metadata_list

    @Slot(str, object)
    def broadcast_event(self, event_type: str, data: Any) -> None:
        """Broadcast an event to all active plugins.

        Args:
            event_type (str): Type of event.
            data (Any): Event data.
        """
        self.logger.debug(f"Broadcasting event {event_type} to plugins")
        for plugin_id, plugin in self.plugins.items():
            if plugin.is_active:
                try:
                    plugin.handle_event(event_type, data)
                except Exception as e:
                    self.logger.error(f"Error broadcasting event to plugin {plugin_id}: {str(e)}")
        self.logger.debug(f"Completed broadcasting event {event_type}")
