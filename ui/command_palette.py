from typing import Dict, List, Any, Optional
import tkinter as tk
from tkinter import ttk
import json

class CommandPalette:
    """Class to manage a floating command palette with contextual suggestions"""
    
    def __init__(self, root, command_data: Optional[Dict[str, Any]] = None):
        """Initialize the command palette
        
        Args:
            root: Tkinter root window or parent widget
            command_data (Optional[Dict[str, Any]]): Predefined command data
        """
        self.root = root
        self.command_data = command_data or self._load_default_commands()
        self.window = None
        self.entry = None
        self.suggestions_listbox = None
        self.filtered_commands = []
        self.is_visible = False
        
    def _load_default_commands(self) -> Dict[str, Any]:
        """Load default command data
        
        Returns:
            Dict[str, Any]: Default command structure
        """
        # Default commands - would be loaded from config or database in real implementation
        return {
            "commands": [
                {"name": "Create Workflow", "action": "create_workflow", "category": "Workflow", "shortcut": "Ctrl+Shift+W"},
                {"name": "Open Dashboard", "action": "open_dashboard", "category": "Navigation", "shortcut": "Ctrl+D"},
                {"name": "Start Task", "action": "start_task", "category": "Task", "shortcut": "Ctrl+T"},
                {"name": "Save Current Workflow", "action": "save_workflow", "category": "Workflow", "shortcut": "Ctrl+S"},
                {"name": "Publish Workflow", "action": "publish_workflow", "category": "Workflow", "shortcut": "Ctrl+P"},
                {"name": "Switch Theme", "action": "switch_theme", "category": "UI", "shortcut": "Ctrl+Alt+T"},
                {"name": "Settings", "action": "open_settings", "category": "Navigation", "shortcut": "Ctrl+,"}
            ],
            "contextual": [
                {"context": "workflow_editor", "commands": ["Save Current Workflow", "Publish Workflow"]},
                {"context": "dashboard_view", "commands": ["Open Dashboard", "Switch Theme"]},
                {"context": "task_list", "commands": ["Start Task"]}
            ]
        }
        
    def show(self, context: Optional[str] = None, x: Optional[int] = None, y: Optional[int] = None):
        """Show the command palette
        
        Args:
            context (Optional[str]): Current context for contextual suggestions
            x (Optional[int]): X position for window placement
            y (Optional[int]): Y position for window placement
        """
        if self.is_visible:
            return
            
        self.is_visible = True
        self.window = tk.Toplevel(self.root)
        self.window.title("Command Palette")
        self.window.geometry("400x300")
        if x is not None and y is not None:
            self.window.geometry(f"+{x}+{y}")
        self.window.transient(self.root)
        self.window.grab_set()
        
        # Make window always on top
        self.window.attributes('-topmost', True)
        
        # Search entry
        self.entry = ttk.Entry(self.window)
        self.entry.pack(padx=5, pady=5, fill=tk.X)
        self.entry.bind("<KeyRelease>", self._on_entry_change)
        self.entry.bind("<Return>", self._on_select_command)
        self.entry.bind("<Down>", self._move_selection_down)
        self.entry.bind("<Up>", self._move_selection_up)
        self.entry.focus()
        
        # Suggestions listbox
        self.suggestions_listbox = tk.Listbox(self.window, height=10)
        self.suggestions_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.suggestions_listbox.bind("<Return>", self._on_select_command)
        
        # Update suggestions based on context
        self._update_suggestions(context)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
    def hide(self):
        """Hide the command palette"""
        if not self.is_visible:
            return
            
        self.is_visible = False
        if self.window:
            self.window.destroy()
            self.window = None
        
    def _update_suggestions(self, context: Optional[str] = None, search_text: str = ""):
        """Update the list of suggested commands
        
        Args:
            context (Optional[str]): Current context for filtering
            search_text (str): Text to filter commands by
        """
        self.suggestions_listbox.delete(0, tk.END)
        self.filtered_commands = []
        
        # Get contextual commands if context is provided
        contextual_commands = []
        if context:
            for ctx in self.command_data.get("contextual", []):
                if ctx.get("context") == context:
                    contextual_commands = ctx.get("commands", [])
                    break
        
        # Filter commands based on search text and context
        search_text = search_text.lower()
        for cmd in self.command_data.get("commands", []):
            cmd_name = cmd.get("name", "").lower()
            if search_text in cmd_name or not search_text:
                if not contextual_commands or cmd.get("name") in contextual_commands:
                    self.filtered_commands.append(cmd)
                    display_text = f"{cmd['name']} ({cmd.get('shortcut', 'No shortcut')})"
                    self.suggestions_listbox.insert(tk.END, display_text)
        
        if self.filtered_commands:
            self.suggestions_listbox.select_set(0)
            
    def _on_entry_change(self, event):
        """Handle changes in the search entry
        
        Args:
            event: Tkinter event object
        """
        search_text = self.entry.get()
        self._update_suggestions(search_text=search_text)
        
    def _move_selection_down(self, event):
        """Move selection down in the listbox
        
        Args:
            event: Tkinter event object
        """
        current_selection = self.suggestions_listbox.curselection()
        if not current_selection:
            return
        index = current_selection[0]
        if index < self.suggestions_listbox.size() - 1:
            self.suggestions_listbox.selection_clear(index)
            self.suggestions_listbox.selection_set(index + 1)
            self.suggestions_listbox.see(index + 1)
        return 'break'  # Prevent default behavior
        
    def _move_selection_up(self, event):
        """Move selection up in the listbox
        
        Args:
            event: Tkinter event object
        """
        current_selection = self.suggestions_listbox.curselection()
        if not current_selection:
            return
        index = current_selection[0]
        if index > 0:
            self.suggestions_listbox.selection_clear(index)
            self.suggestions_listbox.selection_set(index - 1)
            self.suggestions_listbox.see(index - 1)
        return 'break'  # Prevent default behavior
        
    def _on_select_command(self, event=None):
        """Handle selection of a command
        
        Args:
            event: Tkinter event object (optional)
        """
        selection = self.suggestions_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if 0 <= index < len(self.filtered_commands):
            command = self.filtered_commands[index]
            print(f"Executing command: {command['name']} (action: {command['action']})")
            self._execute_command(command)
            self.hide()
        
    def _execute_command(self, command: Dict[str, Any]):
        """Execute the selected command
        
        Args:
            command (Dict[str, Any]): Command to execute
        """
        # Placeholder for actual command execution - would integrate with Atlas system
        print(f"Command execution placeholder: {command['action']}")
        # In a real implementation, this would trigger the appropriate action
