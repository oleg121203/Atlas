"""
Memory Panel for Atlas AI Platform.

This module provides a PySide6-based memory management interface for viewing,
searching, and managing memory collections in the Atlas AI platform.
"""

from typing import Callable, List, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class MemoryPanel(QFrame):
    """
    Memory management panel with search, collection browsing, and content viewing.

    This panel provides functionality for:
    - Browsing memory collections
    - Searching memory content
    - Viewing memory data
    - Refreshing and clearing memory
    """

    # Signals for external communication
    search_requested = Signal(str)
    refresh_requested = Signal()
    clear_requested = Signal()
    collection_changed = Signal(str)

    def __init__(
        self,
        parent=None,
        collections: Optional[List[str]] = None,
        on_search: Optional[Callable[[str], None]] = None,
        on_refresh: Optional[Callable[[], None]] = None,
        on_clear: Optional[Callable[[], None]] = None,
    ):
        """
        Initialize the Memory Panel.

        Args:
            parent: Parent widget
            collections: List of available memory collections
            on_search: Callback for search operations
            on_refresh: Callback for refresh operations
            on_clear: Callback for clear operations
        """
        super().__init__(parent)

        self.collections = collections or []
        self.on_search = on_search
        self.on_refresh = on_refresh
        self.on_clear = on_clear

        self._setup_ui()
        self._connect_signals()
        self._apply_styling()

    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top section with collections and search
        top_frame = QFrame()
        top_layout = QGridLayout(top_frame)
        top_layout.setSpacing(10)

        # Collections section
        collections_label = QLabel("Collections:")
        collections_label.setStyleSheet("font-weight: bold;")
        top_layout.addWidget(collections_label, 0, 0)

        self.collections_combo = QComboBox()
        self.collections_combo.addItems(self.collections)
        self.collections_combo.setMinimumWidth(150)
        top_layout.addWidget(self.collections_combo, 1, 0)

        # Search section
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-weight: bold;")
        top_layout.addWidget(search_label, 0, 1)

        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(5)

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Enter search terms...")
        search_layout.addWidget(self.search_entry, 1)

        self.search_button = QPushButton("Search")
        self.search_button.setMinimumWidth(80)
        search_layout.addWidget(self.search_button)

        top_layout.addWidget(search_frame, 1, 1)

        # Make search column expandable
        top_layout.setColumnStretch(1, 1)

        layout.addWidget(top_frame)

        # Content viewing area
        content_label = QLabel("Memory Content:")
        content_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(content_label)

        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setPlaceholderText("Memory content will appear here...")
        layout.addWidget(self.content_display, 1)  # Stretch factor 1

        # Bottom button section
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch()  # Push buttons to the right

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setMinimumWidth(80)
        button_layout.addWidget(self.refresh_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setMinimumWidth(80)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(button_frame)

    def _connect_signals(self) -> None:
        """Connect internal signals to callbacks."""
        # Connect to internal methods
        self.search_button.clicked.connect(self._on_search)
        self.refresh_button.clicked.connect(self._on_refresh)
        self.clear_button.clicked.connect(self._on_clear)
        self.search_entry.returnPressed.connect(self._on_search)
        self.collections_combo.currentTextChanged.connect(self._on_collection_changed)

        # Connect to external callbacks
        if self.on_search:
            self.search_requested.connect(self.on_search)
        if self.on_refresh:
            self.refresh_requested.connect(self.on_refresh)
        if self.on_clear:
            self.clear_requested.connect(self.on_clear)

    def _apply_styling(self) -> None:
        """Apply cyberpunk-style styling to the panel."""
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 5px;
            }

            QLabel {
                color: #00ffff;
                font-size: 12px;
                font-weight: bold;
            }

            QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }

            QComboBox:hover {
                border-color: #00ffff;
            }

            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #ffffff;
                selection-background-color: #00ffff;
                selection-color: #000000;
            }

            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }

            QLineEdit:focus {
                border-color: #00ffff;
            }

            QPushButton {
                background-color: #2a2a2a;
                color: #00ffff;
                border: 1px solid #00ffff;
                border-radius: 3px;
                padding: 8px 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #3a3a3a;
                color: #ffffff;
            }

            QPushButton:pressed {
                background-color: #00ffff;
                color: #000000;
            }

            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Courier New', monospace;
            }

            QTextEdit:focus {
                border-color: #00ffff;
            }
        """)

    def _on_search(self) -> None:
        """Handle search button click or Enter key press."""
        search_text = self.search_entry.text().strip()
        if search_text:
            self.search_requested.emit(search_text)

    def _on_refresh(self) -> None:
        """Handle refresh button click."""
        self.refresh_requested.emit()

    def _on_clear(self) -> None:
        """Handle clear button click."""
        self.clear_requested.emit()
        self.content_display.clear()

    def _on_collection_changed(self, collection_name: str) -> None:
        """Handle collection selection change."""
        if collection_name:
            self.collection_changed.emit(collection_name)

    # Public API methods for external control

    def update_collections(self, collections: List[str]) -> None:
        """
        Update the available collections list.

        Args:
            collections: New list of collection names
        """
        self.collections = collections
        current_text = self.collections_combo.currentText()
        self.collections_combo.clear()
        self.collections_combo.addItems(collections)

        # Restore selection if it still exists
        if current_text in collections:
            self.collections_combo.setCurrentText(current_text)

    def set_content(self, content: str) -> None:
        """
        Set the content displayed in the memory viewer.

        Args:
            content: Text content to display
        """
        self.content_display.setPlainText(content)

    def append_content(self, content: str) -> None:
        """
        Append content to the memory viewer.

        Args:
            content: Text content to append
        """
        self.content_display.append(content)

    def get_selected_collection(self) -> str:
        """
        Get the currently selected collection.

        Returns:
            Name of the selected collection
        """
        return self.collections_combo.currentText()

    def get_search_text(self) -> str:
        """
        Get the current search text.

        Returns:
            Current search query text
        """
        return self.search_entry.text().strip()

    def clear_search(self) -> None:
        """Clear the search input field."""
        self.search_entry.clear()

    def set_search_text(self, text: str) -> None:
        """
        Set the search input text.

        Args:
            text: Text to set in search field
        """
        self.search_entry.setText(text)

    def enable_controls(self, enabled: bool = True) -> None:
        """
        Enable or disable all interactive controls.

        Args:
            enabled: Whether to enable (True) or disable (False) controls
        """
        self.collections_combo.setEnabled(enabled)
        self.search_entry.setEnabled(enabled)
        self.search_button.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
