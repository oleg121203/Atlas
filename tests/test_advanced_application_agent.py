"""Tests for AdvancedApplicationAgent."""

import unittest
from unittest.mock import patch, MagicMock
import os

from agents.advanced_application_agent import AdvancedApplicationAgent


class TestAdvancedApplicationAgent(unittest.TestCase):
    """Test suite for AdvancedApplicationAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = MagicMock()
        self.agent = AdvancedApplicationAgent(self.mock_logger)

    def test_init(self):
        """Test initialization of AdvancedApplicationAgent."""
        self.assertIsNotNone(self.agent)
        self.mock_logger.info.assert_called_with("Advanced Application Control Agent initialized.")

    def test_execute_task_workflow(self):
        """Test execute_task with a workflow automation task."""
        with patch.object(self.agent, '_handle_complex_workflow') as mock_workflow:
            mock_workflow.return_value = "Workflow result"
            result = self.agent.execute_task("Automate workflow in Excel", {})
            self.assertEqual(result, "Workflow result")
            mock_workflow.assert_called_once()
            self.mock_logger.info.assert_called_with("Executing advanced application task: Automate workflow in Excel")

    def test_execute_task_window_management(self):
        """Test execute_task with a window management task."""
        task = "Window management for Finder"
        context = {}

        with patch.object(self.agent, '_handle_window_management', return_value="Window management successful") as mock_handler:
            result = self.agent.execute_task(task, context)
            mock_handler.assert_called_once_with(task)
            self.assertEqual(result, "Window management successful")
            self.mock_logger.info.assert_called_with("Executing advanced application task: Window management for Finder")

    def test_execute_task_script_execution(self):
        """Test execute_task with a script execution task."""
        task = "Script execution for a command"
        context = {}

        with patch.object(self.agent, '_handle_script_execution', return_value="Script executed successfully") as mock_handler:
            result = self.agent.execute_task(task, context)
            mock_handler.assert_called_once_with(task)
            self.assertEqual(result, "Script executed successfully")
            self.mock_logger.info.assert_called_with("Executing advanced application task: Script execution for a command")

    def test_execute_task_ui_automation(self):
        """Test execute_task with a UI automation task."""
        task = "UI automation for a button click"
        context = {}

        with patch.object(self.agent, '_handle_ui_automation', return_value="Performed UI automation: UI automation for a button click") as mock_handler:
            result = self.agent.execute_task(task, context)
            mock_handler.assert_called_once_with(task)
            self.assertEqual(result, "Performed UI automation: UI automation for a button click")
            self.mock_logger.info.assert_called_with("Executing advanced application task: UI automation for a button click")

    def test_execute_task_complex_workflow(self):
        """Test execute_task with a complex workflow task."""
        task = "Workflow for document processing"
        context = {}

        with patch.object(self.agent, '_handle_complex_workflow', return_value="Complex workflow completed for: Workflow for document processing") as mock_handler:
            result = self.agent.execute_task(task, context)
            mock_handler.assert_called_once_with(task)
            self.assertEqual(result, "Complex workflow completed for: Workflow for document processing")
            self.mock_logger.info.assert_called_with("Executing advanced application task: Workflow for document processing")

    def test_execute_task_default(self):
        """Test execute_task with an unrecognized task."""
        task = "Unknown task"
        context = {}

        with patch.object(self.agent, '_default_task_handler', return_value="Task executed with default handler: Unknown task") as mock_handler:
            result = self.agent.execute_task(task, context)
            mock_handler.assert_called_once_with(task)
            self.assertEqual(result, "Task executed with default handler: Unknown task")
            self.mock_logger.info.assert_called_with("Executing advanced application task: Unknown task")

    def test_execute_task_error_handling(self):
        """Test execute_task error handling when an exception occurs."""
        task = "Window management for Finder"
        context = {}

        with patch.object(self.agent, '_handle_window_management', side_effect=Exception("Test error")) as mock_handler:
            result = self.agent.execute_task(task, context)
            mock_handler.assert_called_once_with(task)
            self.assertTrue(result.startswith("Failed to execute task: Test error"))
            self.mock_logger.error.assert_called_with("Error executing task: Test error")

    def test_handle_window_management_os_type_posix(self):
        """Test window management handler for POSIX systems (macOS/Linux)."""
        task = "Window management for Finder"

        with patch('os.name', 'posix'):
            with patch('subprocess.run', return_value=MagicMock(returncode=0, stdout="Success", stderr="")), \
                 patch.object(self.agent, '_generate_applescript_for_task', return_value="tell application \"System Events\" to tell process \"Finder\" to activate"):
                result = self.agent._handle_window_management(task)
                self.assertEqual(result, "Window management successful: Success")
                self.mock_logger.info.assert_called_with("Handling window management: Window management for Finder")

    def test_handle_window_management_os_type_nt(self):
        """Test window management handler for NT systems (Windows)."""
        task = "Window management for Explorer"

        with patch('os.name', 'nt'):
            with patch('subprocess.run', return_value=MagicMock(returncode=0, stdout="Success", stderr="")), \
                 patch.object(self.agent, '_generate_powershell_script_for_task', return_value="Get-Process | Where-Object {$_.MainWindowTitle -like '*Explorer*'} | Select-Object -First 1 | ForEach-Object { $_.MainWindowHandle | Set-ForegroundWindow }"):
                result = self.agent._handle_window_management(task)
                self.assertEqual(result, "Window management successful: Success")
                self.mock_logger.info.assert_called_with("Handling window management: Window management for Explorer")

    def test_handle_window_management_unsupported_os(self):
        """Test window management handler for unsupported OS."""
        task = "Window management for Finder"

        with patch('os.name', 'unsupported'):
            result = self.agent._handle_window_management(task)
            self.assertEqual(result, "Unsupported OS for window management")
            self.mock_logger.info.assert_called_with("Handling window management: Window management for Finder")

    def test_get_status(self):
        """Test getting the agent's status."""
        result = self.agent.get_status()
        self.assertEqual(result, "Advanced Application Agent is operational")

    def test_initialize(self):
        """Test initializing the agent."""
        with patch.object(self.agent, '_check_tools') as mock_check:
            self.agent.initialize()
            mock_check.assert_called_once()
            self.mock_logger.info.assert_called_with("Initializing Advanced Application Agent")

    def test_shutdown(self):
        """Test shutting down the agent."""
        self.agent.shutdown()
        self.mock_logger.info.assert_called_with("Shutting down Advanced Application Agent")

    def test_handle_error(self):
        """Test error handling method."""
        error = "Test error message"
        result = self.agent.handle_error(error)
        self.assertEqual(result, "Error handled: Test error message")
        self.mock_logger.error.assert_called_with("Handling error: Test error message")


if __name__ == '__main__':
    unittest.main()
