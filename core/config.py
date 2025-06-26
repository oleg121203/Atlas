"""
Unified configuration management for Atlas.

This module provides a centralized way to manage application settings,
environment-based configurations, and validation.
"""
import os
import json
from typing import Optional, Any, Dict
import logging

from jsonschema import validate, ValidationError

# Logger for configuration operations
logger = logging.getLogger("Config")

# Default configuration paths
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config")
DEFAULT_CONFIG_PATH = os.path.join(CONFIG_DIR, "default.json")
SCHEMA_PATH = os.path.join(CONFIG_DIR, "schema.json")

# Environment variable prefix for overrides
ENV_PREFIX = "ATLAS_"

# Slack Integration
SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID", "")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET", "")
SLACK_REDIRECT_URI = os.getenv("SLACK_REDIRECT_URI", "http://localhost:5000/slack/callback")

class ConfigManager:
    """Manages application configuration with support for environment-based settings and validation."""
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._schema: Optional[Dict[str, Any]] = None
        self._current_env = os.environ.get(f"{ENV_PREFIX}ENV", "development")
        logger.info("ConfigManager initialized with environment: %s", self._current_env)

    def load_config(self) -> None:
        """Load configuration from files and environment variables."""
        try:
            # Load schema
            if os.path.exists(SCHEMA_PATH):
                with open(SCHEMA_PATH, "r") as schema_file:
                    self._schema = json.load(schema_file)
                logger.info("Configuration schema loaded")
            else:
                logger.warning("Schema file not found at %s", SCHEMA_PATH)

            # Load default configuration
            if os.path.exists(DEFAULT_CONFIG_PATH):
                with open(DEFAULT_CONFIG_PATH, "r") as default_file:
                    self._config = json.load(default_file)
                logger.info("Default configuration loaded")
            else:
                logger.warning("Default config file not found at %s", DEFAULT_CONFIG_PATH)
                self._config = {}

            # Load environment-specific configuration
            env_config_path = os.path.join(CONFIG_DIR, f"{self._current_env}.json")
            if os.path.exists(env_config_path):
                with open(env_config_path, "r") as env_file:
                    env_config = json.load(env_file)
                    self._deep_update(self._config, env_config)
                logger.info("Environment configuration loaded for %s", self._current_env)
            else:
                logger.warning("Environment config not found at %s", env_config_path)

            # Apply environment variable overrides
            self._apply_env_overrides()

            # Validate configuration
            if self._schema and not self.validate():
                logger.error("Configuration validation failed")
            else:
                logger.info("Configuration loaded and validated successfully")
        except Exception as e:
            logger.error("Error loading configuration: %s", str(e))

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        for key, value in os.environ.items():
            if key.startswith(ENV_PREFIX):
                config_key = key[len(ENV_PREFIX):].lower().replace("_", ".")
                try:
                    # Convert string values to appropriate types if possible
                    if value.lower() == "true":
                        config_value = True
                    elif value.lower() == "false":
                        config_value = False
                    elif value.isdigit():
                        config_value = int(value)
                    elif self._is_float(value):
                        config_value = float(value)
                    else:
                        config_value = value
                    self.set(config_key, config_value)
                    logger.info("Applied environment override for %s", config_key)
                except Exception as e:
                    logger.error("Failed to apply env override for %s: %s", key, str(e))

    def _is_float(self, value: str) -> bool:
        """Check if a string can be converted to float."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _deep_update(self, original: Dict, update: Dict) -> None:
        """Recursively update nested dictionaries."""
        for key, value in update.items():
            if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key (dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default if not found
        """
        try:
            current = self._config
            for part in key.split("."):
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return default
            return current if current is not None else default
        except Exception as e:
            logger.error("Error getting config value for %s: %s", key, str(e))
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (dot notation for nested keys)
            value: Value to set
        """
        try:
            # Check if the key is for sensitive data
            sensitive_keys = ["password", "secret", "key", "token"]
            if any(sk in key.lower() for sk in sensitive_keys):
                # Removed import of security functions to break circular dependency
                # encrypted_value = encrypt_data(str(value))
                # if encrypted_value:
                #     value = {"__encrypted__": encrypted_value}
                #     logger.info("Encrypted sensitive configuration data for key: %s", key)
                # else:
                #     logger.warning("Failed to encrypt sensitive data for key: %s", key)
                pass

            current = self._config
            parts = key.split(".")
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = value
            logger.debug("Set configuration value for %s", key)
        except Exception as e:
            logger.error("Error setting config value for %s: %s", key, str(e))

    def save(self, environment: Optional[str] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            environment: Environment to save config for, defaults to current
            
        Returns:
            bool: True if save successful
        """
        try:
            save_env = environment or self._current_env
            save_path = os.path.join(CONFIG_DIR, f"{save_env}.json")
            os.makedirs(CONFIG_DIR, exist_ok=True)
            
            # Create a copy of config without encrypted markers for saving
            save_config = self._prepare_config_for_save(self._config)
            
            with open(save_path, "w") as config_file:
                json.dump(save_config, config_file, indent=2)
            logger.info("Configuration saved to %s", save_path)
            return True
        except Exception as e:
            logger.error("Error saving configuration: %s", str(e))
            return False

    def _prepare_config_for_save(self, config: Dict) -> Dict:
        """
        Prepare configuration for saving by handling encrypted data markers.
        
        Args:
            config: Configuration dictionary to process
            
        Returns:
            Dict: Processed configuration dictionary
        """
        result = {}
        for key, value in config.items():
            if isinstance(value, dict):
                if "__encrypted__" in value:
                    result[key] = value  # Keep encrypted marker as is
                else:
                    result[key] = self._prepare_config_for_save(value)
            else:
                result[key] = value
        return result

    def validate(self) -> bool:
        """
        Validate the configuration against schema.
        
        Returns:
            bool: True if configuration is valid
        """
        if not self._schema:
            logger.warning("No schema available for validation")
            return True
        try:
            validate(instance=self._config, schema=self._schema)
            logger.info("Configuration validated successfully")
            return True
        except ValidationError as e:
            logger.error("Configuration validation failed: %s", str(e))
            return False

    def get_environment(self) -> str:
        """
        Get the current environment.
        
        Returns:
            str: Current environment name
        """
        return self._current_env

    def set_environment(self, environment: str) -> None:
        """
        Set the current environment and reload configuration.
        
        Args:
            environment: Environment name to set
        """
        self._current_env = environment
        logger.info("Environment set to %s, reloading configuration", environment)
        self.load_config()


def load_config() -> Dict[str, Any]:
    """Load configuration settings from environment or file.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    config = {
        'feature_flags': {
            'experimental_ui': False,
            'voice_commands': True,
            'hotkey_support': True
        }
    }
    
    config_file_path = os.getenv('ATLAS_CONFIG_PATH', 'config.json')
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r') as config_file:
                file_config = json.load(config_file)
                config.update(file_config)
        except Exception as e:
            print(f"Error loading config from file: {e}")
    
    return config

def get_config() -> Dict[str, Any]:
    """Get the application configuration.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    return load_config()

def get_config_manager() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        ConfigManager: Configuration manager instance
    """
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager()
        _global_config.load_config()
    return _global_config

_global_config = None
