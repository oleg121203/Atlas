"""
Test cases for Atlas configuration system.
"""

import json
import os
import unittest
from typing import Any, Dict
from unittest.mock import mock_open, patch

from core.config import CONFIG_DIR, ConfigManager


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.test_config: Dict[str, Any] = {
            "environment": "test",
            "logging": {
                "level": "DEBUG",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "api": {"host": "localhost", "port": 5000},
        }

    @patch("core.config.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_config_initialization(self, mock_exists, mock_file):
        """Test configuration manager initialization."""
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            self.test_config
        )

        config_manager = ConfigManager()
        self.assertIsNotNone(config_manager)
        self.assertEqual(config_manager._current_env, "development")

    @patch("core.config.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_load_config(self, mock_exists, mock_file):
        """Test loading configuration from file."""
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            self.test_config
        )

        config_manager = ConfigManager()
        config_manager.load_config()

        self.assertEqual(config_manager.get("environment"), "test")
        self.assertEqual(config_manager.get("logging.level"), "DEBUG")
        self.assertEqual(config_manager.get("api.port"), 5000)

    @patch("core.config.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_environment_overrides(self, mock_makedirs, mock_exists, mock_file):
        """Test environment variable overrides."""
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
            config_manager._config = self.test_config.copy()
            config_manager.apply_environment_overrides()

            self.assertEqual(config_manager._current_env, "production")
            self.assertEqual(config_manager.get("api.port"), 5001)

    @patch("os.makedirs")
    @patch("core.config.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_save_config(self, mock_exists, mock_file, mock_makedirs):
        """Test saving configuration to file."""
        mock_exists.return_value = True  # Make sure file "exists" for initial loads

        # Create a new ConfigManager with minimal mocked setup
        config_manager = ConfigManager()
        config_manager._config = self.test_config
        config_manager._schema = {}  # Empty schema for this test

        # Test save
        success = config_manager.save()
        self.assertTrue(success)

        # Verify the directory was created
        mock_makedirs.assert_called_once_with(
            os.path.dirname(os.path.join(CONFIG_DIR, "development.json")), exist_ok=True
        )

        # Verify a file was opened for writing
        write_call = None
        for call in mock_file.call_args_list:
            args, kwargs = call
            if (
                args
                and args[0].endswith("development.json")
                and "w" in (args[1] if len(args) > 1 else kwargs.get("mode", ""))
            ):
                write_call = call
                break

        self.assertIsNotNone(write_call, "No write call found for saving config")


if __name__ == "__main__":
    unittest.main()
