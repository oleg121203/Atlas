# Standard library imports
import os
import sys
import tempfile
import unittest

# Third-party imports
# Local application imports
from core.config import Config


class TestConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configure path before any tests run."""
        if ".." not in sys.path:
            sys.path.append("..")

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = Config()
        # Reset config to empty for clean test state
        self.config._config = {}
        # Set test data using set method to ensure nested structure
        self.config.set("app.name", "Atlas")
        self.config.set("app.version", "1.0.0")
        self.config.set("settings.debug", True)
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")

    def test_initialization(self):
        """Test that the config initializes correctly."""
        self.assertIsNotNone(self.config._config)

    def test_get_existing_key(self):
        """Test retrieving a value for an existing key."""
        app_name = self.config.get("app.name")
        self.assertEqual(app_name, "Atlas")

    def test_get_nested_key(self):
        """Test retrieving a value for a nested key."""
        debug_setting = self.config.get("settings.debug")
        self.assertEqual(debug_setting, True)

    def test_get_nonexistent_key(self):
        """Test retrieving a value for a nonexistent key."""
        default_value = "default"
        result = self.config.get("nonexistent.key", default_value)
        self.assertEqual(result, default_value)

    def test_set_key(self):
        """Test setting a value for a key."""
        self.config.set("test.key", "value")
        self.assertEqual(self.config.get("test.key"), "value")

    def test_set_nested_key(self):
        """Test setting a value for a nested key."""
        self.config.set("test.nested.key", "nested_value")
        self.assertEqual(self.config.get("test.nested.key"), "nested_value")


if __name__ == "__main__":
    unittest.main()
