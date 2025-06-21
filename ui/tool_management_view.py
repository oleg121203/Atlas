import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any, Dict

import customtkinter as ctk

from monitoring.metrics_manager import metrics_manager

if TYPE_CHECKING:
    from agents.agent_manager import AgentManager

class ToolManagementView(ctk.CTkFrame):
    """A view to display and manage dynamically created tools."""

    def __init__(self, master, agent_manager: "AgentManager", **kwargs):
        super().__init__(master, **kwargs)
        self.agent_manager = agent_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Available Tools", font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.refresh_button = ctk.CTkButton(self, text="Refresh", command=self.populate_tools)
        self.refresh_button.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="e")

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Available Tools")
        self.scrollable_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        self.populate_tools()

    def populate_tools(self):
        """Clears and repopulates the list of tools with usage statistics."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        #Create header
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=(5, 0))
        header_frame.grid_columnconfigure(0, weight=4)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_columnconfigure(3, weight=2)

        ctk.CTkLabel(header_frame, text="Tool Details", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=10)
        ctk.CTkLabel(header_frame, text="Success", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(header_frame, text="Failure", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(header_frame, text="Actions", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, sticky="w", padx=10)

        ctk.CTkFrame(self.scrollable_frame, height=2, fg_color="gray").pack(fill="x", padx=5, pady=(0, 5))

        tools = self.agent_manager.get_all_tools_details()
        usage_stats = metrics_manager.get_tool_usage_stats()

        if not tools:
            no_tools_label = ctk.CTkLabel(self.scrollable_frame, text="No tools are available.")
            no_tools_label.pack(padx=10, pady=10)
            return

        for i, tool in enumerate(tools):
            tool_stats = usage_stats.get(tool.get("name"), {})
            self._create_tool_entry(tool, i, tool_stats)

    def _edit_tool(self, file_path: str):
        """Opens the tool file in the default system editor."""
        try:
            if sys.platform == "win32":
                subprocess.run(["start", file_path], check=True, shell=True)
            elif sys.platform == "darwin": #macOS
                subprocess.run(["open", file_path], check=True)
            else: #linux
                subprocess.run(["xdg-open", file_path], check=True)
        except Exception as e:
            #You might want to show an error message to the user in the GUI
            print(f"Error opening file: {e}")

    def _delete_tool(self, tool_name: str, file_path: str):
        """Handles the request to delete a tool."""
        self.agent_manager.delete_tool(tool_name, file_path)
        self.populate_tools()

    def _view_tool_source(self, file_path: str):
        """Opens a new window to display the tool's source code."""
        try:
            with open(file_path, encoding="utf-8") as f:
                code_content = f.read()
        except Exception as e:
            error_dialog = ctk.CTkToplevel(self)
            error_dialog.title("Error")
            error_dialog.geometry("300x100")
            label = ctk.CTkLabel(error_dialog, text=f"Error reading file:\n{e}", wraplength=280)
            label.pack(expand=True, fill="both", padx=10, pady=10)
            error_dialog.transient(self)
            error_dialog.grab_set()
            return

        source_window = ctk.CTkToplevel(self)
        source_window.title(f"Source: {os.path.basename(file_path)}")
        source_window.geometry("800x600")

        source_window.grid_rowconfigure(0, weight=1)
        source_window.grid_columnconfigure(0, weight=1)

        textbox = ctk.CTkTextbox(source_window, wrap="none", font=("monospace", 12))
        textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        textbox.insert("1.0", code_content)
        textbox.configure(state="disabled")

        source_window.transient(self)
        source_window.grab_set()

    def _show_tool_info(self, tool: Dict[str, Any]):
        """Show information dialog for built-in tools."""
        info_window = ctk.CTkToplevel(self)
        info_window.title(f"Tool Info: {tool['name']}")
        info_window.geometry("500x400")
        info_window.transient(self)
        info_window.grab_set()

        #Main frame
        main_frame = ctk.CTkFrame(info_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        #Tool name
        name_label = ctk.CTkLabel(main_frame, text=tool["name"], font=ctk.CTkFont(size=18, weight="bold"))
        name_label.pack(pady=(10, 5))

        #Tool type and source
        type_label = ctk.CTkLabel(main_frame, text=f"Type: {tool.get('type', 'Unknown').title()}")
        type_label.pack()

        source_label = ctk.CTkLabel(main_frame, text=f"Source: {tool.get('source', 'Unknown')}")
        source_label.pack(pady=(0, 10))

        #Description
        desc_frame = ctk.CTkFrame(main_frame)
        desc_frame.pack(fill="both", expand=True, pady=10)

        desc_title = ctk.CTkLabel(desc_frame, text="Description:", font=ctk.CTkFont(weight="bold"))
        desc_title.pack(anchor="w", padx=10, pady=(10, 5))

        desc_text = ctk.CTkTextbox(desc_frame, height=150, wrap="word")
        desc_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        desc_text.insert("1.0", tool.get("doc", "No description available."))
        desc_text.configure(state="disabled")

        #File path
        path_label = ctk.CTkLabel(main_frame, text=f"File: {tool.get('file_path', 'N/A')}")
        path_label.pack(pady=5)

        #Close button
        close_btn = ctk.CTkButton(main_frame, text="Close", command=info_window.destroy)
        close_btn.pack(pady=10)

    def _create_tool_entry(self, tool: Dict[str, Any], index: int, usage_stats: Dict[str, int]):
        """Creates a frame for a single tool entry with usage stats."""
        tool_frame = ctk.CTkFrame(self.scrollable_frame)
        tool_frame.pack(fill="x", padx=5, pady=5)

        tool_frame.grid_columnconfigure(0, weight=4)  #Details
        tool_frame.grid_columnconfigure(1, weight=1)  #Success
        tool_frame.grid_columnconfigure(2, weight=1)  #Failure
        tool_frame.grid_columnconfigure(3, weight=2)  #Actions

        #--- Column 0: Tool Details ---
        details_frame = ctk.CTkFrame(tool_frame, fg_color="transparent")
        details_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        name_label = ctk.CTkLabel(details_frame, text=tool["name"], font=ctk.CTkFont(weight="bold"))
        name_label.pack(anchor="w", padx=5)

        #Add tool type indicator
        tool_type = tool.get("type", "unknown")
        tool_source = tool.get("source", "Unknown")

        type_color = {
            "built-in": "green",
            "generated": "blue",
            "essential": "orange",
            "plugin": "purple",
        }.get(tool_type, "gray")

        type_label = ctk.CTkLabel(
            details_frame,
            text=f"[{tool_type.upper()}] {tool_source}",
            font=ctk.CTkFont(size=10),
            text_color=type_color,
        )
        type_label.pack(anchor="w", padx=5)

        doc_label = ctk.CTkLabel(details_frame, text=tool["doc"], wraplength=350, justify="left")
        doc_label.pack(anchor="w", padx=5)

        path_label = ctk.CTkLabel(details_frame, text=f"Path: {tool['file_path']}", font=ctk.CTkFont(size=10))
        path_label.pack(anchor="w", padx=5)

        #--- Column 1: Success Count ---
        success_count = usage_stats.get("success", 0)
        success_label = ctk.CTkLabel(tool_frame, text=str(success_count), font=ctk.CTkFont(size=14))
        success_label.grid(row=0, column=1, sticky="w")

        #--- Column 2: Failure Count ---
        failure_count = usage_stats.get("failure", 0)
        failure_label = ctk.CTkLabel(tool_frame, text=str(failure_count), font=ctk.CTkFont(size=14))
        failure_label.grid(row=0, column=2, sticky="w")

        #--- Column 3: Action Buttons ---
        button_frame = ctk.CTkFrame(tool_frame, fg_color="transparent")
        button_frame.grid(row=0, column=3, sticky="e", padx=5, pady=5)

        view_button = ctk.CTkButton(
            button_frame,
            text="View",
            width=60,
            command=lambda t=tool: self._view_tool_source(t["file_path"]),
        )
        view_button.pack(side="left", padx=(0, 5))

        #Edit button - only for generated tools
        if tool.get("type") == "generated":
            edit_button = ctk.CTkButton(
                button_frame,
                text="Edit",
                width=60,
                command=lambda t=tool: self._edit_tool(t["file_path"]),
            )
            edit_button.pack(side="left", padx=(0, 5))

        #Delete button - only for generated tools
        if tool.get("type") == "generated":
            delete_button = ctk.CTkButton(
                button_frame,
                text="Delete",
                width=60,
                command=lambda t=tool: self._delete_tool(t["name"], t["file_path"]),
                fg_color="#DB3E3E",
                hover_color="#B72B2B",
            )
            delete_button.pack(side="left")
        elif tool.get("type") in ["built-in", "essential", "plugin"]:
            #Info button for built-in, essential, and plugin tools
            info_button = ctk.CTkButton(
                button_frame,
                text="Info",
                width=60,
                command=lambda t=tool: self._show_tool_info(t),
                fg_color="gray",
                hover_color="lightgray",
            )
            info_button.pack(side="left")
