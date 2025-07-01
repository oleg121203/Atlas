"""
Panel for displaying and managing agents.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.module_communication import EVENT_BUS


class AgentListPanel(QWidget):
    """PySide6 implementation of agent list panel."""

    def __init__(
        self, parent=None, agents=None, on_start_agent=None, on_stop_agent=None
    ):
        """Initialize the panel.

        Args:
            parent: Parent widget
            agents: Dictionary of agents
            on_start_agent: Callback for starting an agent
            on_stop_agent: Callback for stopping an agent
        """
        super().__init__(parent)
        self.agents = agents or {}
        self.on_start_agent = on_start_agent
        self.on_stop_agent = on_stop_agent
        self.event_bus = EVENT_BUS
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Header
        header = QLabel("Agents")
        header.setStyleSheet("font-weight: bold;")
        layout.addWidget(header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container for agents
        self.agents_container = QWidget()
        self.agents_layout = QVBoxLayout(self.agents_container)
        scroll.setWidget(self.agents_container)

        layout.addWidget(scroll)
        self.populate_agents()

    def populate_agents(self):
        """Populate the list with agents."""
        # Clear existing widgets
        while self.agents_layout.count():
            child = self.agents_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add agents
        for agent_id, agent in self.agents.items():
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)

            frame_layout = QHBoxLayout(frame)
            frame_layout.setContentsMargins(5, 5, 5, 5)

            # Agent ID
            id_label = QLabel(agent_id)
            id_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            frame_layout.addWidget(id_label)

            # Status
            status = getattr(agent, "status", "Unknown")
            status_label = QLabel(f"Status: {status}")
            frame_layout.addWidget(status_label)

            frame_layout.addStretch()

            # Control buttons            # Control buttons
            if self.on_stop_agent is not None:
                stop_btn = QPushButton("Stop")
                stop_btn.setFixedWidth(60)
                stop_btn.clicked.connect(
                    lambda checked, aid=agent_id: self._on_stop_agent(aid)
                )
                frame_layout.addWidget(stop_btn)

            if self.on_start_agent is not None:
                start_btn = QPushButton("Start")
                start_btn.setFixedWidth(60)
                start_btn.clicked.connect(
                    lambda checked, aid=agent_id: self._on_start_agent(aid)
                )
                frame_layout.addWidget(start_btn)

            self.agents_layout.addWidget(frame)

        # Add stretch at the end to push all items to the top
        self.agents_layout.addStretch()

    def update_agents(self, agents):
        """Update the agents dictionary and refresh the display.

        Args:
            agents: New dictionary of agents
        """
        self.agents = agents
        self.populate_agents()

    def _on_start_agent(self, agent_id):
        """Handle start agent button click.

        Args:
            agent_id: ID of the agent to start
        """
        if self.on_start_agent is not None:
            self.on_start_agent(agent_id)

    def _on_stop_agent(self, agent_id):
        """Handle stop agent button click.

        Args:
            agent_id: ID of the agent to stop
        """
        if self.on_stop_agent is not None:
            self.on_stop_agent(agent_id)
