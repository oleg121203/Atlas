from PySide6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from core.intelligence.context_engine import ContextEngine


class ContextUI(QWidget):
    """UI component for displaying and interacting with context data."""

    def __init__(self, context_engine: ContextEngine, parent: QWidget | None = None):
        super().__init__(parent)
        self.context_engine = context_engine
        self.init_ui()
        self.context_engine.register_listener("ui_update", self.on_context_updated)

    def init_ui(self) -> None:
        """Initialize the UI layout and components."""
        layout = QVBoxLayout(self)
        title_label = QLabel("Context Awareness Engine")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ffaa;")
        layout.addWidget(title_label)
        self.context_tree = QTreeWidget()
        self.context_tree.setHeaderLabels(["Context Type", "Value"])
        self.context_tree.setStyleSheet(
            "background-color: #1a1a1a; color: #ffffff; border: 1px solid #00ffaa;"
        )
        layout.addWidget(self.context_tree)
        self.setLayout(layout)
        self.update_context_display()

    def on_context_updated(self, context_type: str, data: dict) -> None:
        """Callback for when context data is updated."""
        self.update_context_display()

    def update_context_display(self) -> None:
        """Update the tree widget with the latest context data."""
        self.context_tree.clear()
        for context_type, data in self.context_engine.get_contexts().items():
            type_item = QTreeWidgetItem(self.context_tree, [context_type, ""])
            for key, value in data.items():
                QTreeWidgetItem(type_item, [str(key), str(value)])
        self.context_tree.expandAll()
