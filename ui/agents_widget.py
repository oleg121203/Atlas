"""
Agents widget for the Atlas application.

This module provides the UI component for agent management, including
input validation and sanitization for agent-related inputs.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

from ui.input_validation import validate_ui_input, sanitize_ui_input
from core.logging import get_logger

logger = get_logger("AgentsWidget")

class AgentsWidget(QWidget):
    """Agent management interface widget for Atlas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        logger.info("Agents widget initialized")
    
    def init_ui(self) -> None:
        """Initialize UI components for the agents widget."""
        layout = QVBoxLayout(self)
        
        # Agent list
        self.agent_list = QListWidget()
        layout.addWidget(self.agent_list)
        
        # Input area for new agents or commands
        input_layout = QHBoxLayout()
        self.agent_input = QLineEdit()
        self.agent_input.setPlaceholderText("Enter agent command or name...")
        self.agent_input.returnPressed.connect(self.process_input)
        input_layout.addWidget(self.agent_input)
        
        process_button = QPushButton("Process")
        process_button.clicked.connect(self.process_input)
        input_layout.addWidget(process_button)
        
        layout.addLayout(input_layout)
    
    def process_input(self) -> None:
        """Handle processing agent input with validation and sanitization."""
        input_text = self.agent_input.text().strip()
        if not input_text:
            return
        
        # Validate input
        is_valid, error_msg = validate_ui_input(input_text, "text", "Agent Input")
        if not is_valid:
            logger.warning("Invalid agent input: %s", error_msg)
            # Display error to user (could be improved with a proper error display mechanism)
            self.agent_input.setPlaceholderText(error_msg)
            return
        
        # Sanitize input
        sanitized_input = sanitize_ui_input(input_text)
        logger.debug("Agent input sanitized, original: %s, sanitized: %s", input_text, sanitized_input)
        
        # Add the sanitized input to the list (for demonstration)
        item = QListWidgetItem(f"Command: {sanitized_input}")
        self.agent_list.addItem(item)
        self.agent_input.clear()
        
        # TODO: Implement actual agent command processing logic
        logger.info("Agent input processed: %s", sanitized_input)
    
    def remove_agent(self, item: QListWidgetItem) -> None:
        """
        Remove an agent or command from the list.
        
        Args:
            item: QListWidgetItem to remove
        """
        self.agent_list.takeItem(self.agent_list.row(item))
        logger.info("Agent item removed")
