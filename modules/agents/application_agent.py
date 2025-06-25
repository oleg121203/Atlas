"""Application Agent module."""

import logging
from typing import Dict, Any, Tuple

# Assuming BaseAgent or similar parent class exists in agents directory
from modules.agents.base_agent import BaseAgent


class ApplicationAgent(BaseAgent):
    """Agent for controlling applications and system interactions."""

    def __init__(self):
        super().__init__("Application Control Agent")
        self.logger = logging.getLogger(__name__)

    def execute_task(self, prompt: str, context: Dict[str, Any]) -> str:
        """Execute a task related to application control."""
        self.logger.info(f"Executing application control task: '{prompt}'")
        prompt_lower = prompt.lower()

        try:
            if "terminal" in prompt_lower or "command" in prompt_lower or "shell" in prompt_lower:
                return self._handle_terminal_command(prompt)
            elif "mouse" in prompt_lower or "click" in prompt_lower or "move" in prompt_lower:
                return self._handle_mouse_control(prompt)
            elif "keyboard" in prompt_lower or "type" in prompt_lower or "press" in prompt_lower:
                return self._handle_keyboard_control(prompt)
            elif "clipboard" in prompt_lower or "copy" in prompt_lower or "paste" in prompt_lower:
                return self._handle_clipboard_operation(prompt)
            elif "launch" in prompt_lower or "open app" in prompt_lower or "start app" in prompt_lower:
                return self._handle_app_launch(prompt)
            else:
                return self._default_response(prompt)
        except Exception as e:
            self.logger.error(f"Failed to execute task: {e}")
            return f"Failed to execute task: {str(e)}"

    def _handle_terminal_command(self, command: str) -> str:
        """Handle terminal command execution."""
        try:
            from tools.terminal_tool import execute_command
            result = execute_command(command)
            return f"Executed terminal command: {result}"
        except Exception as e:
            self.logger.error(f"Failed to execute terminal command: {e}")
            return f"Failed to execute terminal command: {str(e)}"

    def _handle_mouse_control(self, instruction: str) -> str:
        """Handle mouse control actions."""
        try:
            from tools.mouse_keyboard_tool import click_at, move_mouse, MouseButton
            if "click" in instruction.lower():
                # Default to center or parse coordinates if provided
                x, y = self._extract_coordinates(instruction)
                result = click_at(x, y, MouseButton.LEFT)
                return f"Performed mouse click at ({x}, {y})"
            elif "move" in instruction.lower():
                x, y = self._extract_coordinates(instruction)
                result = move_mouse(x, y)
                return f"Moved mouse to ({x}, {y})"
            return "Mouse control action not recognized."
        except Exception as e:
            self.logger.error(f"Failed to perform mouse control: {e}")
            return f"Failed to perform mouse control: {str(e)}"

    def _handle_keyboard_control(self, instruction: str) -> str:
        """Handle keyboard control actions."""
        try:
            from tools.mouse_keyboard_tool import type_text, press_key
            if "type" in instruction.lower():
                text = self._extract_text(instruction)
                result = type_text(text)
                return f"Typed text: {text}"
            elif "press" in instruction.lower():
                key = self._extract_key(instruction)
                result = press_key(key)
                return f"Pressed key: {key}"
            return "Keyboard control action not recognized."
        except Exception as e:
            self.logger.error(f"Failed to perform keyboard control: {e}")
            return f"Failed to perform keyboard control: {str(e)}"

    def _handle_clipboard_operation(self, instruction: str) -> str:
        """Handle clipboard operations."""
        try:
            from tools.clipboard_tool import set_clipboard_text, get_clipboard_text, clear_clipboard
            if "copy" in instruction.lower():
                text = self._extract_text(instruction)
                result = set_clipboard_text(text)
                return f"Copied to clipboard: {text}"
            elif "paste" in instruction.lower():
                result = get_clipboard_text()
                return f"Pasted from clipboard: {result}"
            elif "clear" in instruction.lower():
                result = clear_clipboard()
                return f"Cleared clipboard"
            return "Clipboard operation not recognized."
        except Exception as e:
            self.logger.error(f"Failed to perform clipboard operation: {e}")
            return f"Failed to perform clipboard operation: {str(e)}"

    def _handle_app_launch(self, instruction: str) -> str:
        """Handle launching applications."""
        try:
            app_name = self._extract_app_name(instruction)
            import os
            if os.name == 'posix':  # macOS or Linux
                command = f"open -a '{app_name}'"
            else:  # Windows
                command = f"start {app_name}"
            from tools.terminal_tool import execute_command
            result = execute_command(command)
            return f"Launched application {app_name}"
        except Exception as e:
            self.logger.error(f"Failed to launch application: {e}")
            return f"Failed to launch application: {str(e)}"

    def _default_response(self, prompt: str) -> str:
        """Default response for unrecognized tasks."""
        return "Task not recognized for application control. Please specify a task related to terminal, mouse, keyboard, clipboard, or app launch."

    def _extract_coordinates(self, instruction: str) -> Tuple[int, int]:
        """Extract coordinates from instruction."""
        import re
        coords = re.findall(r'\d+', instruction)
        if len(coords) >= 2:
            return (int(coords[0]), int(coords[1]))
        return (500, 500)  # Default center coordinates if not specified

    def _extract_text(self, instruction: str) -> str:
        """Extract text content from instruction."""
        import re
        match = re.search(r'\"(.*?)\"|text\s+(.+?)(?:\s+|$)', instruction)
        if match:
            return match.group(1) or match.group(2) or ""
        return ""

    def _extract_key(self, instruction: str) -> str:
        """Extract key name from instruction."""
        import re
        match = re.search(r'key\s+(\w+)|press\s+(\w+)', instruction, re.IGNORECASE)
        if match:
            return match.group(1) or match.group(2) or "enter"
        return "enter"

    def _extract_app_name(self, instruction: str) -> str:
        """Extract application name from instruction."""
        import re
        match = re.search(r'launch\s+(.+?)(?:\s+|$)|open\s+app\s+(.+?)(?:\s+|$)|start\s+app\s+(.+?)(?:\s+|$)', instruction, re.IGNORECASE)
        if match:
            return match.group(1) or match.group(2) or match.group(3) or ""
        return ""
