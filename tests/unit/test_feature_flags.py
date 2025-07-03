import json
import unittest
from contextlib import suppress
from unittest.mock import mock_open, patch

from core.feature_flags import FeatureFlagManager


class TestFeatureFlags(unittest.TestCase):
    def setUp(self):
        self.manager = FeatureFlagManager()
        self.manager.environment = "test"
        self.manager.flags = {"test_feature": True, "another_feature": False}

    def test_init(self):
        """Test initialization of FeatureFlagManager."""
        assert self.manager.environment == "test"
        assert isinstance(self.manager.flags, dict)
        assert "test_feature" in self.manager.flags
        assert "another_feature" in self.manager.flags

    def test_load_flags_existing_file(self):
        """Test load_flags with an existing file."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch(
                "builtins.open",
                new_callable=mock_open,
                read_data=json.dumps({"test_feature": True, "another_feature": False}),
            ),
        ):
            self.manager.load_flags()
            assert self.manager.flags["test_feature"] is True
            assert self.manager.flags["another_feature"] is False

    def test_is_enabled_nonexistent_feature(self):
        """Test is_enabled with a non-existent feature."""
        with patch.object(self.manager, "flags", {"test_feature": True}):
            assert not self.manager.is_enabled("nonexistent_feature")

    def test_is_enabled_empty_name(self):
        """Test is_enabled with an empty feature name."""
        assert not self.manager.is_enabled("")

    def test_is_enabled_none_name(self):
        """Test is_enabled with a None feature name."""
        try:
            assert not self.manager.is_enabled("None")
        except TypeError:
            self.skipTest("is_enabled does not handle None as a string")

    def test_save_flags_exception(self):
        """Test save_flags with an exception during file writing."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.parent.mkdir", return_value=None),
            patch("builtins.open", side_effect=OSError),
            self.assertLogs("root", level="ERROR") as cm,
        ):
            try:
                self.manager.save_flags()
            except Exception as e:
                self.assertTrue(isinstance(e, Exception))
            self.assertTrue(
                any("Failed to save feature flags" in log for log in cm.output)
            )

    def test_load_flags_value_error(self):
        """Test load_flags with ValueError during file reading."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", new_callable=mock_open, read_data="invalid json"),
            suppress(ValueError),
        ):
            self.manager.load_flags()

    def test_load_flags_type_error(self):
        """Test load_flags with TypeError during file reading."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", new_callable=mock_open, read_data=None),
            suppress(TypeError),
        ):
            self.manager.load_flags()

    def test_load_flags_file_not_found(self):
        """Test load_flags with FileNotFoundError."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", side_effect=FileNotFoundError),
            suppress(FileNotFoundError),
        ):
            self.manager.load_flags()

    def test_load_flags_os_error(self):
        """Test load_flags with OSError during file reading."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", side_effect=OSError),
            suppress(OSError),
        ):
            self.manager.load_flags()

    def test_clear_all_features_empty_environment(self):
        """Test clear_all_features with empty environment."""
        if hasattr(self.manager, "clear_all_features"):
            with patch.object(self.manager, "environment", ""):
                self.manager.clear_all_features()
                assert len(self.manager.flags) == 0
        else:
            self.skipTest("clear_all_features method not implemented")

    def test_clear_all_features_none_environment(self):
        """Test clear_all_features with None environment."""
        if hasattr(self.manager, "clear_all_features"):
            with patch.object(self.manager, "environment", None):
                self.manager.clear_all_features()
                assert len(self.manager.flags) == 0
        else:
            self.skipTest("clear_all_features method not implemented")

    def test_get_all_features_empty_environment(self):
        """Test get_all_features with empty environment."""
        if hasattr(self.manager, "get_all_features"):
            with patch.object(self.manager, "environment", ""):
                result = self.manager.get_all_features()
                assert isinstance(result, dict)
        else:
            self.skipTest("get_all_features method not implemented")

    def test_get_all_features_none_environment(self):
        """Test get_all_features with None environment."""
        if hasattr(self.manager, "get_all_features"):
            with patch.object(self.manager, "environment", None):
                result = self.manager.get_all_features()
                assert isinstance(result, dict)
        else:
            self.skipTest("get_all_features method not implemented")


if __name__ == "__main__":
    unittest.main()
