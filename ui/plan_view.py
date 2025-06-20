"""
Defines the PlanView class for displaying the agent's execution plan in the UI.
"""

import customtkinter as ctk
from typing import Dict, Any, List

class PlanView(ctk.CTkScrollableFrame):
    """A widget to display the agent's plan and its execution status."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.label_text = "Execution Plan"
        self.step_widgets: List[ctk.CTkFrame] = []
        self.details_frames: List[ctk.CTkFrame] = []

    def clear_plan(self):
        """Clears all widgets from the plan view."""
        for widget in self.winfo_children():
            widget.destroy()
        self.step_widgets = []
        self.details_frames = []

    def display_plan(self, plan: Dict[str, Any]):
        """Renders the entire plan in the view."""
        self.clear_plan()

        description = plan.get("description", "No description provided.")
        desc_label = ctk.CTkLabel(self, text=f"Goal: {description}", font=ctk.CTkFont(weight="bold"), wraplength=400)
        desc_label.pack(anchor="w", padx=10, pady=5)

        steps = plan.get("steps", [])
        if not steps:
            no_steps_label = ctk.CTkLabel(self, text="No steps in this plan.", text_color="gray")
            no_steps_label.pack(anchor="w", padx=10, pady=5)
            return

        for i, step in enumerate(steps):
            step_frame = ctk.CTkFrame(self, fg_color="transparent")
            step_frame.pack(fill="x", padx=5, pady=2)

            status_label = ctk.CTkLabel(step_frame, text="⏳", width=20) #Pending
            status_label.pack(side="left", padx=(5, 10))

            step_desc = step.get('description', 'No description for this step.')
            step_label = ctk.CTkLabel(step_frame, text=f"{i+1}. {step_desc}", wraplength=450, justify="left")
            step_label.pack(side="left", fill="x", expand=True)
            
            self.step_widgets.append(step_frame)

            #Create a container for details, but don't show it yet
            details_frame = ctk.CTkFrame(self, fg_color="gray20")
            self.details_frames.append(details_frame)

    def update_step_status(self, index: int, status: str, data: Dict[str, Any]):
        """Updates the visual status of a single step and shows details."""
        if index >= len(self.step_widgets):
            return

        step_frame = self.step_widgets[index]
        details_frame = self.details_frames[index]
        status_label = step_frame.winfo_children()[0]

        #Clear previous details from the details frame
        for widget in details_frame.winfo_children():
            widget.destroy()

        #Ensure details frame is visible by packing it if it's not already
        if not details_frame.winfo_viewable():
            details_frame.pack(fill="x", padx=(40, 5), pady=2, after=step_frame)

        step_info = data.get('step', {})
        tool_name = step_info.get('tool_name', 'N/A')
        args = step_info.get('arguments', {})

        if status == "start":
            status_label.configure(text="⚙️") #Running
            tool_label = ctk.CTkLabel(details_frame, text=f"Tool: {tool_name}", font=ctk.CTkFont(slant="italic"))
            tool_label.pack(anchor="w", padx=5)
            args_label = ctk.CTkLabel(details_frame, text=f"Arguments: {args}", wraplength=400, justify="left")
            args_label.pack(anchor="w", padx=5)

        elif status == "end":
            if data.get("status") == "success":
                status_label.configure(text="✅") #Success
                result = data.get("result", "No output.")
                result_label = ctk.CTkLabel(details_frame, text=f"Output: {result}", wraplength=400, justify="left")
                result_label.pack(anchor="w", padx=5)
            else:
                status_label.configure(text="❌") #Error
                error_msg = data.get("error", "An unknown error occurred.")
                error_label = ctk.CTkLabel(details_frame, text=f"Error: {error_msg}", text_color="#E57373", wraplength=450)
                error_label.pack(anchor="w", padx=5)
