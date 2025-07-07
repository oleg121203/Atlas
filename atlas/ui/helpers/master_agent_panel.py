"""Master Agent Panel component for Atlas."""

import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MasterAgentPanel(QWidget):
    """Panel for managing master agents in Atlas with cyberpunk styling."""

    agent_selected = Signal(str)
    agent_activated = Signal(str)
    add_agent = Signal()
    remove_agent = Signal(str)

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
        self.logger.info("MasterAgentPanel component initialized")

    def initialize_ui(self) -> None:
        """Initialize the UI components for the master agent panel."""
        layout = QVBoxLayout(self)

        header_label = QLabel("Master Agents")
        header_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #00ffaa;"
        )
        layout.addWidget(header_label)

        self.agent_list = QListWidget()
        self.agent_list.itemClicked.connect(self.on_agent_selected)
        self.agent_list.itemActivated.connect(self.on_agent_activated)
        layout.addWidget(self.agent_list)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Agent")
        self.add_button.clicked.connect(self.on_add_agent)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Agent")
        self.remove_button.clicked.connect(self.on_remove_agent)
        button_layout.addWidget(self.remove_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def update_agents(self, agents: List[Dict[str, Any]]) -> None:
        """Update the list of master agents.

        Args:
            agents (List[Dict[str, Any]]): List of agent dictionaries.
        """
        self.agent_list.clear()
        for agent in agents:
            agent_name = agent.get("name", "Unnamed Agent")
            agent_id = agent.get("id", agent_name)
            item = QListWidgetItem(agent_name)
            item.setData(Qt.ItemDataRole.UserRole, agent_id)
            self.agent_list.addItem(item)
            self.logger.debug(f"Added agent to list: {agent_name}")
        self.logger.info(f"Updated agent list with {len(agents)} agents")

    @Slot()
    def on_add_agent(self) -> None:
        """Handle add agent button click."""
        self.add_agent.emit()
        self.logger.info("Add agent requested")

    @Slot()
    def on_remove_agent(self) -> None:
        """Handle remove agent button click."""
        selected_items = self.agent_list.selectedItems()
        if selected_items:
            agent_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.remove_agent.emit(agent_id)
            self.logger.info(f"Remove agent requested: {agent_id}")

    @Slot(QListWidgetItem)
    def on_agent_selected(self, item: QListWidgetItem) -> None:
        """Handle agent selection event.

        Args:
            item (QListWidgetItem): The selected item.
        """
        agent_id = item.data(Qt.ItemDataRole.UserRole)
        self.agent_selected.emit(agent_id)
        self.logger.info(f"Selected agent: {agent_id}")

    @Slot(QListWidgetItem)
    def on_agent_activated(self, item: QListWidgetItem) -> None:
        """Handle agent activation event.

        Args:
            item (QListWidgetItem): The activated item.
        """
        agent_id = item.data(Qt.ItemDataRole.UserRole)
        self.agent_activated.emit(agent_id)
        self.logger.info(f"Activated agent: {agent_id}")
