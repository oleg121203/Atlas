"""
Defines the abstract base class for all specialized agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import threading
import multiprocessing

from utils.logger import get_logger


class BaseAgent(ABC):
    """Abstract base class for all specialized agents in Atlas."""

    def __init__(self, name: str, connection: Optional[Any] = None) -> None:
        self.name = name
        self.connection = connection
        self.logger = get_logger()
        self.is_active = False
        self.process: Optional[multiprocessing.Process] = None
        self.thread: Optional[threading.Thread] = None
        self.logger.info(f"{self.name} initialized.")

    @abstractmethod
    def execute_task(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Executes a given task based on a prompt and returns the result.

        Args:
            prompt: The specific instruction for the task.
            context: Additional data or state needed to perform the task.

        Returns:
            A string containing the result of the task execution.
        """
        pass

    def start(self) -> None:
        """Start the agent (can be overridden by subclasses)."""
        self.is_active = True
        self.logger.info(f"{self.name} started.")

    def stop(self) -> None:
        """Stop the agent (can be overridden by subclasses)."""
        self.is_active = False
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=5)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        self.logger.info(f"{self.name} stopped.")

    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle messages from other components (can be overridden)."""
        return {"type": "unknown", "data": {}}

    def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message through the connection if available."""
        if self.connection:
            try:
                self.connection.send(message)
            except Exception as e:
                self.logger.error(f"Failed to send message: {e}")

    def is_running(self) -> bool:
        """Check if the agent is currently running."""
        return self.is_active
