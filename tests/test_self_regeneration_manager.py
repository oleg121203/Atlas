"""Test module for SelfRegenerationManager."""

import unittest
from pathlib import Path
from unittest.mock import patch

from agents.self_regeneration_manager import SelfRegenerationManager


class TestSelfRegenerationManager(unittest.TestCase):
    """Test class for SelfRegenerationManager."""

    def setUp(self):
        """Set up the test environment before each test."""
        self.project_root = str(Path(__file__).parent.parent)
        self.manager = SelfRegenerationManager(self.project_root)

    def test_initialization(self):
        """Test that SelfRegenerationManager initializes correctly."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(str(self.manager.project_root), self.project_root)
        self.assertEqual(self.manager.fixes_applied, [])
        self.assertTrue(len(self.manager.issue_types) > 0)

    def test_detect_issues_empty(self):
        """Test detecting issues when there are none."""
        with (
            patch.object(self.manager, "_detect_import_issues", return_value=[]),
            patch.object(self.manager, "_detect_missing_methods", return_value=[]),
            patch.object(self.manager, "_detect_broken_tools", return_value=[]),
            patch.object(self.manager, "_detect_missing_plugins", return_value=[]),
            patch.object(self.manager, "_detect_config_issues", return_value=[]),
        ):
            issues = self.manager._detect_issues()
            self.assertEqual(issues, [])

    def test_execute_tool_unknown(self):
        """Test executing an unknown tool."""
        result = self.manager.execute_tool("unknown_tool", {})
        self.assertFalse(result["success"])
        self.assertIn("Unknown tool", result["message"])

    def test_execute_create_module_tool(self):
        """Test executing create_module tool."""
        with patch.object(
            self.manager, "_run_tool_code", return_value=None
        ) as mock_run:
            result = self.manager.execute_tool(
                "create_module", {"module_name": "test_module"}
            )
            self.assertTrue(result["success"])
            self.assertIn("Tool for module test_module created", result["message"])
            mock_run.assert_called_once()

    def test_execute_create_class_tool(self):
        """Test executing create_class tool."""
        with patch.object(
            self.manager, "_run_tool_code", return_value=None
        ) as mock_run:
            params = {"class_name": "TestClass", "module_name": "test_module"}
            result = self.manager.execute_tool("create_class", params)
            self.assertTrue(result["success"])
            self.assertIn("Tool for class TestClass created", result["message"])
            mock_run.assert_called_once()

    def test_execute_create_method_tool(self):
        """Test executing create_method tool."""
        with patch.object(
            self.manager, "_run_tool_code", return_value=None
        ) as mock_run:
            params = {
                "method_name": "test_method",
                "class_name": "TestClass",
                "module_name": "test_module",
            }
            result = self.manager.execute_tool("create_method", params)
            self.assertTrue(result["success"])
            self.assertIn("Tool for method test_method created", result["message"])
            mock_run.assert_called_once()

    def test_execute_create_tool_tool(self):
        """Test executing create_tool tool."""
        with patch.object(
            self.manager, "_run_tool_code", return_value=None
        ) as mock_run:
            result = self.manager.execute_tool(
                "create_tool", {"tool_name": "test_tool"}
            )
            self.assertTrue(result["success"])
            self.assertIn("Tool for tool test_tool created", result["message"])
            mock_run.assert_called_once()

    def test_execute_create_plugin_tool(self):
        """Test executing create_plugin tool."""
        with patch.object(
            self.manager, "_run_tool_code", return_value=None
        ) as mock_run:
            result = self.manager.execute_tool(
                "create_plugin", {"plugin_name": "test_plugin"}
            )
            self.assertTrue(result["success"])
            self.assertIn("Tool for plugin test_plugin created", result["message"])
            mock_run.assert_called_once()

    def test_execute_create_config_tool(self):
        """Test executing create_config tool."""
        with patch.object(
            self.manager, "_run_tool_code", return_value=None
        ) as mock_run:
            result = self.manager.execute_tool(
                "create_config", {"config_name": "test_config"}
            )
            self.assertTrue(result["success"])
            self.assertIn("Tool for config test_config created", result["message"])
            mock_run.assert_called_once()

    def test_handle_tool_activation(self):
        """Test handling tool activation from UI."""
        mock_return = {"success": True, "message": "Tool executed"}
        with patch.object(
            self.manager, "execute_tool", return_value=mock_return
        ) as mock_execute:
            result = self.manager.handle_tool_activation("test_tool")
            self.assertTrue(result["success"])
            self.assertEqual(result["message"], "Tool executed")
            mock_execute.assert_called_once_with("test_tool", parameters={})

    def test_generate_browser_tool_content(self):
        """Test generating browser tool content."""
        content = self.manager._generate_browser_tool_content("browser_tool")
        self.assertIn("BrowserTool", content)
        self.assertIn("open_url", content)

    def test_generate_generic_tool_content(self):
        """Test generating generic tool content."""
        content = self.manager._generate_generic_tool_content("generic_tool")
        self.assertIn("GenericTool", content)
        self.assertIn("execute", content)


if __name__ == "__main__":
    unittest.main()
