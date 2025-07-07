import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QFileIconProvider,
    QFileSystemModel,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class FileExplorer(QWidget):
    """
    A file explorer widget for browsing and managing files with cyberpunk styling.
    """

    file_selected = Signal(str)
    directory_changed = Signal(str)

    def __init__(
        self, parent: Optional[QWidget] = None, default_path: Optional[str] = None
    ) -> None:
        """
        Initialize the FileExplorer widget.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            default_path (str, optional): Default directory path to display. Defaults to None.
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.default_path = default_path if default_path else str(Path.home())
        self.current_path = Path(self.default_path)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI components with a cyberpunk aesthetic."""
        self.setWindowTitle("Atlas File Explorer")
        layout = QVBoxLayout(self)

        # Navigation Bar
        nav_bar = QWidget()
        nav_layout = QHBoxLayout(nav_bar)
        self.path_input = QLineEdit(str(self.current_path))
        self.path_input.returnPressed.connect(self.on_path_entered)
        self.path_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        nav_layout.addWidget(QLabel("Path:"))
        nav_layout.addWidget(self.path_input)
        self.up_button = QPushButton("Up")
        self.up_button.clicked.connect(self.on_up_clicked)
        self.up_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)
        nav_layout.addWidget(self.up_button)
        layout.addWidget(nav_bar)

        # File Tree View
        self.model = QFileSystemModel()
        self.model.setRootPath(str(self.current_path))
        self.model.setIconProvider(QFileIconProvider())

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(str(self.current_path)))
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.clicked.connect(self.on_item_clicked)
        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QTreeView::item {
                border-bottom: 1px solid #333;
            }
            QTreeView::item:selected {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        layout.addWidget(self.tree_view)

        # Status Label
        self.status_label = QLabel(f"Current directory: {self.current_path}")
        self.status_label.setStyleSheet("color: #00ffaa; font-size: 12px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.apply_cyberpunk_style()

    def style_button(self, button: QPushButton) -> None:
        """Apply cyberpunk style to buttons."""
        button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        font = QFont("Courier New", 10)
        font.setBold(True)
        button.setFont(font)

    def style_line_edit(self, line_edit: QLineEdit) -> None:
        """Apply cyberpunk style to line edit."""
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
                padding: 0 5px;
            }
        """)
        font = QFont("Courier New", 10)
        line_edit.setFont(font)

    def apply_cyberpunk_style(self) -> None:
        """Apply overall cyberpunk styling to the file explorer widget."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0a0a0a"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#00ffaa"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#1a1a1a"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#00ffaa"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#1a1a1a"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#00ffaa"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#00ffaa"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        self.setPalette(palette)
        self.setStyleSheet("background-color: #0a0a0a;")

    @Slot()
    def on_up_clicked(self) -> None:
        """Navigate to the parent directory."""
        new_path = self.current_path.parent
        if new_path != self.current_path:
            self.update_path(new_path)
            self.logger.info("Navigating up to parent directory: %s", new_path)

    @Slot()
    def on_path_entered(self) -> None:
        """Load path from the input field."""
        path_text = self.path_input.text().strip()
        if path_text:
            new_path = Path(path_text)
            if new_path.exists() and new_path.is_dir():
                self.update_path(new_path)
                self.logger.info("Loading path from input: %s", path_text)
            else:
                self.logger.error("Invalid directory path: %s", path_text)
                self.status_label.setText(f"Invalid path: {path_text}")
        else:
            self.logger.warning("Empty path input")

    def update_path(self, new_path: Path) -> None:
        """Update the current path and refresh the view."""
        self.current_path = new_path
        self.path_input.setText(str(self.current_path))
        self.model.setRootPath(str(self.current_path))
        self.tree_view.setRootIndex(self.model.index(str(self.current_path)))
        self.status_label.setText(f"Current directory: {self.current_path}")
        self.directory_changed.emit(str(self.current_path))

    @Slot()
    def on_item_clicked(self) -> None:
        """Handle item click event."""
        index = self.tree_view.currentIndex()
        path = Path(self.model.filePath(index))
        if path.is_file():
            self.file_selected.emit(str(path))
            self.logger.info("Selected file: %s", path)
        else:
            self.status_label.setText(f"Selected: {path.name}")

    @Slot()
    def on_item_double_clicked(self) -> None:
        """Handle item double-click event."""
        index = self.tree_view.currentIndex()
        path = Path(self.model.filePath(index))
        if path.is_dir():
            self.update_path(path)
            self.logger.info("Double-clicked directory: %s", path)
        else:
            self.file_selected.emit(str(path))
            self.logger.info("Double-clicked file: %s", path)

    def set_directory(self, path: str) -> bool:
        """Set the current directory to display."""
        new_path = Path(path)
        if new_path.exists() and new_path.is_dir():
            self.update_path(new_path)
            self.logger.info("Set directory to: %s", path)
            return True
        return False
