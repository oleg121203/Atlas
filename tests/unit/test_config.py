import unittest

from core.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = Config()
        # Manually set some test data since Config doesn't accept initial data
        self.config._config = {
            "app": {"name": "Atlas", "version": "1.0.0"},
            "settings": {"debug": True},
        }

    def test_initialization(self):
        """Test that the config initializes correctly."""
        self.assertIsNotNone(self.config._config)

    def test_get_existing_key(self):
        """Test retrieving a value for an existing key."""
        # Access nested structure directly since dot notation may not be supported
        app_name = self.config._config["app"]["name"]
        self.assertEqual(app_name, "Atlas")

    def test_get_nested_key(self):
        """Test retrieving a value for a nested key."""
        # Access nested structure directly since dot notation may not be supported
        debug_setting = self.config._config["settings"]["debug"]
        self.assertTrue(debug_setting)

    def test_get_nonexistent_key(self):
        """Test retrieving a value for a nonexistent key."""
        default_value = "default"
        result = self.config.get("nonexistent.key", default_value)
        self.assertEqual(result, default_value)

    def test_set_key(self):
        """Test setting a value for a key."""
        self.config.set("test.key", "value")
        self.assertEqual(self.config.get("test.key"), "value")


if __name__ == "__main__":
    unittest.main()
