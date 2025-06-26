"""Tests for ApplicationAgent."""

import unittest
from unittest.mock import patch

from modules.agents.application_agent import ApplicationAgent


class TestApplicationAgent(unittest.TestCase):
    """Test suite for ApplicationAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = ApplicationAgent()

    def test_init(self):
        """Test initialization of ApplicationAgent."""
        self.assertEqual(self.agent.name, "Application Control Agent")

    def test_handle_terminal_command(self):
        """Test handling of terminal commands."""
        with patch.object(self.agent, 'execute_command', return_value="Command output") as mock_execute:
            result = self.agent.handle_terminal_command("ls")
            mock_execute.assert_called_once_with("ls")
            self.assertEqual(result, "Command output")

    @patch.object(ApplicationAgent, '_handle_mouse_control')
    @patch('tools.mouse_keyboard_tool.click_at')
    @patch('tools.mouse_keyboard_tool.move_mouse')
    def test_handle_mouse_control_click(self, mock_move, mock_click, mock_mouse):
        """Test handling of mouse click control."""
        mock_click.return_value = "Clicked"
        result = self.agent._handle_mouse_control("click at 100 200")
        self.assertIn("Performed mouse click", result)
        mock_click.assert_called_once()
        mock_move.assert_not_called()

    @patch.object(ApplicationAgent, '_handle_mouse_control')
    @patch('tools.mouse_keyboard_tool.move_mouse')
    def test_handle_mouse_control_move(self, mock_move, mock_mouse):
        """Test handling of mouse move control."""
        mock_move.return_value = "Moved"
        result = self.agent._handle_mouse_control("move mouse to 300 400")
        self.assertIn("Moved mouse", result)
        mock_move.assert_called_once()

    @patch.object(ApplicationAgent, '_handle_keyboard_control')
    @patch('tools.mouse_keyboard_tool.type_text')
    def test_handle_keyboard_control_type(self, mock_type, mock_keyboard):
        """Test handling of keyboard typing control."""
        mock_type.return_value = "Typed"
        result = self.agent._handle_keyboard_control("type hello world")
        self.assertIn("Typed text", result)
        mock_type.assert_called_once_with("hello world")

    @patch.object(ApplicationAgent, '_handle_keyboard_control')
    @patch('tools.mouse_keyboard_tool.press_key')
    def test_handle_keyboard_control_press(self, mock_press, mock_keyboard):
        """Test handling of keyboard key press control."""
        mock_press.return_value = "Pressed"
        result = self.agent._handle_keyboard_control("press enter")
        self.assertIn("Pressed key", result)
        mock_press.assert_called_once_with("enter")

    @patch.object(ApplicationAgent, '_handle_clipboard_operation')
    @patch('tools.clipboard_tool.set_clipboard_text')
    def test_handle_clipboard_operation_copy(self, mock_set, mock_clipboard):
        """Test handling of clipboard copy operation."""
        mock_set.return_value = "Copied"
        result = self.agent._handle_clipboard_operation("copy some text")
        self.assertIn("Copied to clipboard", result)
        mock_set.assert_called_once_with("some text")

    @patch.object(ApplicationAgent, '_handle_clipboard_operation')
    @patch('tools.clipboard_tool.get_clipboard_text')
    def test_handle_clipboard_operation_paste(self, mock_get, mock_clipboard):
        """Test handling of clipboard paste operation."""
        mock_get.return_value = "Pasted text"
        result = self.agent._handle_clipboard_operation("paste")
        self.assertIn("Pasted from clipboard", result)
        mock_get.assert_called_once()

    @patch.object(ApplicationAgent, '_handle_clipboard_operation')
    @patch('tools.clipboard_tool.clear_clipboard')
    def test_handle_clipboard_operation_clear(self, mock_clear, mock_clipboard):
        """Test handling of clipboard clear operation."""
        mock_clear.return_value = "Cleared"
        result = self.agent._handle_clipboard_operation("clear clipboard")
        self.assertIn("Cleared clipboard", result)
        mock_clear.assert_called_once()

    @patch.object(ApplicationAgent, '_handle_app_launch')
    @patch('tools.terminal_tool.execute_command')
    def test_handle_app_launch(self, mock_execute, mock_launch):
        """Test handling of application launch."""
        mock_execute.return_value = "Launched"
        result = self.agent._handle_app_launch("launch Safari")
        self.assertIn("Launched application Safari", result)
        mock_execute.assert_called_once()

    def test_execute_task_terminal(self):
        """Test execute_task with a terminal command."""
        with patch.object(self.agent, '_handle_terminal_command') as mock_terminal:
            mock_terminal.return_value = "Terminal result"
            result = self.agent.execute_task("Run terminal command ls", {})
            self.assertEqual(result, "Terminal result")
            mock_terminal.assert_called_once()

    def test_execute_task_mouse(self):
        """Test execute_task with a mouse control task."""
        with patch.object(self.agent, '_handle_mouse_control') as mock_mouse:
            mock_mouse.return_value = "Mouse result"
            result = self.agent.execute_task("Click mouse at 100 200", {})
            self.assertEqual(result, "Mouse result")
            mock_mouse.assert_called_once()

    def test_execute_task_default(self):
        """Test execute_task with an unrecognized task."""
        with patch.object(self.agent, '_default_response') as mock_default:
            mock_default.return_value = "Default response"
            result = self.agent.execute_task("Unknown task", {})
            self.assertEqual(result, "Default response")
            mock_default.assert_called_once()


if __name__ == '__main__':
    unittest.main()
