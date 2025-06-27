"""
Unified configuration management for Atlas.

This module provides a centralized way to manage application settings,
environment-based configurations, and validation.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from jsonschema import ValidationError, validate

# Logger for configuration operations
logger = logging.getLogger("Config")

# Default configuration paths
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config")
DEFAULT_CONFIG_PATH = os.path.join(CONFIG_DIR, "default.json")
SCHEMA_PATH = os.path.join(CONFIG_DIR, "schema.json")

# Environment variable prefix for overrides
ENV_PREFIX = "ATLAS_"


class ConfigManager:
    """Manages application configuration with support for environment-based settings and validation."""

    def __init__(self, env: Optional[str] = None):
        """Initialize the configuration manager."""
        self._config: Dict[str, Any] = {}
        self._schema: Dict[str, Any] = {}
        # Check ATLAS_ENV first, then parameter, then default to development
        self._current_env = os.getenv("ATLAS_ENV") or env or "development"
        self.load_config()
        self.apply_environment_overrides()
        self.validate_config()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        try:
            current = self._config
            for part in key.split("."):
                if not isinstance(current, dict):
                    return default
                current = current.get(part, default)
                if current == default:
                    return default
            return current
        except Exception as e:
            logger.error("Error getting config value for %s: %s", key, str(e))
            return default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        try:
            current = self._config
            parts = key.split(".")
            for _i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
            self.validate_config()
        except Exception as e:
            logger.error("Error setting config value for %s: %s", key, str(e))

    def save(self, environment: Optional[str] = None) -> bool:
        """Save the current configuration to file.

        Args:
            environment (str, optional): Environment name to save as. Defaults to current environment.

        Returns:
            bool: True if saved successfully, False otherwise.
        """
        try:
            env = environment or self._current_env
            config_path = os.path.join(CONFIG_DIR, f"{env}.json")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w") as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            logger.error("Error saving config: %s", e)
            return False

    def load_config(self) -> None:
        """Load configuration from files and environment variables."""
        self.load_schema()
        self.load_default_config()
        self.load_environment_config()

    def load_schema(self) -> None:
        """Load JSON schema for configuration validation."""
        try:
            if os.path.exists(SCHEMA_PATH):
                with open(SCHEMA_PATH, "r") as schema_file:
                    data = schema_file.read().strip()
                    if not data:
                        logger.error("Schema file is empty")
                        return
                    self._schema = json.loads(data)
                    logger.debug("Configuration schema loaded")
            else:
                logger.warning("Schema file not found: %s", SCHEMA_PATH)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in schema file: %s", e)
        except Exception as e:
            logger.error("Error loading schema: %s", e)

    def load_default_config(self) -> None:
        """Load default configuration settings."""
        try:
            if os.path.exists(DEFAULT_CONFIG_PATH):
                with open(DEFAULT_CONFIG_PATH, "r") as default_file:
                    data = default_file.read().strip()
                    if not data:
                        logger.error("Default config file is empty")
                        return
                    self._config = json.loads(data)
                    logger.debug("Default configuration loaded")
            else:
                logger.warning("Default config file not found: %s", DEFAULT_CONFIG_PATH)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in default config: %s", e)
        except Exception as e:
            logger.error("Error loading default config: %s", e)

    def _deep_merge(
        self, base: Dict[str, Any], update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        merged = base.copy()
        for key, value in update.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def load_environment_config(self) -> None:
        """Load environment-specific configuration."""
        try:
            env_config_path = os.path.join(CONFIG_DIR, f"{self._current_env}.json")
            if os.path.exists(env_config_path):
                with open(env_config_path, "r") as env_file:
                    env_config = json.load(env_file)
                    if not isinstance(env_config, dict):
                        logger.error("Environment config must be a JSON object")
                        return
                    self._config = self._deep_merge(self._config, env_config)
                    logger.debug("Environment configuration loaded")
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in environment config: %s", e)
        except Exception as e:
            logger.error("Error loading environment config: %s", e)

    def validate_config(self) -> None:
        """Validate the configuration against the schema."""
        try:
            if self._schema:
                validate(instance=self._config, schema=self._schema)
                logger.debug("Configuration validated successfully")
        except ValidationError as e:
            logger.error("Configuration validation failed: %s", e)
            raise

    def apply_environment_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        for key, value in os.environ.items():
            if not key.startswith(ENV_PREFIX):
                continue

            # Convert ATLAS_API_PORT to api.port
            config_key = key[len(ENV_PREFIX) :].lower().replace("_", ".")
            try:
                # Try to parse as JSON for complex types (lists, objects, numbers, booleans)
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                # If not valid JSON, use as string
                parsed_value = value

            # Set using the nested key support
            self.set(config_key, parsed_value)


# Singleton instance
_config_instance: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create the singleton ConfigManager instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value by key."""
    return get_config_manager().get(key, default)
