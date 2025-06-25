"""Decision Explanation Module for Atlas

This module provides a UI for displaying explanations of AI decisions
to enhance transparency and user trust within the Atlas application.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox, QListWidget, QListWidgetItem, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.ethics.ethical_guidelines import EthicalGuidelines
import logging

logger = logging.getLogger(__name__)


class DecisionExplanation(QWidget):
    """A widget for displaying explanations of AI decisions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ethics = EthicalGuidelines()
        self.setWindowTitle("AI Decision Explanation")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("AI Decision Explanation")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # Description
        desc = QLabel("View detailed explanations of AI decisions, including the rationale and ethical considerations.")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Decision list
        self.decision_list = QListWidget()
        self.decision_list.itemClicked.connect(self.show_decision_details)
        layout.addWidget(self.decision_list)

        # Detail view
        self.detail_view = QTextEdit()
        self.detail_view.setReadOnly(True)
        layout.addWidget(self.detail_view)

        # Feedback section
        feedback_layout = QHBoxLayout()
        feedback_label = QLabel("Was this decision helpful?")
        feedback_layout.addWidget(feedback_label)

        yes_btn = QPushButton("Yes")
        yes_btn.clicked.connect(lambda: self.submit_feedback(True))
        feedback_layout.addWidget(yes_btn)

        no_btn = QPushButton("No")
        no_btn.clicked.connect(lambda: self.submit_feedback(False))
        feedback_layout.addWidget(no_btn)

        layout.addLayout(feedback_layout)
        self.setLayout(layout)

        # Load sample decisions for demo
        self.load_sample_decisions()

    def load_sample_decisions(self):
        """Load sample AI decisions for demonstration purposes."""
        self.decisions = [
            {
                "id": "DEC001",
                "title": "Task Automation Approval",
                "action": "Automatically complete user task",
                "context": {
                    "explanation": "Task matches user pattern for automation",
                    "audit_log": True,
                    "bias_check": True,
                    "data_protection": True,
                    "user_benefit": True
                }
            },
            {
                "id": "DEC002",
                "title": "Data Collection for Training",
                "action": "Collect user interaction data",
                "context": {
                    "explanation": "Improve AI response accuracy",
                    "audit_log": True,
                    "bias_check": True,
                    "data_protection": False,
                    "user_benefit": True
                }
            }
        ]
        for decision in self.decisions:
            self.decision_list.addItem(QListWidgetItem(f"{decision['id']}: {decision['title']}"))

    def show_decision_details(self, item):
        """Show detailed explanation of the selected decision."""
        index = self.decision_list.row(item)
        if index >= 0 and index < len(self.decisions):
            decision = self.decisions[index]
            is_ethical, scores, explanation = self.ethics.is_action_ethical(decision['action'], decision['context'])
            self.detail_view.setText(explanation)

    def submit_feedback(self, helpful):
        """Submit user feedback on the decision."""
        current_item = self.decision_list.currentItem()
        if current_item:
            index = self.decision_list.row(current_item)
            decision_id = self.decisions[index]['id'] if index < len(self.decisions) else "Unknown"
            feedback_text = "helpful" if helpful else "not helpful"
            logger.info(f"User feedback on decision {decision_id}: {feedback_text}")
            QMessageBox.information(self, "Feedback Received", "Thank you for your feedback on this AI decision.")
