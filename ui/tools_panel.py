import customtkinter as ctk

from ui.tool_management_view import ToolManagementView
from ui.tooltip import Tooltip


class ToolsPanel(ctk.CTkFrame):
    def __init__(self, master, agent_manager, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.agent_manager = agent_manager
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.tool_management_view = ToolManagementView(self, self.agent_manager)
        self.tool_management_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        # Add tooltip to tool management view (if it has a main button or area)
        if hasattr(self.tool_management_view, "refresh_button"):
            Tooltip(
                self.tool_management_view.refresh_button,
                "Refresh the list of available tools",
            )
        # Add tooltip to the panel itself
        Tooltip(self, "Manage and explore all available tools in Atlas")

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
