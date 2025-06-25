"""
Plugin Configuration System for Atlas

This module provides a configuration system for plugins in the Atlas system.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

import logging

logger = logging.getLogger(__name__)

class PluginConfigManager:
    """Manages configuration for plugins in Atlas."""
    
    def __init__(self, config_dir: str = "config/plugins"):
        """Initialize the plugin configuration manager.
        
        Args:
            config_dir: Directory where plugin configurations are stored.
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.configs: Dict[str, Dict[str, Any]] = {}
        logger.info("Plugin configuration manager initialized")

    def load_config(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Load configuration for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to load configuration for.
        
        Returns:
            Configuration dictionary if found, None otherwise.
        """
        config_file = self.config_dir / f"{plugin_name}.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.configs[plugin_name] = config
                    logger.info(f"Loaded configuration for plugin: {plugin_name}")
                    return config
            except Exception as e:
                logger.error(f"Error loading configuration for plugin {plugin_name}: {e}")
                return None
        return None

    def save_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Save configuration for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to save configuration for.
            config: Configuration dictionary to save.
        
        Returns:
            True if save is successful, False otherwise.
        """
        config_file = self.config_dir / f"{plugin_name}.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            self.configs[plugin_name] = config
            logger.info(f"Saved configuration for plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration for plugin {plugin_name}: {e}")
            return False

    def get_config(self, plugin_name: str, default_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get configuration for a plugin, loading from file if necessary.
        
        Args:
            plugin_name: Name of the plugin to get configuration for.
            default_config: Default configuration to use if no config is found.
        
        Returns:
            Configuration dictionary for the plugin.
        """
        if plugin_name not in self.configs:
            config = self.load_config(plugin_name)
            if config is None and default_config is not None:
                self.configs[plugin_name] = default_config
                self.save_config(plugin_name, default_config)
            elif config is None:
                self.configs[plugin_name] = {}
        return self.configs[plugin_name]

    def update_config(self, plugin_name: str, updates: Dict[str, Any]) -> bool:
        """Update specific values in a plugin's configuration.
        
        Args:
            plugin_name: Name of the plugin to update configuration for.
            updates: Dictionary with updated values to merge into existing config.
        
        Returns:
            True if update and save are successful, False otherwise.
        """
        config = self.get_config(plugin_name)
        config.update(updates)
        return self.save_config(plugin_name, config)

    def load_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load configurations for all plugins in the config directory.
        
        Returns:
            Dictionary of plugin names to their configurations.
        """
        configs = {}
        for config_file in self.config_dir.glob("*.json"):
            plugin_name = config_file.stem
            config = self.load_config(plugin_name)
            if config is not None:
                configs[plugin_name] = config
        return configs
