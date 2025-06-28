"""
Test cases for Atlas configuration system.
"""

import json
import os
import unittest
from unittest.mock import mock_open, patch

from jsonschema import ValidationError

from core.config import ConfigManager


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.test_config = {
            "environment": "test",
            "logging": {
                "level": "DEBUG",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "api": {"host": "localhost", "port": 5000},
        }
        self.test_schema = {
            "type": "object",
            "properties": {
                "environment": {"type": "string"},
                "logging": {
                    "type": "object",
                    "properties": {
                        "level": {"type": "string"},
                        "format": {"type": "string"},
                    },
                    "required": ["level", "format"],
                },
                "api": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer"},
                    },
                    "required": ["host", "port"],
                },
            },
            "required": ["environment", "logging", "api"],
        }

    @patch("core.config.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_get_config_default(self, mock_exists, mock_file):
        """Test loading default configuration."""
        # Mock file existence checks
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            self.test_config
        )

        config_manager = ConfigManager()
        config_manager._config = self.test_config
        # Set up test configuration
        config_manager._config = self.test_config
        config_manager._schema = self.test_schema

        # Test retrieving values
        self.assertEqual(config_manager.get("environment"), "test")
        self.assertEqual(config_manager.get("api.port"), 5000)
        self.assertEqual(config_manager.get("api.host"), "localhost")

    @patch("core.config.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_get_config_environment_override(self, mock_exists, mock_file):
        """Test environment variable overrides for configuration."""
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            self.test_config
        )

        with patch.dict(
            os.environ,
            {"ATLAS_API_PORT": "5001", "ATLAS_ENV": "production"},
            clear=True,
        ):
            config_manager = ConfigManager()
            config_manager._config = self.test_config.copy()  # Start with base config
            config_manager.apply_environment_overrides()  # Apply overrides
            self.assertEqual(config_manager._current_env, "production")
            self.assertEqual(config_manager.get("api.port"), 5001)

    @patch("core.config.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_get_config_missing_required(self, mock_exists, mock_file):
        """Test error handling for missing required configuration."""
        invalid_config = {
            "environment": "test",
            # Missing required 'logging' and 'api' sections
        }
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            invalid_config
        )

        config_manager = ConfigManager()
        with self.assertRaises(ValidationError):
            config_manager._config = invalid_config
            config_manager._schema = self.test_schema
            config_manager.validate_config()

    @patch("core.config.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_get_config_invalid_type(self, mock_exists, mock_file):
        """Test error handling for invalid configuration value types."""
        invalid_config = {
            "environment": "test",
            "logging": {
                "level": "DEBUG",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "api": {
                "host": "localhost",
                "port": "5000",  # Port should be integer, not string
            },
        }
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            invalid_config
        )

        config_manager = ConfigManager()
        with self.assertRaises(ValidationError):
            config_manager._config = invalid_config
            config_manager._schema = self.test_schema
            config_manager.validate_config()


if __name__ == "__main__":
    unittest.main()
