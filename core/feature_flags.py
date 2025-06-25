"""
Feature Flag Management System for Atlas

This module provides a system for managing feature flags in the Atlas application,
allowing for controlled rollout of features and easy toggling of functionality.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
import logging

from core.logging import get_logger
from core.config import load_config

# Set up logging
logger = get_logger("FeatureFlags")

class FeatureFlagError(Exception):
    """Custom exception for feature flag errors."""
    pass

class FeatureFlagManager:
    """Manages feature flags for the Atlas application."""
    
    _instance = None
    
    def __new__(cls, config_path: Optional[str] = None, environment: str = "dev"):
        """
        Singleton pattern to ensure only one instance of FeatureFlagManager exists.
        
        Args:
            config_path: Path to configuration file, if any
            environment: Target environment for feature flags
        
        Returns:
            FeatureFlagManager: Singleton instance of the manager
        """
        if cls._instance is None:
            cls._instance = super(FeatureFlagManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None, environment: str = "dev"):
        """
        Initialize the FeatureFlagManager with configuration and environment.
        
        Args:
            config_path: Path to configuration file, if any
            environment: Target environment for feature flags (dev, staging, prod)
        """
        if not hasattr(self, '_initialized') or not self._initialized:
            self.environment = environment.lower()
            self.config = load_config(config_path, environment=self.environment)
            self.flags: Dict[str, Any] = {}
            self.default_flags: Dict[str, Any] = self.config.get("feature_flags", {})
            self.storage_path = Path(self.config.get("feature_flags_storage", "config/feature_flags.json"))
            self.setup_logging()
            self.load_flags()
            self._initialized = True
            logger.info("FeatureFlagManager initialized for environment: %s", self.environment)
    
    def setup_logging(self) -> None:
        """Set up logging configuration for feature flag management."""
        log_level = self.config.get("logging", {}).get("level", "INFO")
        log_file = self.config.get("logging", {}).get("file", "atlas_feature_flags.log")
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        logger.info("Logging configured for FeatureFlagManager")
    
    def load_flags(self) -> None:
        """Load feature flags from storage or use default flags from config."""
        logger.info("Loading feature flags")
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r") as f:
                    stored_flags = json.load(f)
                    # Merge stored flags with defaults, giving precedence to stored
                    self.flags = {**self.default_flags, **stored_flags}
                    logger.info("Loaded feature flags from storage: %s", self.storage_path)
            else:
                # If no storage file exists, use the defaults from config
                self.flags = self.default_flags.copy()
                logger.info("No stored flags found, using default feature flags")
            
            # Apply environment-specific overrides if they exist
            env_overrides = self.config.get("feature_flag_overrides", {}).get(self.environment, {})
            if env_overrides:
                self.flags.update(env_overrides)
                logger.info("Applied environment-specific overrides for: %s", self.environment)
        except Exception as e:
            logger.error("Error loading feature flags: %s", str(e), exc_info=True)
            # Fall back to default flags on error
            self.flags = self.default_flags.copy()
            logger.info("Falling back to default feature flags due to load error")
    
    def save_flags(self) -> None:
        """Save current feature flags to storage."""
        logger.info("Saving feature flags to storage: %s", self.storage_path)
        try:
            # Ensure storage directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, "w") as f:
                json.dump(self.flags, f, indent=2)
            logger.info("Feature flags saved successfully")
        except Exception as e:
            logger.error("Error saving feature flags: %s", str(e), exc_info=True)
            raise FeatureFlagError(f"Failed to save feature flags: {str(e)}")
    
    def is_enabled(self, flag_name: str, default: bool = False) -> bool:
        """
        Check if a feature flag is enabled.
        
        Args:
            flag_name: Name of the feature flag to check
            default: Default value if the flag is not found
        
        Returns:
            bool: True if the feature is enabled, False otherwise
        """
        result = self.flags.get(flag_name, default)
        logger.debug("Checking feature flag %s: %s", flag_name, result)
        return bool(result)
    
    def get_flag_value(self, flag_name: str, default: Any = None) -> Any:
        """
        Get the value of a feature flag.
        
        Args:
            flag_name: Name of the feature flag to retrieve
            default: Default value if the flag is not found
        
        Returns:
            Any: Value of the feature flag or the default if not found
        """
        result = self.flags.get(flag_name, default)
        logger.debug("Getting feature flag value %s: %s", flag_name, result)
        return result
    
    def set_flag(self, flag_name: str, value: Any) -> None:
        """
        Set the value of a feature flag and save to storage.
        
        Args:
            flag_name: Name of the feature flag to set
            value: Value to set for the feature flag
        """
        logger.info("Setting feature flag %s to: %s", flag_name, value)
        self.flags[flag_name] = value
        self.save_flags()
    
    def enable_feature(self, flag_name: str) -> None:
        """
        Enable a specific feature flag.
        
        Args:
            flag_name: Name of the feature flag to enable
        """
        self.set_flag(flag_name, True)
        logger.info("Enabled feature: %s", flag_name)
    
    def disable_feature(self, flag_name: str) -> None:
        """
        Disable a specific feature flag.
        
        Args:
            flag_name: Name of the feature flag to disable
        """
        self.set_flag(flag_name, False)
        logger.info("Disabled feature: %s", flag_name)
    
    def reset_to_defaults(self) -> None:
        """Reset all feature flags to their default values."""
        logger.info("Resetting feature flags to defaults")
        self.flags = self.default_flags.copy()
        self.save_flags()
    
    def list_flags(self) -> Dict[str, Any]:
        """
        Get a dictionary of all feature flags and their current values.
        
        Returns:
            Dict[str, Any]: Dictionary of feature flags and their values
        """
        logger.debug("Listing all feature flags")
        return self.flags.copy()

# Global function to get the feature flag manager instance
def get_feature_flag_manager(config_path: Optional[str] = None, environment: str = "dev") -> FeatureFlagManager:
    """
    Get the singleton instance of the FeatureFlagManager.
    
    Args:
        config_path: Path to configuration file, if any
        environment: Target environment for feature flags
    
    Returns:
        FeatureFlagManager: Singleton instance of the feature flag manager
    """
    return FeatureFlagManager(config_path=config_path, environment=environment)

# Convenience functions for easy access to feature flags
def is_feature_enabled(flag_name: str, default: bool = False, config_path: Optional[str] = None, environment: str = "dev") -> bool:
    """
    Check if a feature is enabled.
    
    Args:
        flag_name: Name of the feature flag to check
        default: Default value if the flag is not found
        config_path: Path to configuration file, if any
        environment: Target environment for feature flags
    
    Returns:
        bool: True if the feature is enabled, False otherwise
    """
    return get_feature_flag_manager(config_path, environment).is_enabled(flag_name, default)

def get_feature_value(flag_name: str, default: Any = None, config_path: Optional[str] = None, environment: str = "dev") -> Any:
    """
    Get the value of a feature flag.
    
    Args:
        flag_name: Name of the feature flag to retrieve
        default: Default value if the flag is not found
        config_path: Path to configuration file, if any
        environment: Target environment for feature flags
    
    Returns:
        Any: Value of the feature flag or the default if not found
    """
    return get_feature_flag_manager(config_path, environment).get_flag_value(flag_name, default)
