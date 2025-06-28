"""Workflow Editor component for Atlas."""

import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class WorkflowEditor(QWidget):
    """Editor for creating and modifying workflows in Atlas with cyberpunk styling."""

    workflow_saved = Signal(str, str)
    workflow_selected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                color: #00ffaa;
            }
            QListWidget {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #00ffaa;
                color: #000000;
            }
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        self.initialize_ui()
        self.current_workflow_id = ""
        self.logger.info("WorkflowEditor component initialized")

    def initialize_ui(self) -> None:
        """Initialize the UI components for the workflow editor."""
        layout = QVBoxLayout(self)

        header_label = QLabel("Workflow Editor")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ffaa;")
        layout.addWidget(header_label)

        # Workflow list
        self.workflow_list = QListWidget()
        self.workflow_list.itemClicked.connect(self.on_workflow_selected)
        layout.addWidget(self.workflow_list, 2)

        # Workflow content editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Edit workflow content here...")
        layout.addWidget(self.editor, 5)

        # Buttons for save and new workflow
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Workflow")
        self.save_button.clicked.connect(self.on_save_workflow)
        button_layout.addWidget(self.save_button)

        self.new_button = QPushButton("New Workflow")
        self.new_button.clicked.connect(self.on_new_workflow)
        button_layout.addWidget(self.new_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def update_workflow_list(self, workflows: List[Dict[str, Any]]) -> None:
        """Update the list of workflows.

        Args:
            workflows (List[Dict[str, Any]]): List of workflow dictionaries.
        """
        self.workflow_list.clear()
        for workflow in workflows:
            workflow_name = workflow.get("name", "Unnamed Workflow")
            workflow_id = workflow.get("id", workflow_name)
            item = QListWidgetItem(workflow_name)
            item.setData(Qt.ItemDataRole.UserRole, workflow_id)
            self.workflow_list.addItem(item)
            self.logger.debug(f"Added workflow to list: {workflow_name}")
        self.logger.info(f"Updated workflow list with {len(workflows)} workflows")

    def set_workflow_content(self, workflow_id: str, content: str) -> None:
        """Set the content of the editor for a specific workflow.

        Args:
            workflow_id (str): The ID of the workflow.
            content (str): The content of the workflow.
        """
        self.current_workflow_id = workflow_id
        self.editor.setText(content)
        self.logger.debug(f"Set workflow content for ID: {workflow_id}")

    @Slot()
    def on_save_workflow(self) -> None:
        """Handle save workflow button click."""
        if self.current_workflow_id:
            content = self.editor.toPlainText()
            self.workflow_saved.emit(self.current_workflow_id, content)
            self.logger.info(f"Saved workflow: {self.current_workflow_id}")
        else:
            self.logger.warning("No workflow selected to save")

    @Slot()
    def on_new_workflow(self) -> None:
        """Handle new workflow button click."""
        self.current_workflow_id = ""
        self.editor.clear()
        self.workflow_list.clearSelection()
        self.logger.info("Started new workflow")

    @Slot(QListWidgetItem)
    def on_workflow_selected(self, item: QListWidgetItem) -> None:
        """Handle workflow selection event.

        Args:
            item (QListWidgetItem): The selected item.
        """
        workflow_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_workflow_id = workflow_id
        self.workflow_selected.emit(workflow_id)
        self.logger.info(f"Selected workflow: {workflow_id}")
