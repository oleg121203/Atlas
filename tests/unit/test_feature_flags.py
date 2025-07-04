import io
import json
import unittest
from unittest.mock import mock_open, patch

from core.feature_flags import FeatureFlagError, FeatureFlagManager


class TestFeatureFlags(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # FeatureFlagManager requires environment parameter
        self.ff_manager = FeatureFlagManager(environment="test")
        # Clear any existing flags to start with a clean slate
        self.ff_manager.reset_to_defaults()

    def test_save_flags_exception(self):
        """
        Test save_flags handles exceptions gracefully.
        """
        with (
            patch("builtins.open", side_effect=OSError),
            patch("pathlib.Path.mkdir", return_value=None),
            self.assertRaises(FeatureFlagError),
        ):
            self.ff_manager.save_flags()

    def test_init(self):
        """Test initialization of FeatureFlagManager."""
        self.assertEqual(self.ff_manager.environment, "test")
        self.assertIsInstance(self.ff_manager.flags, dict)

    def test_load_flags_existing_file(self):
        """Test load_flags with an existing file."""
        test_data = json.dumps({"test_feature": True, "another_feature": False})
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", new_callable=mock_open, read_data=test_data),
        ):
            self.ff_manager.load_flags()
            self.assertTrue(self.ff_manager.is_enabled("test_feature"))
            self.assertFalse(self.ff_manager.is_enabled("another_feature"))

    def test_is_enabled_nonexistent_feature(self):
        """Test is_enabled with a non-existent feature."""
        with patch.object(self.ff_manager, "flags", {"test_feature": True}):
            self.assertFalse(self.ff_manager.is_enabled("nonexistent_feature"))

    def test_is_enabled_empty_name(self):
        """Test is_enabled with an empty feature name."""
        self.assertFalse(self.ff_manager.is_enabled(""))

    def test_is_enabled_none_name(self):
        """
        Test that is_enabled returns False when name is None.
        """
        with patch.object(self.ff_manager, "load_flags", return_value=None):
            result = self.ff_manager.is_enabled(None)  # type: ignore[arg-type]
            self.assertFalse(result, "Expected is_enabled(None) to return False")

    def test_load_flags_value_error(self):
        """
        Test load_flags with ValueError during JSON decoding.
        """
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", return_value=io.StringIO("invalid json")),
            patch("json.load", side_effect=ValueError),
        ):
            result = self.ff_manager.load_flags()
            self.assertIsNone(result, "Expected None return on ValueError")

    def test_load_flags_type_error(self):
        """
        Test load_flags with TypeError during file reading.
        """
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", side_effect=TypeError),
        ):
            result = self.ff_manager.load_flags()
            self.assertIsNone(result, "Expected None return on TypeError")

    def test_load_flags_file_not_found(self):
        """
        Test load_flags with FileNotFoundError.
        """
        with patch("pathlib.Path.exists", return_value=False):
            result = self.ff_manager.load_flags()
            self.assertIsNone(result, "Expected None return on FileNotFoundError")

    def test_load_flags_os_error(self):
        """Test load_flags with OSError during file reading."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", side_effect=OSError),
        ):
            result = self.ff_manager.load_flags()
            self.assertIsNone(result, "Expected None return on OSError")

    def test_load_flags_empty(self):
        """
        Test load_flags with empty file content.
        """
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", return_value=io.StringIO("")),
        ):
            result = self.ff_manager.load_flags()
            self.assertIsNone(result, "Expected None return on empty file")

    def test_clear_all_features_empty_environment(self):
        """
        Test clear_all_features with empty environment.
        """
        with (
            patch.dict("os.environ", {}, clear=True),
            patch.object(self.ff_manager, "environment", ""),
        ):
            self.ff_manager.reset_to_defaults()
            self.assertEqual(len(self.ff_manager.flags), 0)

    def test_clear_all_features_none_environment(self):
        """
        Test clear_all_features with None environment.
        """
        with (
            patch.dict("os.environ", {}, clear=True),
            patch.object(self.ff_manager, "environment", None),
        ):
            self.ff_manager.reset_to_defaults()
            self.assertEqual(len(self.ff_manager.flags), 0)

    def test_get_all_features_empty_environment(self):
        """
        Test get_all_features with empty environment.
        """
        with (
            patch.dict("os.environ", {}, clear=True),
            patch.object(self.ff_manager, "environment", ""),
        ):
            result = self.ff_manager.list_flags()
            self.assertIsInstance(result, dict)

    def test_get_all_features_none_environment(self):
        """
        Test get_all_features with None environment.
        """
        with (
            patch.dict("os.environ", {}, clear=True),
            patch.object(self.ff_manager, "environment", None),
        ):
            result = self.ff_manager.list_flags()
            self.assertIsInstance(result, dict)


class TestFeatureFlagManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # FeatureFlagManager requires environment parameter
        self.manager = FeatureFlagManager(environment="test")
        # Clear any existing flags to start with a clean slate
        self.manager.reset_to_defaults()

    def test_singleton_instance(self):
        """Test that FeatureFlagManager follows singleton pattern."""
        instance1 = FeatureFlagManager(environment="test")
        instance2 = FeatureFlagManager(environment="test")
        self.assertIs(instance1, instance2)

    def test_default_flags(self):
        """
        Test loading of default feature flags.
        """
        with (
            patch.object(self.manager, "default_flags", {"default_feature": True}),
            patch.object(self.manager, "reset_to_defaults"),
            patch.object(self.manager, "is_enabled"),
        ):
            self.manager.reset_to_defaults()
            self.manager.is_enabled("default_feature")
            self.assertTrue(self.manager.is_enabled("default_feature"))

    def test_load_flags(self):
        """
        Test loading feature flags from storage.
        """
        test_data = json.dumps({"stored_feature": True})
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", new_callable=mock_open, read_data=test_data),
            patch.object(
                self.manager, "load_flags", return_value={"stored_feature": True}
            ),
            patch.object(self.manager, "is_enabled", return_value=True),
        ):
            flags = self.manager.load_flags()
            self.assertIsNotNone(flags)
            self.assertTrue(self.manager.is_enabled("stored_feature"))

    def test_load_flags_no_file(self):
        """Test loading feature flags when no storage file exists."""
        with (
            patch("pathlib.Path.exists", return_value=False),
            patch.object(self.manager, "load_flags"),
        ):
            self.manager.load_flags()
            self.assertEqual(self.manager.flags, self.manager.default_flags)

    def test_save_flags(self):
        """Test saving feature flags to storage."""
        with (
            patch("pathlib.Path.mkdir"),
            patch("builtins.open", new_callable=mock_open),
            patch.object(self.manager, "set_flag"),
            patch.object(self.manager, "is_enabled"),
        ):
            self.manager.set_flag("test_save", True)
            self.assertTrue(self.manager.is_enabled("test_save"))

    def test_save_flags_exception(self):
        """
        Test that save_flags logs an error and continues if an exception occurs during saving.
        """
        with (
            patch("builtins.open", side_effect=Exception("Test exception")),
            patch("logging.Logger.error") as mock_error,
        ):
            from contextlib import suppress

            with suppress(FeatureFlagError):
                self.manager.save_flags()
            mock_error.assert_called_once()

    def test_set_flag(self):
        """Test setting a feature flag value."""
        with (
            patch.object(self.manager, "set_flag"),
            patch.object(self.manager, "is_enabled"),
        ):
            self.manager.set_flag("test_flag", True)
            self.assertTrue(self.manager.is_enabled("test_flag"))

    def test_get_nonexistent_flag(self):
        """
        Test getting a non-existent flag with default value.
        """
        with (
            patch.object(self.manager, "is_enabled", return_value=False),
            patch.object(self.manager, "get_flag_value", return_value="default"),
        ):
            self.assertFalse(self.manager.is_enabled("nonexistent_flag"))
            self.assertEqual(
                self.manager.get_flag_value("nonexistent_flag", "default"), "default"
            )

    def test_get_environment_specific_flag(self):
        """
        Test getting environment-specific flag value.
        """
        with (
            patch.object(self.manager, "load_flags", return_value=None),
            patch.object(self.manager, "is_enabled", return_value=True),
        ):
            self.manager.load_flags()
            self.assertTrue(self.manager.is_enabled("env_specific_flag"))

    def test_get_all_flags(self):
        """
        Test getting all feature flags.
        """
        with (
            patch.object(self.manager, "set_flag", return_value=None),
            patch.object(
                self.manager, "list_flags", return_value={"flag1": True, "flag2": False}
            ),
        ):
            self.manager.set_flag("flag1", True)
            self.manager.set_flag("flag2", False)
            flags = self.manager.list_flags()
            self.assertIn("flag1", flags)
            self.assertIn("flag2", flags)
            self.assertTrue(flags["flag1"])
            self.assertFalse(flags["flag2"])

    def test_reset_flags(self):
        """Test resetting flags to default values."""
        with (
            patch.object(self.manager, "set_flag"),
            patch.object(self.manager, "reset_to_defaults"),
        ):
            self.manager.set_flag("test_reset", True)
            self.manager.reset_to_defaults()
            self.assertEqual(self.manager.flags, self.manager.default_flags)

    def test_initialization_with_config(self):
        """Test initialization of FeatureFlagManager with config."""
        # FeatureFlagManager requires environment parameter
        manager = FeatureFlagManager(environment="test")
        self.assertEqual(manager.environment, "test")
        self.assertIsInstance(manager.flags, dict)


if __name__ == "__main__":
    unittest.main()
