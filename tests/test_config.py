#!/usr/bin/env python3
"""
Tests for the Config core module.
"""

import json
import os
import tempfile
import unittest

from atlas.core.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary file for configuration
        self.temp_fd, self.temp_file = tempfile.mkstemp(suffix=".json")
        os.close(self.temp_fd)
        # Initialize Config with the temporary file path
        self.config = Config(config_path=self.temp_file)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        os.remove(self.temp_file)

    def test_initialization(self):
        """Test initialization of Config."""
        self.assertIsInstance(self.config, Config)

    def test_load(self):
        """Test load method."""
        config_data = {"key": "value"}
        with open(self.temp_file, "w") as f:
            json.dump(config_data, f)
        self.config.load()
        self.assertEqual(self.config.get("key"), "value")

    def test_save(self):
        """Test save method."""
        self.config.set("key", "value")
        self.config.save()
        with open(self.temp_file, "r") as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data.get("key"), "value")

    def test_get(self):
        """Test get method."""
        self.config.set("key", "value")
        result = self.config.get("key")
        self.assertEqual(result, "value")

    def test_get_default(self):
        """Test get method with default value."""
        result = self.config.get("nonexistent", default="default")
        self.assertEqual(result, "default")

    def test_set(self):
        """Test set method."""
        self.config.set("key", "value")
        self.assertEqual(self.config.get("key"), "value")


if __name__ == "__main__":
    unittest.main()
