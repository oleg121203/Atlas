import os
import subprocess
import sys
import json
from typing import TYPE_CHECKING, Any, Dict
import threading
import asyncio

import customtkinter as ctk

from monitoring.metrics_manager import MetricsManager
metrics_manager_instance = MetricsManager()

if TYPE_CHECKING:
    from modules.agents.agent_manager import AgentManager

class ToolManagementView(ctk.CTkFrame):
    """A view to display and manage dynamically created tools."""

    def __init__(self, master, agent_manager: "AgentManager", **kwargs):
        print("[LOG] ToolManagementView: __init__ called")
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

        # Add Creative Templates section
        self._add_creative_templates_section()

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
        usage_stats = metrics_manager_instance.get_tool_usage_stats()

        if not tools:
            no_tools_label = ctk.CTkLabel(self.scrollable_frame, text="No tools are available.")
            no_tools_label.pack(padx=10, pady=10)
            return

        for i, tool in enumerate(tools):
            tool_stats = usage_stats.get(tool.get("name", ""), {})
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
            error_dialog.transient(self.winfo_toplevel())
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

        source_window.transient(self.winfo_toplevel())
        source_window.grab_set()

    def _show_tool_info(self, tool: Dict[str, Any]):
        """Show information dialog for built-in tools."""
        info_window = ctk.CTkToplevel(self)
        info_window.title(f"Tool Info: {tool['name']}")
        info_window.geometry("500x400")
        info_window.transient(self.winfo_toplevel())
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

    def _add_creative_templates_section(self):
        """Add a panel for creative tool chain templates and playful/proactive automations."""
        templates_frame = ctk.CTkFrame(self)
        templates_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        templates_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(templates_frame, text="Creative Templates", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))

        # Expanded creative chains
        creative_chains = [
            ("Screenshot → OCR → Translate", self._run_screenshot_ocr_translate),
            ("Clipboard → Translate → Search", self._run_clipboard_translate_search),
            ("Screenshot → Image Recognition → Notification", self._run_screenshot_image_notify),
            ("Inbox Zero Challenge (Playful)", self._run_inbox_zero_challenge),
            ("Gamify File Cleanup", self._run_gamify_file_cleanup),
            ("Random Art Generator", self._run_random_art_generator),
            ("Proactive Suggestion", self._run_proactive_suggestion),
            ("Suggest Macro for Recent Actions", self._run_suggest_macro),
            ("Auto-Organize Desktop", self._run_auto_organize_desktop),
            ("Summarize PDF → Translate → Email", self._run_summarize_pdf_translate_email),
            ("Meme Generator from Screenshot", self._run_meme_generator_screenshot),
            ("Mute, Open Zoom, Set Volume to 80%", self._run_mute_open_zoom_set_volume),
            ("Get Running Apps and Open Safari", self._run_get_apps_open_safari),
            ("Sleep Mac", self._run_sleep_mac),
            ("Custom Tool Chain...", self._open_custom_chain_dialog),
        ]
        for i, (label, callback) in enumerate(creative_chains):
            btn = ctk.CTkButton(templates_frame, text=label, command=callback)
            btn.grid(row=1, column=i, padx=5, pady=5, sticky="ew")

    def _show_feedback_dialog(self, context_msg="Tool chain executed."):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Feedback")
        dialog.geometry("400x250")
        ctk.CTkLabel(dialog, text=context_msg, wraplength=380).pack(padx=20, pady=(20, 10))
        ctk.CTkLabel(dialog, text="Was this helpful?").pack(pady=(0, 5))
        helpful_var = ctk.StringVar(value="Yes")
        ctk.CTkRadioButton(dialog, text="Yes", variable=helpful_var, value="Yes").pack()
        ctk.CTkRadioButton(dialog, text="No", variable=helpful_var, value="No").pack()
        ctk.CTkLabel(dialog, text="Suggestions (optional):").pack(pady=(10, 0))
        suggestion_entry = ctk.CTkEntry(dialog, width=350)
        suggestion_entry.pack(pady=(0, 10))
        def submit():
            print(f"[FEEDBACK] Helpful: {helpful_var.get()} | Suggestions: {suggestion_entry.get()}")
            dialog.destroy()
        ctk.CTkButton(dialog, text="Submit", command=submit).pack(pady=10)

    def _run_screenshot_ocr_translate(self):
        tool_chain = [
            {"tool": "capture_screen", "args": {}},
            {"tool": "ocr_image", "args": {}},
            {"tool": "translate_text", "args": {"target_language": "en"}},
        ]
        self.agent_manager.execute_tool("creative_tool", {"tool_chain": tool_chain})
        self._show_feedback_dialog("Screenshot → OCR → Translate chain executed.")

    def _run_inbox_zero_challenge(self):
        self.agent_manager.execute_tool("playful_tool", {"task_type": "inbox_cleanup"})
        self._show_feedback_dialog("Inbox Zero Challenge executed.")

    def _run_proactive_suggestion(self):
        self.agent_manager.execute_tool("proactive_tool", {"trigger_type": "idle", "threshold": 3})
        self._show_feedback_dialog("Proactive Suggestion executed.")

    def _open_custom_chain_dialog(self, template_to_load=None):
        # Full-featured dialog to compose and run custom tool chains
        dialog = ctk.CTkToplevel(self)
        dialog.title("Custom Tool Chain Composer")
        dialog.geometry("600x500")
        dialog.grab_set()

        steps = []  # List of (tool_var, args_entry)

        def add_step(tool_name="", args_str=""):
            row = len(steps) + 1
            frame = ctk.CTkFrame(dialog)
            frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
            tool_var = ctk.StringVar(value=tool_name)
            tool_dropdown = ctk.CTkComboBox(frame, variable=tool_var, values=self._get_tool_names(), width=180)
            tool_dropdown.grid(row=0, column=0, padx=5)
            args_entry = ctk.CTkEntry(frame, placeholder_text="Arguments (JSON)", width=250)
            args_entry.insert(0, args_str)
            args_entry.grid(row=0, column=1, padx=5)
            remove_btn = ctk.CTkButton(frame, text="Remove", width=60, command=lambda: remove_step(frame, (tool_var, args_entry)))
            remove_btn.grid(row=0, column=2, padx=5)
            steps.append((tool_var, args_entry, frame))

        def remove_step(frame, step):
            frame.destroy()
            steps.remove(step + (frame,))

        def run_chain():
            tool_chain = []
            for tool_var, args_entry, _ in steps:
                tool_name = tool_var.get()
                try:
                    args = eval(args_entry.get()) if args_entry.get().strip() else {}
                except Exception:
                    args = {}
                tool_chain.append({"tool": tool_name, "args": args})
            ToolChainRunnerDialog(self, self.agent_manager, tool_chain)

        def save_template():
            # Prompt for name/description
            save_dialog = ctk.CTkToplevel(dialog)
            save_dialog.title("Save Template")
            save_dialog.geometry("350x200")
            ctk.CTkLabel(save_dialog, text="Template Name:").pack(pady=(20, 0))
            name_entry = ctk.CTkEntry(save_dialog, width=300)
            name_entry.pack(pady=5)
            ctk.CTkLabel(save_dialog, text="Description:").pack(pady=(10, 0))
            desc_entry = ctk.CTkEntry(save_dialog, width=300)
            desc_entry.pack(pady=5)
            def do_save():
                name = name_entry.get().strip()
                desc = desc_entry.get().strip()
                if not name:
                    return
                tool_chain = []
                for tool_var, args_entry, _ in steps:
                    tool_name = tool_var.get()
                    try:
                        args = eval(args_entry.get()) if args_entry.get().strip() else {}
                    except Exception:
                        args = {}
                    tool_chain.append({"tool": tool_name, "args": args})
                template = {"name": name, "description": desc, "tool_chain": tool_chain}
                _save_chain_template(template)
                save_dialog.destroy()
            ctk.CTkButton(save_dialog, text="Save", command=do_save).pack(pady=10)

        def _save_chain_template(template):
            path = os.path.expanduser("~/.atlas_tool_chains.json")
            try:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        data = json.load(f)
                else:
                    data = []
                # Overwrite if name exists
                data = [t for t in data if t["name"] != template["name"]]
                data.append(template)
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"[ERROR] Saving template: {e}")

        def load_template():
            path = os.path.expanduser("~/.atlas_tool_chains.json")
            try:
                if not os.path.exists(path):
                    return
                with open(path, "r") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[ERROR] Loading templates: {e}")
                return
            # Show dialog to pick template
            pick_dialog = ctk.CTkToplevel(dialog)
            pick_dialog.title("Load Template")
            pick_dialog.geometry("400x300")
            ctk.CTkLabel(pick_dialog, text="Select a template:").pack(pady=10)
            for t in data:
                def load_this_template(template=t):
                    pick_dialog.destroy()
                    dialog.destroy()
                    self._open_custom_chain_dialog(template_to_load=template)
                btn = ctk.CTkButton(pick_dialog, text=f"{t['name']}: {t.get('description','')}", command=load_this_template)
                btn.pack(fill="x", padx=20, pady=3)
            ctk.CTkButton(pick_dialog, text="Cancel", command=pick_dialog.destroy).pack(pady=10)

        # Title
        ctk.CTkLabel(dialog, text="Custom Tool Chain Composer", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=4, pady=(10, 5))
        # Steps header
        ctk.CTkLabel(dialog, text="Steps:").grid(row=1, column=0, sticky="w", padx=10)
        # Add Step button
        ctk.CTkButton(dialog, text="Add Step", command=add_step).grid(row=1, column=2, sticky="e", padx=10)
        # Load Template button
        ctk.CTkButton(dialog, text="Load Template", command=load_template).grid(row=1, column=3, sticky="e", padx=10)
        # If loading a template, populate steps
        if template_to_load:
            for step in template_to_load.get("tool_chain", []):
                tool = step.get("tool", "")
                args = json.dumps(step.get("args", {})) if step.get("args") else ""
                add_step(tool, args)
        else:
            add_step()
        # Run/Save/Close buttons
        ctk.CTkButton(dialog, text="Run Chain", command=run_chain).grid(row=100, column=0, pady=20, padx=10, sticky="w")
        ctk.CTkButton(dialog, text="Save as Template", command=save_template).grid(row=100, column=1, pady=20, padx=10)
        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).grid(row=100, column=3, pady=20, padx=10, sticky="e")

    def _get_tool_names(self):
        # Helper to get all available tool names for dropdown
        tools = self.agent_manager.get_all_tools_details()
        return [t["name"] for t in tools]

    def _run_clipboard_translate_search(self):
        tool_chain = [
            {"tool": "get_clipboard_text", "args": {}},
            {"tool": "translate_text", "args": {"target_language": "en"}},
            {"tool": "execute_command", "args": {"command": "open https://www.google.com/search?q={input}"}},
        ]
        self.agent_manager.execute_tool("creative_tool", {"tool_chain": tool_chain})
        self._show_feedback_dialog("Clipboard → Translate → Search chain executed.")

    def _run_screenshot_image_notify(self):
        tool_chain = [
            {"tool": "capture_screen", "args": {}},
            {"tool": "find_object_in_image", "args": {}},
            {"tool": "send_notification", "args": {"message": "Object detected!"}},
        ]
        self.agent_manager.execute_tool("creative_tool", {"tool_chain": tool_chain})
        self._show_feedback_dialog("Screenshot → Image Recognition → Notification chain executed.")

    def _run_gamify_file_cleanup(self):
        self.agent_manager.execute_tool("playful_tool", {"task_type": "file_cleanup"})
        self._show_feedback_dialog("Gamify File Cleanup executed.")

    def _run_random_art_generator(self):
        self.agent_manager.execute_tool("playful_tool", {"task_type": "random_art"})
        self._show_feedback_dialog("Random Art Generator executed.")

    def _run_summarize_pdf_translate_email(self):
        # For now, simulate the chain and show info dialog
        info = (
            "This automation will: \n"
            "1. Extract text from a PDF\n"
            "2. Summarize the content\n"
            "3. Translate the summary\n"
            "4. Email the result to a chosen recipient.\n\n"
            "(In a full implementation, you would select a PDF and recipient.)"
        )
        ctk.CTkMessagebox(title="Summarize PDF → Translate → Email", message=info)
        # Simulate chain
        tool_chain = [
            {"tool": "extract_pdf_text", "args": {"file_path": "example.pdf"}},
            {"tool": "summarize_text", "args": {}},
            {"tool": "translate_text", "args": {"target_language": "en"}},
            {"tool": "send_email", "args": {"to": "user@example.com", "subject": "Summary", "body": "{input}"}},
        ]
        ToolChainRunnerDialog(self, self.agent_manager, tool_chain)

    def _run_meme_generator_screenshot(self):
        info = (
            "This playful automation will:\n"
            "1. Take a screenshot\n"
            "2. Add a random or user-supplied caption\n"
            "3. Save or share the meme!\n\n"
            "(In a full implementation, you would select or enter a caption.)"
        )
        ctk.CTkMessagebox(title="Meme Generator from Screenshot", message=info)
        tool_chain = [
            {"tool": "capture_screen", "args": {}},
            {"tool": "add_meme_caption", "args": {"caption": "When Atlas automates your day..."}},
            {"tool": "save_image", "args": {"file_path": "meme.png"}},
        ]
        ToolChainRunnerDialog(self, self.agent_manager, tool_chain)

    def _run_auto_organize_desktop(self):
        self.agent_manager.execute_tool("proactive_tool", {"trigger_type": "auto_organize_desktop", "threshold": 2})
        self._show_feedback_dialog("Auto-Organize Desktop executed.")

    def _run_mute_open_zoom_set_volume(self):
        tool_chain = [
            {"tool": "system_event", "args": {"event": "mute"}},
            {"tool": "system_event", "args": {"event": "open_app", "app_name": "zoom.us"}},
            {"tool": "system_event", "args": {"event": "set_volume", "value": 80}},
        ]
        ToolChainRunnerDialog(self, self.agent_manager, tool_chain)

    def _run_get_apps_open_safari(self):
        tool_chain = [
            {"tool": "system_event", "args": {"event": "get_running_apps"}},
            {"tool": "system_event", "args": {"event": "open_app", "app_name": "Safari"}},
        ]
        ToolChainRunnerDialog(self, self.agent_manager, tool_chain)

    def _run_sleep_mac(self):
        tool_chain = [
            {"tool": "system_event", "args": {"event": "sleep"}},
        ]
        ToolChainRunnerDialog(self, self.agent_manager, tool_chain)

