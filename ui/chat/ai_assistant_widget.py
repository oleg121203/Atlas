"""
AI Assistant Widget for Atlas UI

This module provides a UI component for interacting with AI models integrated
into the Atlas application.
"""

import json

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.ai_integration import AIIntegrationError, get_ai_model_manager
from core.logging import get_logger

logger = get_logger("AIAssistantWidget")


class AIAssistantWidget(QWidget):
    """UI Widget for interacting with AI Assistant functionality in Atlas."""

    suggestionReceived = Signal(str)
    taskAutomated = Signal(dict)

    def __init__(self, app, parent=None):
        """
        Initialize the AI Assistant widget.

        Args:
            app: Instance of AtlasApplication
            parent: Parent widget, if any
        """
        super().__init__(parent)
        self.app = app
        self.ai_manager = get_ai_model_manager()
        self.logger = get_logger("AIAssistantWidget")
        self.setup_ui()
        self.logger.info("AIAssistantWidget initialized")

    def setup_ui(self):
        """Set up the user interface for the AI Assistant widget."""
        self.logger.info("Setting up AI Assistant UI")
        layout = QVBoxLayout()

        # AI Model selection
        model_layout = QHBoxLayout()
        model_label = QLabel("AI Model:")
        self.model_combo = QComboBox()
        self.update_model_list()
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Input area for user requests
        input_layout = QHBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "Enter your request or question for the AI assistant..."
        )
        self.input_text.setFixedHeight(100)
        input_layout.addWidget(self.input_text)

        input_buttons_layout = QVBoxLayout()
        self.request_btn = QPushButton("Get Suggestion")
        self.request_btn.clicked.connect(self.request_suggestion)
        self.automate_btn = QPushButton("Automate Task")
        self.automate_btn.clicked.connect(self.request_automation)
        input_buttons_layout.addWidget(self.request_btn)
        input_buttons_layout.addWidget(self.automate_btn)
        input_layout.addLayout(input_buttons_layout)
        layout.addLayout(input_layout)

        # Output area for AI responses
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("AI responses will appear here...")
        layout.addWidget(self.output_text)

        # Context settings
        context_layout = QHBoxLayout()
        self.context_label = QLabel("Context: None")
        self.clear_context_btn = QPushButton("Clear Context")
        self.clear_context_btn.clicked.connect(self.clear_context)
        context_layout.addWidget(self.context_label)
        context_layout.addWidget(self.clear_context_btn)
        layout.addLayout(context_layout)

        self.setLayout(layout)
        self.logger.info("AI Assistant UI setup complete")

    def update_model_list(self):
        """Update the list of available AI models in the combo box."""
        self.model_combo.clear()
        for model_name in self.ai_manager.models:
            self.model_combo.addItem(model_name)
        self.logger.info("Updated AI model list in UI")

    def get_current_context(self) -> dict:
        """
        Get the current context for AI requests.

        Returns:
            dict: Current context information
        """
        # In a real implementation, this would gather relevant context from the application
        # For now, we'll return a simple placeholder
        return {"user_input": self.input_text.toPlainText(), "history": []}

    def request_suggestion(self):
        """Request a suggestion from the AI model based on user input."""
        self.logger.info("Requesting AI suggestion")
        model_name = self.model_combo.currentText()
        if not model_name:
            self.output_text.setText("Error: No AI model selected.")
            self.logger.warning("No AI model selected for suggestion request")
            return

        context = self.get_current_context()
        if not context.get("user_input"):
            self.output_text.setText("Error: Please enter a request or question.")
            self.logger.warning("Empty input for AI suggestion request")
            return

        self.request_btn.setEnabled(False)
        self.output_text.setText("Processing request...")
        try:
            # Determine prompt type based on model name or context
            prompt_type = "code" if "code" in model_name.lower() else "general"
            suggestion = self.ai_manager.get_suggestion(
                model_name, context, prompt_type
            )
            self.output_text.setText(suggestion)
            self.suggestionReceived.emit(suggestion)
            self.logger.info("Received AI suggestion successfully")
        except AIIntegrationError as e:
            error_msg = f"Error getting suggestion: {str(e)}"
            self.output_text.setText(error_msg)
            self.logger.error(error_msg, exc_info=True)
        finally:
            self.request_btn.setEnabled(True)

    def request_automation(self):
        """Request task automation from the AI model based on user input."""
        self.logger.info("Requesting AI task automation")
        model_name = self.model_combo.currentText()
        if not model_name:
            self.output_text.setText("Error: No AI model selected.")
            self.logger.warning("No AI model selected for automation request")
            return

        context = self.get_current_context()
        user_input = context.get("user_input", "")
        if not user_input:
            self.output_text.setText(
                "Error: Please enter a task description to automate."
            )
            self.logger.warning("Empty input for AI automation request")
            return

        self.automate_btn.setEnabled(False)
        self.output_text.setText("Generating automation plan...")
        try:
            automation_plan = self.ai_manager.automate_task(
                model_name, user_input, context
            )
            self.output_text.setText(json.dumps(automation_plan, indent=2))
            self.taskAutomated.emit(automation_plan)
            self.logger.info("Received AI automation plan successfully")
        except AIIntegrationError as e:
            error_msg = f"Error generating automation plan: {str(e)}"
            self.output_text.setText(error_msg)
            self.logger.error(error_msg, exc_info=True)
        finally:
            self.automate_btn.setEnabled(True)

    def clear_context(self):
        """Clear the current context for AI interactions."""
        self.context_label.setText("Context: None")
        self.logger.info("AI context cleared")

    def set_context(self, context_description: str):
        """
        Set a description of the current context for AI interactions.

        Args:
            context_description: Description of the current context
        """
        self.context_label.setText(f"Context: {context_description}")
        self.logger.info("AI context set to: %s", context_description)
