# plugin_validation_test.py

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from modules.agents.plugin_manager import PluginManager
from PySide6.QtWidgets import QApplication

# Adjust the system path to include the project root directory for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Project root added to sys.path: {project_root}")
print(f"Current sys.path: {sys.path}")


class PluginValidationTest(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = (
            QApplication([]) if not QApplication.instance() else QApplication.instance()
        )
        self.plugin_dir = os.path.join(project_root, "tests", "test_plugins")
        self.agent_manager = MagicMock()
        self.plugin_manager = PluginManager(
            agent_manager=self.agent_manager, plugin_dir=self.plugin_dir
        )

    def tearDown(self):
        """Clean up after each test method."""
        pass

    def test_plugin_metadata_validation(self):
        """Test that plugin metadata adheres to required format and content."""
        # Mock a plugin with valid metadata
        valid_plugin = {
            "metadata": {
                "name": "ValidPlugin",
                "version": "1.0.0",
                "description": "A valid test plugin",
                "author": "Test Author",
                "dependencies": {},
            }
        }
        self.plugin_manager.plugins["ValidPlugin"] = valid_plugin

        # Mock a plugin with invalid metadata (missing required fields)
        invalid_plugin = {
            "metadata": {
                "name": "InvalidPlugin"
                # Missing version, description, etc.
            }
        }
        self.plugin_manager.plugins["InvalidPlugin"] = invalid_plugin

        # Validate metadata
        with patch.object(
            self.plugin_manager,
            "get_all_plugins",
            return_value=self.plugin_manager.plugins,
        ):
            valid_result = self.plugin_manager._validate_metadata("ValidPlugin")
            invalid_result = self.plugin_manager._validate_metadata("InvalidPlugin")

            self.assertTrue(
                valid_result["valid"], "Valid plugin metadata should pass validation"
            )
            self.assertFalse(
                invalid_result["valid"],
                "Invalid plugin metadata should fail validation",
            )
            self.assertIn(
                "missing required fields",
                invalid_result["reason"].lower(),
                "Validation failure reason should mention missing fields",
            )

    def test_plugin_security_scan(self):
        """Test scanning plugins for potential security issues."""
        # Mock a plugin with safe code
        safe_plugin = {
            "metadata": {"name": "SafePlugin", "version": "1.0.0"},
            "module": MagicMock(__file__="/path/to/safe_plugin.py"),
        }
        # Mock a plugin with potentially unsafe code (e.g., use of eval)
        unsafe_plugin = {
            "metadata": {"name": "UnsafePlugin", "version": "1.0.0"},
            "module": MagicMock(__file__="/path/to/unsafe_plugin.py"),
        }

        self.plugin_manager.plugins["SafePlugin"] = safe_plugin
        self.plugin_manager.plugins["UnsafePlugin"] = unsafe_plugin

        # Mock file content reading for security scan
        with patch(
            "builtins.open",
            side_effect=[
                unittest.mock.mock_open(
                    read_data="def safe_function(): pass"
                ).return_value,
                unittest.mock.mock_open(
                    read_data="def unsafe_function(): eval('malicious code')"
                ).return_value,
            ],
        ):
            safe_result = self.plugin_manager._scan_for_security_issues("SafePlugin")
            unsafe_result = self.plugin_manager._scan_for_security_issues(
                "UnsafePlugin"
            )

            self.assertTrue(
                safe_result["safe"], "Safe plugin should pass security scan"
            )
            self.assertFalse(
                unsafe_result["safe"], "Unsafe plugin should fail security scan"
            )
            self.assertIn(
                "eval",
                unsafe_result["issues"][0].lower(),
                "Security scan should flag use of eval as an issue",
            )

    def test_plugin_dependency_validation(self):
        """Test validation of plugin dependencies for conflicts and availability."""
        # Mock plugins with dependency data
        self.plugin_manager.plugins = {
            "PluginA": {
                "metadata": {
                    "name": "PluginA",
                    "version": "1.0.0",
                    "dependencies": {"PluginB": ">=1.0.0"},
                }
            },
            "PluginB": {
                "metadata": {"name": "PluginB", "version": "1.1.0", "dependencies": {}}
            },
            "PluginC": {
                "metadata": {
                    "name": "PluginC",
                    "version": "1.0.0",
                    "dependencies": {"NonExistentPlugin": ">=1.0.0"},
                }
            },
        }

        with patch.object(
            self.plugin_manager,
            "get_all_plugins",
            return_value=self.plugin_manager.plugins,
        ):
            valid_result = self.plugin_manager._validate_dependencies("PluginA")
            invalid_result = self.plugin_manager._validate_dependencies("PluginC")

            self.assertTrue(
                valid_result["valid"], "PluginA dependencies should be valid"
            )
            self.assertFalse(
                invalid_result["valid"],
                "PluginC dependencies should be invalid due to missing dependency",
            )
            self.assertIn(
                "nonexistentplugin",
                invalid_result["reason"].lower(),
                "Validation failure reason should mention missing dependency",
            )

    def test_plugin_quality_metrics(self):
        """Test evaluation of plugin quality based on code metrics."""
        # Mock plugins for quality check
        good_quality_plugin = {
            "metadata": {"name": "GoodQualityPlugin", "version": "1.0.0"},
            "module": MagicMock(__file__="/path/to/good_quality_plugin.py"),
        }
        poor_quality_plugin = {
            "metadata": {"name": "PoorQualityPlugin", "version": "1.0.0"},
            "module": MagicMock(__file__="/path/to/poor_quality_plugin.py"),
        }

        self.plugin_manager.plugins["GoodQualityPlugin"] = good_quality_plugin
        self.plugin_manager.plugins["PoorQualityPlugin"] = poor_quality_plugin

        # Mock code quality metrics (e.g., cyclomatic complexity, docstring coverage)
        with patch(
            "agents.plugin_manager.run_code_quality_checks",
            side_effect=[
                {"complexity": 2, "docstring_coverage": 0.9, "passes": True},
                {"complexity": 15, "docstring_coverage": 0.1, "passes": False},
            ],
        ):
            good_result = self.plugin_manager._check_code_quality("GoodQualityPlugin")
            poor_result = self.plugin_manager._check_code_quality("PoorQualityPlugin")

            self.assertTrue(
                good_result["passes"], "Good quality plugin should pass quality checks"
            )
            self.assertFalse(
                poor_result["passes"], "Poor quality plugin should fail quality checks"
            )
            self.assertIn(
                "high complexity",
                poor_result["issues"][0].lower(),
                "Quality check should flag high complexity",
            )

    def test_plugin_load_without_errors(self):
        """Test that plugins load without raising exceptions."""
        # Mock a plugin that loads successfully
        success_plugin = {
            "metadata": {"name": "SuccessPlugin", "version": "1.0.0"},
            "module": MagicMock(),
        }
        # Mock a plugin that raises an error during load
        error_plugin = {
            "metadata": {"name": "ErrorPlugin", "version": "1.0.0"},
            "module": MagicMock(side_effect=Exception("Load error")),
        }

        self.plugin_manager.plugins["SuccessPlugin"] = success_plugin
        self.plugin_manager.plugins["ErrorPlugin"] = error_plugin

        with patch.object(
            self.plugin_manager,
            "get_all_plugins",
            return_value=self.plugin_manager.plugins,
        ):
            success_result = self.plugin_manager._test_load("SuccessPlugin")
            error_result = self.plugin_manager._test_load("ErrorPlugin")

            self.assertTrue(
                success_result["success"],
                "Plugin should load successfully without errors",
            )
            self.assertFalse(
                error_result["success"], "Plugin should fail to load due to exception"
            )
            self.assertIn(
                "load error",
                error_result["error"].lower(),
                "Load failure reason should include the exception message",
            )


if __name__ == "__main__":
    unittest.main()
