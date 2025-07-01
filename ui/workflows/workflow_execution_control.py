"""Workflow Execution Control component for Atlas."""

import json
import logging
import os
import pathlib
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.components.loading_spinner import LoadingSpinner
from ui.module_communication import EVENT_BUS
from workflow.engine import WorkflowEngine


class WorkflowExecutionControl(QWidget):
    """Control panel for executing workflows in Atlas with cyberpunk styling."""

    execute_workflow = Signal(str)
    stop_workflow = Signal(str)
    workflow_selected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.event_bus = EVENT_BUS
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
        self.is_executing = False
        self.logger.info("WorkflowExecutionControl component initialized")

    def initialize_ui(self) -> None:
        """Initialize the UI components for the workflow execution control."""
        layout = QVBoxLayout(self)

        header_label = QLabel("Workflow Execution")
        header_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #00ffaa;"
        )
        layout.addWidget(header_label)

        # Workflow list
        self.workflow_list = QListWidget()
        self.workflow_list.itemClicked.connect(self.on_workflow_selected)
        layout.addWidget(self.workflow_list, 5)

        # Buttons for execute and stop
        button_layout = QHBoxLayout()
        self.execute_button = QPushButton("Execute Workflow")
        self.execute_button.clicked.connect(self.on_execute_workflow)
        button_layout.addWidget(self.execute_button)

        self.stop_button = QPushButton("Stop Workflow")
        self.stop_button.clicked.connect(self.on_stop_workflow)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        self.spinner = LoadingSpinner(self)
        layout.addWidget(self.spinner)

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

    def set_execution_state(self, workflow_id: str, is_executing: bool) -> None:
        """Set the execution state of a workflow.

        Args:
            workflow_id (str): The ID of the workflow.
            is_executing (bool): Whether the workflow is currently executing.
        """
        self.current_workflow_id = workflow_id
        self.is_executing = is_executing
        self.execute_button.setEnabled(not is_executing)
        self.stop_button.setEnabled(is_executing)
        self.logger.debug(f"Set execution state for {workflow_id}: {is_executing}")

    @Slot()
    def on_execute_workflow(self) -> None:
        """Handle execute workflow button click."""
        if self.current_workflow_id and not self.is_executing:
            self.execute_button.setEnabled(False)
            self.spinner.start()
            # Завантажити план workflow (наприклад, з JSON-файлу)
            workflow_id = self.current_workflow_id
            patterns_path = (
                pathlib.Path(os.path.dirname(__file__)).parent.parent
                / "workflow"
                / "workflow_patterns.json"
            )
            with open(patterns_path, "r") as f:
                patterns = json.load(f)
            plan = None
            initial_state = {}
            for key, wf in patterns.get("patterns", {}).items():
                if (
                    key == workflow_id
                    or wf.get("name") == workflow_id
                    or wf.get("id") == workflow_id
                ):
                    # Конвертуємо структуру у список кроків для WorkflowEngine
                    steps = wf.get("structure", {}).get("steps", [])
                    # Кожен крок повинен мати tool_name та params
                    plan = []
                    for step in steps:
                        tool_name = (
                            step.get("name") or step.get("type") or "unknown_tool"
                        )
                        params = step.get("config", {})
                        plan.append({"tool_name": tool_name, "params": params})
                    break
            if not plan:
                QMessageBox.critical(
                    self,
                    "Workflow Error",
                    f"Workflow plan not found for: {workflow_id}",
                )
                return
            engine = WorkflowEngine()
            result = engine.execute_workflow_plan(plan, initial_state)
            msg = json.dumps(result, indent=2, ensure_ascii=False)
            self.spinner.stop()
            self.execute_button.setEnabled(True)
            if result["errors"]:
                QMessageBox.critical(self, "Workflow Execution Failed", msg)
            else:
                QMessageBox.information(self, "Workflow Execution Success", msg)
            self.set_execution_state(self.current_workflow_id, False)
            self.logger.info(f"Executed workflow: {self.current_workflow_id}")
        else:
            self.logger.warning("No workflow selected or already executing")

    @Slot()
    def on_stop_workflow(self) -> None:
        """Handle stop workflow button click."""
        if self.current_workflow_id and self.is_executing:
            self.stop_workflow.emit(self.current_workflow_id)
            self.set_execution_state(self.current_workflow_id, False)
            self.logger.info(f"Stopped workflow: {self.current_workflow_id}")
        else:
            self.logger.warning("No workflow executing to stop")

    @Slot(QListWidgetItem)
    def on_workflow_selected(self, item: QListWidgetItem) -> None:
        """Handle workflow selection event.

        Args:
            item (QListWidgetItem): The selected item.
        """
        workflow_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_workflow_id = workflow_id
        self.workflow_selected.emit(workflow_id)
        self.logger.info(f"Selected workflow for execution: {workflow_id}")
