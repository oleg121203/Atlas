"""Command Palette component for Atlas."""

import logging
from typing import Callable, List, Optional, Tuple

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)


class CommandPalette(QDialog):
    """Command palette for quick actions and commands in Atlas with cyberpunk styling."""

    command_selected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setWindowTitle("Command Palette")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                border-radius: 3px;
            }
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
                padding: 5px;
            }
            QListWidget {
                background-color: #1a1a1a;
                color: #00ffaa;
                border: 1px solid #00ffaa;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #00ffaa;
                color: #000000;
            }
        """)
        self.resize(400, 300)
        self.initialize_ui()
        self.commands: List[Tuple[str, Callable[[], None]]] = []
        self.logger.info("CommandPalette component initialized")

    def initialize_ui(self) -> None:
        """Initialize the UI components for the command palette."""
        layout = QVBoxLayout(self)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command...")
        self.input_field.textChanged.connect(self.filter_commands)
        self.input_field.returnPressed.connect(self.execute_command)
        layout.addWidget(self.input_field)

        self.command_list = QListWidget()
        self.command_list.itemActivated.connect(self.on_command_activated)
        layout.addWidget(self.command_list)

        self.setLayout(layout)

    def set_commands(self, commands: List[Tuple[str, Callable[[], None]]]) -> None:
        """Set the list of available commands.

        Args:
            commands (List[Tuple[str, Callable[[], None]]]): List of tuples with command text and callback.
        """
        self.commands = commands
        self.update_command_list()
        self.logger.debug(f"Set {len(commands)} commands in the palette")

    def update_command_list(self, filter_text: str = "") -> None:
        """Update the command list, optionally filtering by text.

        Args:
            filter_text (str, optional): Text to filter commands by. Defaults to "".
        """
        self.command_list.clear()
        filter_text = filter_text.lower()
        for command_text, _ in self.commands:
            if not filter_text or filter_text in command_text.lower():
                item = QListWidgetItem(command_text)
                self.command_list.addItem(item)
        self.logger.debug(f"Updated command list with filter: {filter_text}")

    @Slot(str)
    def filter_commands(self, text: str) -> None:
        """Filter commands based on the input text.

        Args:
            text (str): The text to filter by.
        """
        self.update_command_list(text)

    def show_palette(self) -> None:
        """Show the command palette."""
        self.input_field.clear()
        self.update_command_list()
        self.input_field.setFocus()
        self.show()
        self.logger.debug("Showing command palette")

    @Slot()
    def execute_command(self) -> None:
        """Execute the currently selected command or the first in the filtered list."""
        selected_items = self.command_list.selectedItems()
        if selected_items:
            command_text = selected_items[0].text()
            for cmd_text, callback in self.commands:
                if cmd_text == command_text:
                    callback()
                    self.command_selected.emit(command_text)
                    self.close()
                    self.logger.info(f"Executed command: {command_text}")
                    return
        elif self.command_list.count() > 0:
            command_text = self.command_list.item(0).text()
            for cmd_text, callback in self.commands:
                if cmd_text == command_text:
                    callback()
                    self.command_selected.emit(command_text)
                    self.close()
                    self.logger.info(f"Executed first command: {command_text}")
                    return
        self.logger.warning("No command executed")

    @Slot(QListWidgetItem)
    def on_command_activated(self, item: QListWidgetItem) -> None:
        """Handle activation of a command item.

        Args:
            item (QListWidgetItem): The activated item.
        """
        command_text = item.text()
        for cmd_text, callback in self.commands:
            if cmd_text == command_text:
                callback()
                self.command_selected.emit(command_text)
                self.close()
                self.logger.info(f"Activated command: {command_text}")
                return
        self.logger.warning(f"Command not found: {command_text}")
