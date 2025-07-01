from PySide6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget


class DecisionUI(QWidget):
    """UI component for displaying and interacting with decision engine data."""

    def __init__(self, decision_engine=None, parent: QWidget | None = None):
        super().__init__(parent)
        self.decision_engine = decision_engine
        self.init_ui()
        self.connect_to_engine()

    def init_ui(self) -> None:
        """Initialize the UI layout and components."""
        layout = QVBoxLayout(self)

        title_label = QLabel("Decision Engine")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ffaa;")
        layout.addWidget(title_label)

        self.decision_tree = QTreeWidget()
        self.decision_tree.setHeaderLabels(["Decision Factor", "Value"])
        self.decision_tree.setStyleSheet(
            "background-color: #1a1a1a; color: #ffffff; border: 1px solid #00ffaa;"
        )
        layout.addWidget(self.decision_tree)

        self.setLayout(layout)
        self.update_decision_display()

    def connect_to_engine(self):
        """Connect to the decision engine signals to update UI on changes."""
        if self.decision_engine:
            self.decision_engine.decision_made.connect(self.on_decision_made)
            self.decision_engine.decision_factors_updated.connect(
                self.on_factors_updated
            )

    def on_decision_made(self, decision: dict):
        """Handle new decision made by the engine.

        Args:
            decision: Dictionary containing decision details.
        """
        self.update_decision_display()

    def on_factors_updated(self, factors: dict):
        """Handle updates to decision factors.

        Args:
            factors: Dictionary containing updated decision factors.
        """
        self.update_decision_display()

    def update_decision_display(self) -> None:
        """Update the tree widget with the latest decision engine data."""
        self.decision_tree.clear()

        if self.decision_engine:
            # Display current decision factors
            factors = self.decision_engine.decision_factors
            for factor_type, factor_data in factors.items():
                type_item = QTreeWidgetItem(self.decision_tree, [factor_type, ""])
                if isinstance(factor_data, dict):
                    for key, value in factor_data.items():
                        QTreeWidgetItem(type_item, [str(key), str(value)])
                else:
                    QTreeWidgetItem(type_item, ["Value", str(factor_data)])

            # Display decision history if available
            history = self.decision_engine.get_decision_history()
            if history:
                history_item = QTreeWidgetItem(
                    self.decision_tree, ["Decision History", ""]
                )
                for i, decision in enumerate(history[:5]):  # Limit to last 5 decisions
                    decision_text = (
                        f"Decision {i + 1}: {decision.get('goal', 'Unknown')}"
                    )
                    decision_item = QTreeWidgetItem(history_item, [decision_text, ""])
                    QTreeWidgetItem(
                        decision_item, ["Action", decision.get("decision", "N/A")]
                    )
                    QTreeWidgetItem(
                        decision_item,
                        ["Confidence", str(decision.get("confidence", "N/A"))],
                    )
                    QTreeWidgetItem(
                        decision_item,
                        ["Strategy", decision.get("strategy_used", "N/A")],
                    )

        else:
            type_item = QTreeWidgetItem(self.decision_tree, ["Placeholder", ""])
            QTreeWidgetItem(type_item, ["Sample Factor", "Sample Value"])

        self.decision_tree.expandAll()