class ToolChainRunnerDialog(ctk.CTkToplevel):
    def __init__(self, parent, agent_manager, tool_chain):
        super().__init__(parent)
        self.title("Tool Chain Runner")
        self.geometry("600x400")
        self.agent_manager = agent_manager
        self.tool_chain = tool_chain
        self.cancelled = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._step_times = []
        self._success_count = 0
        self._error_count = 0
        self._start_time = None

        ctk.CTkLabel(self, text="Tool Chain Execution", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        self.log_box = ctk.CTkTextbox(self, width=560, height=260, wrap="word")
        self.log_box.pack(padx=20, pady=10, fill="both", expand=True)
        self.log_box.insert("end", "Starting tool chain...\n", ("info",))
        self.log_box.configure(state="disabled")

        self.status_label = ctk.CTkLabel(self, text="Running...", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(0, 5))
        self.stop_btn = ctk.CTkButton(self, text="Stop", command=self._cancel)
        self.stop_btn.pack(pady=(0, 10))

        # Tag config for color/formatting
        self.log_box.tag_configure("info", foreground="#3A7CA5")
        self.log_box.tag_configure("success", foreground="#2E8B57", font=("monospace", 11, "bold"))
        self.log_box.tag_configure("error", foreground="#B22222", font=("monospace", 11, "bold"))
        self.log_box.tag_configure("step", font=("monospace", 11, "bold"))
        self.log_box.tag_configure("result", font=("monospace", 11))

        # Start execution in a thread to avoid blocking UI
        threading.Thread(target=self._run_chain, daemon=True).start()

    def _log(self, msg, tag=None):
        self.log_box.configure(state="normal")
        if tag:
            self.log_box.insert("end", msg + "\n", (tag,))
        else:
            self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _cancel(self):
        self.cancelled = True
        self.status_label.configure(text="Cancelled by user.")
        self.stop_btn.configure(state="disabled")

    def _on_close(self):
        self._cancel()
        self.destroy()

    def _run_chain(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._run_chain_async())

    async def _run_chain_async(self):
        import time
        self._start_time = time.time()
        for idx, step in enumerate(self.tool_chain):
            if self.cancelled:
                self._log(f"Step {idx+1}: Cancelled.", tag="info")
                break
            tool_name = step.get("tool", "")
            args = step.get("args", {})
            self._log(f"Step {idx+1}: {tool_name} {args}", tag="step")
            step_start = time.time()
            try:
                result = await self._run_tool(tool_name, args)
                step_time = time.time() - step_start
                self._step_times.append(step_time)
                self._success_count += 1
                self._log(f"Result: {result}", tag="success")
                self._log(f"Step time: {step_time:.2f}s", tag="info")
            except Exception as e:
                step_time = time.time() - step_start
                self._step_times.append(step_time)
                self._error_count += 1
                self._log(f"Error: {e}", tag="error")
                self._log(f"Step time: {step_time:.2f}s", tag="info")
                self.status_label.configure(text=f"Error at step {idx+1}")
                break
        else:
            total_time = time.time() - self._start_time
            self.status_label.configure(text="Chain complete.")
            self._log("All steps complete.", tag="success")
            self._log(f"Total time: {total_time:.2f}s", tag="info")
            self._log(f"Steps succeeded: {self._success_count}, failed: {self._error_count}", tag="info")
        self.stop_btn.configure(text="Close", command=self.destroy, state="normal")

    async def _run_tool(self, tool_name, args):
        tool = getattr(self.agent_manager, "get_tool_instance", None)
        if tool:
            tool_instance = self.agent_manager.get_tool_instance(tool_name)
            if hasattr(tool_instance, "run") and asyncio.iscoroutinefunction(tool_instance.run):
                return await tool_instance.run(**args)
            elif hasattr(tool_instance, "run"):
                return tool_instance.run(**args)
        result = self.agent_manager.execute_tool(tool_name, args)
        if asyncio.iscoroutine(result):
            return await result
        return result
