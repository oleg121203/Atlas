"""Enhanced Terminal Tool for Atlas."""

import logging
import os
from typing import Any, Dict, List, Optional

try:
    import importlib.util

    PYAUTOGUI_AVAILABLE = importlib.util.find_spec("pyautogui") is not None
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning(
        "PyAutoGUI not installed. Terminal interaction functionality will be limited."
    )

from PySide6.QtCore import QProcess
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class EnhancedTerminal(QWidget):
    """An enhanced terminal tool for Atlas with advanced command execution and history management."""

    def __init__(
        self, config: Optional[Dict[str, Any]] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.history: List[str] = []
        self.history_index = -1
        try:
            self.process = QProcess(self)
            self.process.readyReadStandardOutput.connect(self.on_output_ready)
            self.process.readyReadStandardError.connect(self.on_error_ready)
        except Exception as e:
            self.logger.error(f"Failed to initialize QProcess: {str(e)}")
            self.process = None
        self.init_ui()
        self.initialize()

    def init_ui(self) -> None:
        """Initialize the UI components for the terminal tool."""
        layout = QVBoxLayout(self)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet(
            "background-color: #1a1a1a; color: #00ffaa; border: 1px solid #00ffaa; "
            "font-family: 'Courier New', monospace;"
        )
        font = QFont("Courier New", 10)
        self.output_area.setFont(font)
        layout.addWidget(self.output_area)

        self.input_field = QLineEdit()
        self.input_field.setStyleSheet(
            "background-color: #1a1a1a; color: #00ffaa; border: 1px solid #00ffaa; padding: 5px;"
        )
        self.input_field.returnPressed.connect(self.execute_command)
        layout.addWidget(self.input_field)

        button_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet(
            "background-color: #00ffaa; color: #000000; padding: 5px;"
        )
        self.clear_button.clicked.connect(self.clear_output)
        button_layout.addWidget(self.clear_button)

        self.history_up_button = QPushButton("History Up")
        self.history_up_button.setStyleSheet(
            "background-color: #00ffaa; color: #000000; padding: 5px;"
        )
        self.history_up_button.clicked.connect(self.history_up)
        button_layout.addWidget(self.history_up_button)

        self.history_down_button = QPushButton("History Down")
        self.history_down_button.setStyleSheet(
            "background-color: #00ffaa; color: #000000; padding: 5px;"
        )
        self.history_down_button.clicked.connect(self.history_down)
        button_layout.addWidget(self.history_down_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def initialize(self) -> None:
        """Initialize the terminal tool settings and configurations."""
        self.logger.info("Initializing Enhanced Terminal Tool")
        self.default_shell = self.config.get(
            "default_shell", os.environ.get("SHELL", "/bin/bash")
        )
        self.logger.info("Default shell set to: %s", self.default_shell)

    def execute_command(self) -> None:
        """Execute the command entered in the input field."""
        command = self.input_field.text().strip()
        if not command:
            return

        if not PYAUTOGUI_AVAILABLE:
            logging.error(
                "PyAutoGUI not installed. Cannot execute terminal commands interactively."
            )
            self.output_area.append(
                "Error: Terminal interaction not available without PyAutoGUI."
            )
            return

        if self.process is None:
            self.logger.error("QProcess not initialized. Cannot execute command.")
            self.output_area.append("Error: QProcess not initialized.")
            return

        self.history.append(command)
        self.history_index = len(self.history) - 1
        self.input_field.clear()
        self.output_area.append(f"$ {command}")
        self.logger.info("Executing command: %s", command)

        try:
            self.process.start(self.default_shell, ["-c", command])
        except Exception as e:
            self.logger.error("Failed to execute command: %s", e)
            self.output_area.append(f"Error: {str(e)}")

    def on_output_ready(self) -> None:
        """Handle standard output from the process."""
        if self.process is None:
            self.logger.error("QProcess not initialized. Cannot read output.")
            return

        output = self.process.readAllStandardOutput().data().decode()
        self.output_area.append(output)
        self.logger.debug("Command output: %s", output)

    def on_error_ready(self) -> None:
        """Handle error output from the process."""
        if self.process is None:
            self.logger.error("QProcess not initialized. Cannot read error.")
            return

        error = self.process.readAllStandardError().data().decode()
        self.output_area.append(f"Error: {error}")
        self.logger.error("Command error: %s", error)

    def clear_output(self) -> None:
        """Clear the output area."""
        self.output_area.clear()
        self.logger.info("Cleared terminal output")

    def history_up(self) -> None:
        """Navigate up through command history."""
        if not self.history or self.history_index < 0:
            return
        self.input_field.setText(self.history[self.history_index])
        self.history_index = max(0, self.history_index - 1)
        self.logger.debug("History up to index: %d", self.history_index)

    def history_down(self) -> None:
        """Navigate down through command history."""
        if not self.history or self.history_index >= len(self.history) - 1:
            return
        self.history_index = min(len(self.history) - 1, self.history_index + 1)
        self.input_field.setText(self.history[self.history_index])
        self.logger.debug("History down to index: %d", self.history_index)
