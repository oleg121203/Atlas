"""
Unified configuration management for Atlas.

This module provides a centralized way to manage application settings,
environment-based configurations, and validation.
"""

import logging
import os
from typing import Any, Dict, Optional

# Logger for configuration operations
logger = logging.getLogger("Config")


class Config:
    """
    Simplified configuration management for Atlas.

    This class provides basic configuration loading and access
    with environment variable support.
    """

    def __init__(self):
        """Initialize the configuration manager."""
        self._config: Dict[str, Any] = {}
        self._loaded = False

    def load(self):
        """Load configuration from environment and defaults."""
        if self._loaded:
            return

        # Default configuration
        self._config = {
            "app": {
                "name": "Atlas",
                "version": "1.0.0",
                "debug": os.getenv("ATLAS_DEBUG", "false").lower() == "true",
            },
            "ui": {
                "theme": os.getenv("ATLAS_THEME", "dark"),
                "window_size": {
                    "width": int(os.getenv("ATLAS_WINDOW_WIDTH", "1200")),
                    "height": int(os.getenv("ATLAS_WINDOW_HEIGHT", "800")),
                },
            },
            "plugins": {
                "directory": os.getenv("ATLAS_PLUGIN_DIR", "plugins"),
                "auto_load": os.getenv("ATLAS_AUTO_LOAD_PLUGINS", "true").lower()
                == "true",
            },
            "logging": {
                "level": os.getenv("ATLAS_LOG_LEVEL", "INFO"),
                "file": os.getenv("ATLAS_LOG_FILE", "atlas.log"),
            },
        }

        self._loaded = True
        logger.info("Configuration loaded successfully")

    def save(self):
        """Save configuration (placeholder for future implementation)."""
        logger.info("Configuration save requested (not implemented)")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-separated key.

        Args:
            key: Dot-separated key (e.g., 'app.name', 'ui.theme')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if not self._loaded:
            self.load()

        current = self._config
        for part in key.split("."):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def set(self, key: str, value: Any):
        """
        Set a configuration value by dot-separated key.

        Args:
            key: Dot-separated key
            value: Value to set
        """
        if not self._loaded:
            self.load()

        current = self._config
        parts = key.split(".")

        # Navigate to the parent of the target key
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set the final value
        current[parts[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary."""
        if not self._loaded:
            self.load()
        return self._config.copy()


# Legacy ConfigManager class for backward compatibility
class ConfigManager(Config):
    """Legacy ConfigManager for backward compatibility."""

    def __init__(self, env: Optional[str] = None):
        """Initialize with environment parameter for compatibility."""
        super().__init__()
        self._current_env = env or "development"


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
