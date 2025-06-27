#!/usr/bin/env python3
"""
Script to help migrate UI components from tkinter/customtkinter to PySide6.
"""

import os
import shutil
from pathlib import Path


def backup_tkinter_files():
    """Move tkinter-based files to backup directory."""
    ui_dir = Path(__file__).parent.parent / "ui"
    backup_dir = Path(__file__).parent.parent / "backup_ui"

    # Files that use tkinter/customtkinter
    tkinter_files = [
        "agent_list_panel.py",
        "log_panel.py",
        "nl_workflow_ui.py",
        "tool_management_view.py",
        "performance_panel.py",
        "plugin_manager_panel.py",
        "chat_history_view.py",
        "goal_history.py",
        "tools_panel.py",
        "fallback_chain_editor.py",
        "context_menu.py",
        "command_palette.py",
        "plan_view.py",
        "tooltip.py",
        "hierarchical_task_view.py",
        "master_agent_panel.py",
        "chat_panel.py",
        "enhanced_settings.py",
        "settings_panel.py",
        "enhanced_settings_panel.py",
        "memory_panel.py",
        "security_panel.py",
        "system_control_panel.py",
        "chat_input_panel.py",
        "enhanced_plugin_manager.py",
        "tasks_panel.py",
        "status_panel.py",
    ]

    # Create backup directory if it doesn't exist
    backup_dir.mkdir(exist_ok=True)

    # Move files to backup
    for file in tkinter_files:
        src = ui_dir / file
        dst = backup_dir / file
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"Moved {file} to backup")


def create_pyside6_templates():
    """Create template files for PySide6 versions of the UI components."""
    ui_dir = Path(__file__).parent.parent / "ui"

    # Basic PySide6 widget template
    widget_template = '''"""
{description}
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout

class {classname}(QWidget):
    """PySide6 implementation of {classname}."""

    def __init__(self, parent=None):
        """Initialize the widget."""
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        # TODO: Implement PySide6 version of the UI
'''

    # Files to create
    components = [
        ("AgentListPanel", "Panel for displaying and managing agents"),
        ("LogPanel", "Panel for displaying log messages"),
        ("WorkflowUI", "Natural language workflow interface"),
        ("ToolManagementView", "View for managing tools"),
        # ... add other components
    ]

    for classname, description in components:
        filename = f"{classname.lower()}.py"
        filepath = ui_dir / filename

        if not filepath.exists():
            with open(filepath, "w") as f:
                f.write(
                    widget_template.format(classname=classname, description=description)
                )
            print(f"Created PySide6 template for {filename}")


if __name__ == "__main__":
    backup_tkinter_files()
    create_pyside6_templates()
