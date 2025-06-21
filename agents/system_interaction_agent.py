"""
Specialized agent for interacting with the operating system.
"""

from typing import Any, Dict

from agents.base_agent import BaseAgent
from tools.terminal_tool import execute_command


class SystemInteractionAgent(BaseAgent):
    """Handles tasks like file I/O, command execution, and system automation."""

    def __init__(self):
        super().__init__("System Interaction Agent")

    def execute_task(self, prompt: str, context: Dict[str, Any]) -> str:
        self.logger.info(f"Executing system task: '{prompt}'")

        #For simplicity, we'll assume the prompt is a direct command.
        #In a real scenario, we'd have more sophisticated parsing.
        command = prompt

        try:
            result = execute_command(command)
            if result.success:
                self.logger.info(f"Command executed successfully. Output:\n{result.stdout}")
                return result.stdout or "Command executed successfully with no output."
            self.logger.error(f"Command failed. Error:\n{result.stderr}")
            return f"Error executing command: {result.stderr}"
        except Exception as e:
            self.logger.error(f"An unexpected error occurred in SystemInteractionAgent: {e}")
            return f"An unexpected error occurred: {e}"
