"""
Unified configuration management for Atlas.

This module provides a centralized way to manage application settings,
environment-based configurations, and validation.
"""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass

class ConfigManager:
    """Manages application configuration settings."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager."""
        self._config: Dict[str, Any] = {}
        self._config_path = config_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'app_config.json')
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file or environment."""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r') as f:
                    self._config = json.load(f)
                    logger.info(f"Loaded configuration from {self._config_path}")
            else:
                logger.warning(f"Config file not found at {self._config_path}. Using environment defaults.")
                self._load_from_env()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise ConfigurationError(f"Invalid configuration format: {e}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        self._config = {
            "environment": os.getenv("ATLAS_ENV", "development"),
            "logging": {
                "level": os.getenv("ATLAS_LOG_LEVEL", "INFO")
            },
            "ui": {
                "theme": os.getenv("ATLAS_THEME", "dark")
            }
            # Add more environment-based configs as needed
        }
        logger.info("Loaded configuration from environment variables")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by key."""
        keys = key.split('.')
        current = self._config
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value
        logger.debug(f"Set configuration: {key} = {value}")

    def save(self) -> None:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Saved configuration to {self._config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise ConfigurationError(f"Failed to save configuration: {e}")

    def validate(self) -> bool:
        """Validate the current configuration."""
        required_keys = ["environment"]
        for key in required_keys:
            if key not in self._config:
                logger.error(f"Missing required configuration key: {key}")
                return False
        logger.info("Configuration validated successfully")
        return True

# Global configuration instance
CONFIG = ConfigManager()
