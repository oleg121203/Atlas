"""
Self-Improvement UI for Atlas

This module provides a UI component for interacting with the SelfImprovementEngine,
allowing users to view identified improvement areas, plans, and execution history.
"""

from PySide6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget


class SelfImprovementUI(QWidget):
    """UI component for displaying and interacting with self-improvement engine data."""

    def __init__(self, improvement_engine=None, parent: QWidget | None = None):
        super().__init__(parent)
        self.improvement_engine = improvement_engine
        self.init_ui()
        self.connect_to_engine()

    def init_ui(self) -> None:
        """Initialize the UI layout and components."""
        layout = QVBoxLayout(self)

        title_label = QLabel("Self-Improvement Engine")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ffaa;")
        layout.addWidget(title_label)

        self.improvement_tree = QTreeWidget()
        self.improvement_tree.setHeaderLabels(["Improvement Area", "Details"])
        self.improvement_tree.setStyleSheet(
            "background-color: #1a1a1a; color: #ffffff; border: 1px solid #00ffaa;"
        )
        layout.addWidget(self.improvement_tree)

        self.setLayout(layout)
        self.update_improvement_display()

    def connect_to_engine(self):
        """Connect to the self-improvement engine signals to update UI on changes."""
        if self.improvement_engine:
            self.improvement_engine.improvement_identified.connect(
                self.on_improvement_identified
            )
            self.improvement_engine.improvement_plan_updated.connect(
                self.on_plan_updated
            )
            self.improvement_engine.improvement_executed.connect(
                self.on_improvement_executed
            )

    def on_improvement_identified(self, improvement_area: dict):
        """Handle new improvement area identified by the engine.

        Args:
            improvement_area: Dictionary containing improvement area details.
        """
        self.update_improvement_display()

    def on_plan_updated(self, plan: dict):
        """Handle updates to improvement plans.

        Args:
            plan: Dictionary containing updated improvement plan.
        """
        self.update_improvement_display()

    def on_improvement_executed(self, result: dict):
        """Handle execution of improvement plans.

        Args:
            result: Dictionary containing the results of the improvement execution.
        """
        self.update_improvement_display()

    def update_improvement_display(self) -> None:
        """Update the tree widget with the latest self-improvement engine data."""
        self.improvement_tree.clear()

        if self.improvement_engine:
            # Display current improvement areas
            for (
                area_type,
                area_data,
            ) in self.improvement_engine.improvement_areas.items():
                area_item = QTreeWidgetItem(self.improvement_tree, [area_type, ""])
                QTreeWidgetItem(area_item, ["Issue", area_data.get("issue", "N/A")])
                QTreeWidgetItem(
                    area_item,
                    ["Current Value", str(area_data.get("current_value", "N/A"))],
                )
                QTreeWidgetItem(
                    area_item,
                    ["Target Value", str(area_data.get("target_value", "N/A"))],
                )

            # Display improvement plans
            for area_type, plan in self.improvement_engine.improvement_plans.items():
                plan_item = QTreeWidgetItem(
                    self.improvement_tree, [f"Plan: {area_type}", ""]
                )
                QTreeWidgetItem(
                    plan_item, ["Expected Outcome", plan.get("expected_outcome", "N/A")]
                )
                steps_item = QTreeWidgetItem(plan_item, ["Steps", ""])
                for i, step in enumerate(plan.get("steps", [])):
                    QTreeWidgetItem(steps_item, [f"Step {i + 1}", step])

            # Display improvement history if available
            history = self.improvement_engine.get_improvement_history()
            if history:
                history_item = QTreeWidgetItem(
                    self.improvement_tree, ["Improvement History", ""]
                )
                for i, result in enumerate(history[:5]):  # Limit to last 5 improvements
                    result_text = (
                        f"Improvement {i + 1}: {result.get('area', 'Unknown')}"
                    )
                    result_item = QTreeWidgetItem(history_item, [result_text, ""])
                    QTreeWidgetItem(
                        result_item, ["Success", str(result.get("success", "N/A"))]
                    )
                    QTreeWidgetItem(
                        result_item, ["Message", result.get("message", "N/A")]
                    )
                    QTreeWidgetItem(
                        result_item, ["Strategy", result.get("strategy_used", "N/A")]
                    )

        else:
            placeholder_item = QTreeWidgetItem(
                self.improvement_tree, ["Placeholder", ""]
            )
            QTreeWidgetItem(placeholder_item, ["Sample Area", "Sample Details"])

        self.improvement_tree.expandAll()
