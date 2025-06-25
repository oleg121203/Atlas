#!/usr/bin/env python3
"""
Status Panel for Atlas

Real-time status display showing agent activity, progress, and logs.
"""

import tkinter as tk
from datetime import datetime
from typing import Any, Dict, Optional

import customtkinter as ctk


class StatusPanel(ctk.CTkFrame):
    """Enhanced real-time status display for Atlas agents."""

    def __init__(self, parent):
        print("[LOG] StatusPanel: __init__ called")
        super().__init__(parent)
        self.status_data = {
            "agent_status": "Idle",
            "current_action": "None",
            "progress": 0,
            "last_update": datetime.now(),
            "errors": [],
            "sub_agents": {},
        }
        self.setup_ui()

    def setup_ui(self):
        """Setup the status panel UI components."""
        #Configure grid
        self.grid_columnconfigure(0, weight=1)

        #Status indicator frame
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.status_frame.grid_columnconfigure(1, weight=1)

        #Status labels
        ctk.CTkLabel(self.status_frame, text="Agent Status:", font=("Arial", 14, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=5,
        )

        self.status_label = ctk.CTkLabel(self.status_frame, text="Idle", font=("Arial", 12))
        self.status_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(self.status_frame, text="Current Action:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="w", padx=10, pady=2,
        )

        self.action_label = ctk.CTkLabel(self.status_frame, text="None", font=("Arial", 11))
        self.action_label.grid(row=1, column=1, sticky="w", padx=10, pady=2)

        #Progress bar
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.progress_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.progress_frame, text="Progress:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=5,
        )

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        self.progress_bar.set(0)

        #Sub-agents status
        self.sub_agents_frame = ctk.CTkFrame(self)
        self.sub_agents_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(self.sub_agents_frame, text="Sub-Agents Status", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=5,
        )

        self.sub_agents_labels = {}

        #Real-time log frame
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self.log_frame, text="Real-time Activity Log", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=5,
        )

        #Create a frame for the text widget and scrollbar
        text_frame = ctk.CTkFrame(self.log_frame)
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        #Use tkinter Text widget for better control
        self.log_text = tk.Text(
            text_frame,
            height=10,
            wrap="word",
            bg="#2b2b2b",
            fg="#ffffff",
            insertbackground="#ffffff",
            font=("Consolas", 10),
        )

        #Scrollbar for log
        log_scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

        #Configure text tags for colored output
        self.log_text.tag_configure("ERROR", foreground="#ff6b6b")
        self.log_text.tag_configure("WARNING", foreground="#ffa500")
        self.log_text.tag_configure("SUCCESS", foreground="#51cf66")
        self.log_text.tag_configure("INFO", foreground="#74c0fc")

        #Clear log button
        clear_button = ctk.CTkButton(
            self.log_frame,
            text="Clear Log",
            command=self.clear_log,
            width=100,
            height=30,
        )
        clear_button.pack(anchor="e", padx=10, pady=(0, 10))

    def update_status(self, status: str, action: Optional[str] = None, progress: Optional[float] = None):
        """Update the main agent status."""
        self.status_data["agent_status"] = status
        if action:
            self.status_data["current_action"] = action
        if progress is not None:
            self.status_data["progress"] = max(0, min(100, progress))
        self.status_data["last_update"] = datetime.now()

        #Update UI elements
        self.status_label.configure(text=status)
        self.action_label.configure(text=self.status_data["current_action"])
        self.progress_bar.set(self.status_data["progress"] / 100.0)

    def update_sub_agent_status(self, agent_name: str, status: str):
        """Update status for a specific sub-agent."""
        self.status_data["sub_agents"][agent_name] = {
            "status": status,
            "last_update": datetime.now(),
        }

        #Update or create label for this sub-agent
        if agent_name not in self.sub_agents_labels:
            label_frame = ctk.CTkFrame(self.sub_agents_frame)
            label_frame.pack(fill="x", padx=10, pady=2)

            name_label = ctk.CTkLabel(label_frame, text=f"{agent_name}:", font=("Arial", 10, "bold"))
            name_label.pack(side="left", padx=5)

            status_label = ctk.CTkLabel(label_frame, text=status, font=("Arial", 10))
            status_label.pack(side="left", padx=5)

            self.sub_agents_labels[agent_name] = status_label
        else:
            self.sub_agents_labels[agent_name].configure(text=status)

    def add_log_entry(self, message: str, level: str = "INFO", source: str = "Agent"):
        """Add a new entry to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {source}: {message}\n"

        #Insert at end and scroll to bottom
        self.log_text.insert(tk.END, log_entry)

        #Apply color coding based on level
        start_idx = self.log_text.index("end-2l linestart")
        end_idx = self.log_text.index("end-1l lineend")

        if level in ["ERROR", "WARNING", "SUCCESS", "INFO"]:
            self.log_text.tag_add(level, start_idx, end_idx)

        #Auto-scroll to bottom
        self.log_text.see(tk.END)

        #Limit log size (keep last 1000 lines)
        line_count = int(self.log_text.index("end-1c").split(".")[0])
        if line_count > 1000:
            self.log_text.delete(1.0, f"{line_count - 1000}.0")

    def clear_log(self):
        """Clear the activity log."""
        self.log_text.delete(1.0, tk.END)
        self.add_log_entry("Log cleared", "INFO", "System")

    def handle_agent_message(self, message: Dict[str, Any]):
        """Handle status messages from modules.agents."""
        msg_type = message.get("type")
        data = message.get("data", {})
        content = message.get("content", "")

        if msg_type == "status_update":
            self.update_status(
                data.get("status", "Unknown"),
                data.get("action"),
                data.get("progress"),
            )

        elif msg_type == "sub_agent_status":
            self.update_sub_agent_status(
                data.get("agent_name", "Unknown"),
                data.get("status", "Unknown"),
            )

        elif msg_type == "plan":
            self.add_log_entry("Generated execution plan", "SUCCESS", "MasterAgent")
            self.update_status("Planning Complete", "Executing plan")

        elif msg_type == "step_start":
            step_index = data.get("index", 0)
            step_description = data.get("description", "Unknown step")
            self.add_log_entry(f"Starting step {step_index + 1}: {step_description}", "INFO", "MasterAgent")
            self.update_status("Executing", f"Step {step_index + 1}", step_index * 20)

        elif msg_type == "step_end":
            step_index = data.get("index", 0)
            success = data.get("success", False)
            level = "SUCCESS" if success else "ERROR"
            result = "completed successfully" if success else "failed"
            self.add_log_entry(f"Step {step_index + 1} {result}", level, "MasterAgent")

        elif msg_type == "tool_execution":
            tool_name = data.get("tool_name", "Unknown")
            self.add_log_entry(f"Executing tool: {tool_name}", "INFO", "ToolAgent")

        elif msg_type == "error":
            self.add_log_entry(f"Error: {content}", "ERROR", data.get("source", "Agent"))

        elif msg_type == "success":
            self.add_log_entry(f"Goal completed: {content}", "SUCCESS", "MasterAgent")
            self.update_status("Completed", "Goal achieved", 100)

        elif msg_type == "request_clarification":
            self.add_log_entry(f"Requesting clarification: {content}", "WARNING", "MasterAgent")
            self.update_status("Waiting", "Clarification needed")

        elif msg_type == "request_feedback":
            self.add_log_entry(f"Requesting feedback: {content}", "WARNING", "MasterAgent")
            self.update_status("Waiting", "Feedback needed")

        else:
            #Generic message
            self.add_log_entry(content, "INFO", data.get("source", "Agent"))
