#!/usr/bin/env python3
"""
Goal History Manager for Atlas

Manages and displays history of executed goals with ability to re-run them.
"""

import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

import customtkinter as ctk


class GoalHistoryManager:
    """Manages goal history storage and retrieval."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, "goal_history.json")
        self.history = self.load_history()

        #Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

    def load_history(self) -> List[Dict[str, Any]]:
        """Load goal history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading goal history: {e}")
                return []
        return []

    def save_history(self):
        """Save goal history to file."""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving goal history: {e}")

    def add_goal(self, goal_text: str, status: str = "Completed",
                execution_time: Optional[float] = None,
                steps_completed: Optional[int] = None,
                total_steps: Optional[int] = None,
                error_message: Optional[str] = None,
                metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add a new goal to history."""
        goal_entry = {
            "id": len(self.history) + 1,
            "goal": goal_text,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "execution_time": execution_time,
            "steps_completed": steps_completed,
            "total_steps": total_steps,
            "error_message": error_message,
            "metadata": metadata or {},
        }
        self.history.append(goal_entry)
        self.save_history()
        return goal_entry

    def get_goal_by_id(self, goal_id: int) -> Optional[Dict[str, Any]]:
        """Get a goal by its ID."""
        return next((g for g in self.history if g["id"] == goal_id), None)

    def search_goals(self, query: str) -> List[Dict[str, Any]]:
        """Search goals by text content."""
        query_lower = query.lower()
        return [
            goal for goal in self.history
            if query_lower in goal["goal"].lower()
        ]

    def filter_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Filter goals by status."""
        if status == "All":
            return self.history
        return [goal for goal in self.history if goal["status"] == status]

    def delete_goal(self, goal_id: int) -> bool:
        """Delete a goal from history."""
        original_length = len(self.history)
        self.history = [g for g in self.history if g["id"] != goal_id]
        if len(self.history) < original_length:
            self.save_history()
            return True
        return False

    def export_history(self, file_path: str):
        """Export history to a file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, default=str, ensure_ascii=False)


class GoalHistoryWindow:
    """Enhanced goal history window with search, filtering, and management capabilities."""

    def __init__(self, parent, goal_callback=None):
        self.parent = parent
        self.goal_callback = goal_callback  #Callback to execute selected goals

        #Create window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Goal History")
        self.window.geometry("1200x700")
        self.window.transient(parent)
        self.window.grab_set()

        #Initialize history manager
        self.history_manager = GoalHistoryManager()
        self.selected_goal = None

        self.setup_ui()
        self.refresh_history()

    def setup_ui(self):
        """Setup the goal history UI."""
        #Configure main grid
        self.window.grid_columnconfigure(0, weight=2)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        #Left panel - History list
        self.setup_history_list_panel()

        #Right panel - Goal details and actions
        self.setup_goal_details_panel()

    def setup_history_list_panel(self):
        """Setup the left panel with goal history list."""
        list_frame = ctk.CTkFrame(self.window)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(2, weight=1)

        #Title
        ctk.CTkLabel(list_frame, text="Goal History", font=("Arial", 16, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 5),
        )

        #Search and filter frame
        search_frame = ctk.CTkFrame(list_frame)
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="Search:").grid(row=0, column=0, padx=(10, 5), pady=5)

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="Search goals...")
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        self.filter_var = tk.StringVar(value="All")
        filter_combo = ctk.CTkComboBox(
            search_frame,
            variable=self.filter_var,
            values=["All", "Completed", "Failed", "In Progress", "Cancelled"],
            command=self.on_filter,
        )
        filter_combo.grid(row=0, column=2, padx=(5, 10), pady=5)

        #History tree frame
        tree_frame = ctk.CTkFrame(list_frame)
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        #Create Treeview
        columns = ("ID", "Goal", "Status", "Date", "Time", "Duration")
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)

        #Configure columns
        self.history_tree.heading("ID", text="ID")
        self.history_tree.heading("Goal", text="Goal")
        self.history_tree.heading("Status", text="Status")
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("Time", text="Time")
        self.history_tree.heading("Duration", text="Duration")

        self.history_tree.column("ID", width=50)
        self.history_tree.column("Goal", width=400)
        self.history_tree.column("Status", width=100)
        self.history_tree.column("Date", width=100)
        self.history_tree.column("Time", width=80)
        self.history_tree.column("Duration", width=80)

        #Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.history_tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.history_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        #Bind selection event
        self.history_tree.bind("<<TreeviewSelect>>", self.on_goal_select)
        self.history_tree.bind("<Double-1>", self.on_goal_double_click)

        #Bottom buttons
        buttons_frame = ctk.CTkFrame(list_frame)
        buttons_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkButton(
            buttons_frame,
            text="Refresh",
            command=self.refresh_history,
            width=80,
        ).pack(side="left", padx=5, pady=5)

        ctk.CTkButton(
            buttons_frame,
            text="Export",
            command=self.export_history,
            width=80,
        ).pack(side="left", padx=5, pady=5)

        ctk.CTkButton(
            buttons_frame,
            text="Clear All",
            command=self.clear_all_history,
            width=80,
            fg_color="darkred",
            hover_color="red",
        ).pack(side="right", padx=5, pady=5)

    def setup_goal_details_panel(self):
        """Setup the right panel with goal details."""
        details_frame = ctk.CTkFrame(self.window)
        details_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_rowconfigure(1, weight=1)

        #Title
        ctk.CTkLabel(details_frame, text="Goal Details", font=("Arial", 16, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 5),
        )

        #Goal text display
        text_frame = ctk.CTkFrame(details_frame)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        ctk.CTkLabel(text_frame, text="Goal Text:", font=("Arial", 12, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        self.goal_text = ctk.CTkTextbox(text_frame, height=200)
        self.goal_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        #Goal metadata
        meta_frame = ctk.CTkFrame(details_frame)
        meta_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        meta_frame.grid_columnconfigure(1, weight=1)

        #Status
        ctk.CTkLabel(meta_frame, text="Status:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=2,
        )
        self.status_label = ctk.CTkLabel(meta_frame, text="-")
        self.status_label.grid(row=0, column=1, sticky="w", padx=10, pady=2)

        #Execution time
        ctk.CTkLabel(meta_frame, text="Duration:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="w", padx=10, pady=2,
        )
        self.duration_label = ctk.CTkLabel(meta_frame, text="-")
        self.duration_label.grid(row=1, column=1, sticky="w", padx=10, pady=2)

        #Steps
        ctk.CTkLabel(meta_frame, text="Steps:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", padx=10, pady=2,
        )
        self.steps_label = ctk.CTkLabel(meta_frame, text="-")
        self.steps_label.grid(row=2, column=1, sticky="w", padx=10, pady=2)

        #Error message (if any)
        ctk.CTkLabel(meta_frame, text="Error:", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky="w", padx=10, pady=2,
        )
        self.error_label = ctk.CTkLabel(meta_frame, text="-", wraplength=200)
        self.error_label.grid(row=3, column=1, sticky="w", padx=10, pady=2)

        #Action buttons
        actions_frame = ctk.CTkFrame(details_frame)
        actions_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        self.rerun_button = ctk.CTkButton(
            actions_frame,
            text="Re-run Goal",
            command=self.rerun_goal,
            height=35,
            fg_color="green",
            hover_color="darkgreen",
        )
        self.rerun_button.pack(fill="x", pady=2)

        self.edit_run_button = ctk.CTkButton(
            actions_frame,
            text="Edit & Run",
            command=self.edit_and_run,
            height=35,
            fg_color="blue",
            hover_color="darkblue",
        )
        self.edit_run_button.pack(fill="x", pady=2)

        self.copy_button = ctk.CTkButton(
            actions_frame,
            text="Copy to Clipboard",
            command=self.copy_goal,
            height=35,
        )
        self.copy_button.pack(fill="x", pady=2)

        self.delete_button = ctk.CTkButton(
            actions_frame,
            text="Delete",
            command=self.delete_goal,
            height=35,
            fg_color="darkred",
            hover_color="red",
        )
        self.delete_button.pack(fill="x", pady=2)

        #Initially disable buttons
        self.update_button_states(False)

    def refresh_history(self):
        """Refresh the history display."""
        #Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        #Reload from file
        self.history_manager.load_history()

        #Apply filters
        search_term = self.search_var.get().lower()
        status_filter = self.filter_var.get()

        #Filter and display goals
        filtered_goals = self.history_manager.filter_by_status(status_filter)
        if search_term:
            filtered_goals = [g for g in filtered_goals if search_term in g["goal"].lower()]

        #Sort by timestamp (newest first)
        filtered_goals.sort(key=lambda x: x["timestamp"], reverse=True)

        for goal in filtered_goals:
            timestamp = datetime.fromisoformat(goal["timestamp"])
            date_str = timestamp.strftime("%Y-%m-%d")
            time_str = timestamp.strftime("%H:%M:%S")

            #Format duration
            duration_str = "-"
            if goal.get("execution_time"):
                duration_str = f"{goal['execution_time']:.1f}s"

            #Truncate goal text for display
            goal_display = goal["goal"][:60] + "..." if len(goal["goal"]) > 60 else goal["goal"]

            self.history_tree.insert("", "end", values=(
                goal["id"],
                goal_display,
                goal["status"],
                date_str,
                time_str,
                duration_str,
            ))

    def on_search(self, event):
        """Handle search input changes."""
        self.refresh_history()

    def on_filter(self, value):
        """Handle filter changes."""
        self.refresh_history()

    def on_goal_select(self, event):
        """Handle goal selection in the tree."""
        selection = self.history_tree.selection()
        if not selection:
            self.update_button_states(False)
            return

        item = self.history_tree.item(selection[0])
        goal_id = int(item["values"][0])

        self.selected_goal = self.history_manager.get_goal_by_id(goal_id)
        if self.selected_goal:
            self.update_goal_details()
            self.update_button_states(True)

    def on_goal_double_click(self, event):
        """Handle double-click on goal (re-run)."""
        if self.selected_goal:
            self.rerun_goal()

    def update_goal_details(self):
        """Update the goal details display."""
        if not self.selected_goal:
            return

        goal = self.selected_goal

        #Update goal text
        self.goal_text.delete(1.0, tk.END)
        self.goal_text.insert(1.0, goal["goal"])

        #Update metadata labels
        self.status_label.configure(text=goal["status"])

        #Duration
        if goal.get("execution_time"):
            duration_text = f"{goal['execution_time']:.2f} seconds"
        else:
            duration_text = "Unknown"
        self.duration_label.configure(text=duration_text)

        #Steps
        if goal.get("steps_completed") is not None and goal.get("total_steps") is not None:
            steps_text = f"{goal['steps_completed']}/{goal['total_steps']}"
        else:
            steps_text = "Unknown"
        self.steps_label.configure(text=steps_text)

        #Error message
        error_text = goal.get("error_message", "-") or "-"
        if len(error_text) > 50:
            error_text = error_text[:50] + "..."
        self.error_label.configure(text=error_text)

    def update_button_states(self, enabled: bool):
        """Enable/disable action buttons based on selection."""
        state = "normal" if enabled else "disabled"

        self.rerun_button.configure(state=state)
        self.edit_run_button.configure(state=state)
        self.copy_button.configure(state=state)
        self.delete_button.configure(state=state)

    def rerun_goal(self):
        """Re-run the selected goal."""
        if not self.selected_goal:
            return

        goal_text = self.selected_goal["goal"]
        self.window.destroy()

        #Call the callback to execute the goal
        if self.goal_callback:
            self.goal_callback(goal_text)
        else:
            #Fallback: show a message
            messagebox.showinfo("Goal History", f"Goal selected for execution:\n{goal_text[:100]}...")

    def edit_and_run(self):
        """Edit the goal text and then run it."""
        if not self.selected_goal:
            return

        #Get edited text
        goal_text = self.goal_text.get(1.0, tk.END).strip()

        if not goal_text:
            messagebox.showerror("Goal History", "Goal text cannot be empty!")
            return

        self.window.destroy()

        #Call the callback to execute the edited goal
        if self.goal_callback:
            self.goal_callback(goal_text)
        else:
            #Fallback: show a message
            messagebox.showinfo("Goal History", f"Edited goal selected for execution:\n{goal_text[:100]}...")

    def copy_goal(self):
        """Copy the goal text to clipboard."""
        if not self.selected_goal:
            return

        goal_text = self.goal_text.get(1.0, tk.END).strip()
        self.window.clipboard_clear()
        self.window.clipboard_append(goal_text)
        messagebox.showinfo("Goal History", "Goal text copied to clipboard!")

    def delete_goal(self):
        """Delete the selected goal from history."""
        if not self.selected_goal:
            return

        result = messagebox.askyesno(
            "Delete Goal",
            f"Are you sure you want to delete this goal from history?\n\nGoal: {self.selected_goal['goal'][:100]}...",
        )

        if result:
            if self.history_manager.delete_goal(self.selected_goal["id"]):
                self.selected_goal = None
                self.refresh_history()

                #Clear details
                self.goal_text.delete(1.0, tk.END)
                self.status_label.configure(text="-")
                self.duration_label.configure(text="-")
                self.steps_label.configure(text="-")
                self.error_label.configure(text="-")
                self.update_button_states(False)

                messagebox.showinfo("Goal History", "Goal deleted successfully!")
            else:
                messagebox.showerror("Goal History", "Failed to delete goal!")

    def export_history(self):
        """Export goal history to a file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Goal History",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if file_path:
            try:
                self.history_manager.export_history(file_path)
                messagebox.showinfo("Export", f"Goal history exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export history:\n{e}")

    def clear_all_history(self):
        """Clear all goal history."""
        result = messagebox.askyesno(
            "Clear All History",
            "Are you sure you want to delete ALL goal history?\nThis action cannot be undone!",
        )

        if result:
            try:
                self.history_manager.history = []
                self.history_manager.save_history()
                self.refresh_history()

                #Clear details
                self.selected_goal = None
                self.goal_text.delete(1.0, tk.END)
                self.status_label.configure(text="-")
                self.duration_label.configure(text="-")
                self.steps_label.configure(text="-")
                self.error_label.configure(text="-")
                self.update_button_states(False)

                messagebox.showinfo("Clear History", "All goal history cleared!")
            except Exception as e:
                messagebox.showerror("Clear History", f"Failed to clear history:\n{e}")
