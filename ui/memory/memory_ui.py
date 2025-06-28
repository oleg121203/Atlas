from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.memory.chromadb_manager import ChromaDBManager


class MemoryUI(QWidget):
    """UI component for managing memory interactions with ChromaDB."""

    def __init__(self, memory_manager: ChromaDBManager, parent: QWidget | None = None):
        super().__init__(parent)
        self.memory_manager = memory_manager
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI layout and components."""
        layout = QVBoxLayout(self)

        title_label = QLabel("Memory Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ffaa;")
        layout.addWidget(title_label)

        self.memory_tree = QTreeWidget()
        self.memory_tree.setHeaderLabels(["Collection", "Item ID", "Details"])
        self.memory_tree.setStyleSheet(
            "background-color: #1a1a1a; color: #ffffff; border: 1px solid #00ffaa;"
        )
        layout.addWidget(self.memory_tree)

        input_layout = QHBoxLayout()
        self.collection_input = QLineEdit()
        self.collection_input.setPlaceholderText("Collection Name")
        self.collection_input.setStyleSheet(
            "background-color: #2a2a2a; color: #ffffff; border: 1px solid #00ffaa; padding: 5px;"
        )
        input_layout.addWidget(self.collection_input)

        self.create_button = QPushButton("Create Collection")
        self.create_button.setStyleSheet(
            "background-color: #00ffaa; color: #000000; padding: 5px;"
        )
        self.create_button.clicked.connect(self.create_collection)
        input_layout.addWidget(self.create_button)

        self.delete_button = QPushButton("Delete Collection")
        self.delete_button.setStyleSheet(
            "background-color: #ff3366; color: #ffffff; padding: 5px;"
        )
        self.delete_button.clicked.connect(self.delete_collection)
        input_layout.addWidget(self.delete_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)
        self.update_memory_display()

    def create_collection(self) -> None:
        """Create a new collection in ChromaDB."""
        collection_name = self.collection_input.text().strip()
        if collection_name:
            success = self.memory_manager.create_collection(collection_name)
            if success:
                self.update_memory_display()
                self.collection_input.clear()

    def delete_collection(self) -> None:
        """Delete a selected collection from ChromaDB."""
        selected_item = self.memory_tree.currentItem()
        if selected_item and selected_item.parent() is None:
            collection_name = selected_item.text(0)
            success = self.memory_manager.delete_collection(collection_name)
            if success:
                self.update_memory_display()

    def update_memory_display(self) -> None:
        """Update the tree widget with the latest memory collections and items."""
        self.memory_tree.clear()

        for collection_name in self.memory_manager.collections:
            collection_item = QTreeWidgetItem(
                self.memory_tree, [collection_name, "", ""]
            )
            collection = self.memory_manager.get_collection(collection_name)
            if collection:
                try:
                    # Retrieve actual items from the collection
                    items = collection.get(include=["metadatas", "documents"])
                    item_ids = items.get("ids", [])
                    metadatas = items.get("metadatas", [])
                    documents = items.get("documents", [])

                    for i, (item_id, metadata, document) in enumerate(zip(item_ids, metadatas, documents)):
                        if i >= 10:  # Limit to first 10 items for performance
                            QTreeWidgetItem(
                                collection_item, ["", "...", f"+ {len(item_ids) - 10} more items"]
                            )
                            break
                        detail_text = str(metadata) if metadata else "No metadata"
                        item_item = QTreeWidgetItem(
                            collection_item, ["", str(item_id), detail_text]
                        )
                        if document:
                            QTreeWidgetItem(item_item, ["Document", str(document)[:100]])
                except Exception as e:
                    QTreeWidgetItem(collection_item, ["", "Error", str(e)])

        self.memory_tree.expandAll()
