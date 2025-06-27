import json
import tkinter as tk
from tkinter import messagebox, ttk

from workflow.natural_language_workflow import NLWorkflowGenerator


class NLWorkflowUI:
    """User Interface for Natural Language to Workflow Generator"""

    def __init__(self, root, generator: NLWorkflowGenerator):
        """Initialize the UI for natural language workflow generation

        Args:
            root: Tkinter root window or frame
            generator (NLWorkflowGenerator): Instance of the workflow generator
        """
        self.root = root
        self.generator = generator
        self.root.title("Atlas Natural Language Workflow Generator")
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input label and text area for natural language prompt
        ttk.Label(main_frame, text="Describe the workflow you want to create:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.input_text = tk.Text(main_frame, height=5, width=50)
        self.input_text.grid(row=1, column=0, columnspan=2, pady=5)

        # Generate button
        ttk.Button(
            main_frame, text="Generate Workflow", command=self.generate_workflow
        ).grid(row=2, column=0, columnspan=2, pady=10)

        # Output label and text area for generated workflow
        ttk.Label(main_frame, text="Generated Workflow Structure:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.output_text = tk.Text(main_frame, height=15, width=50)
        self.output_text.grid(row=4, column=0, columnspan=2, pady=5)
        self.output_text.config(state="disabled")  # Make output read-only

        # Save and Edit buttons
        ttk.Button(main_frame, text="Save Workflow", command=self.save_workflow).grid(
            row=5, column=0, pady=5
        )
        ttk.Button(main_frame, text="Edit Workflow", command=self.edit_workflow).grid(
            row=5, column=1, pady=5
        )

        # Feedback section
        ttk.Label(main_frame, text="Rate this workflow (1-5):").grid(
            row=6, column=0, sticky=tk.W, pady=2
        )
        self.rating_var = tk.IntVar(value=3)
        ttk.Scale(
            main_frame, from_=1, to=5, orient=tk.HORIZONTAL, variable=self.rating_var
        ).grid(row=6, column=1, pady=2)

        ttk.Label(main_frame, text="Feedback comments:").grid(
            row=7, column=0, sticky=tk.W, pady=2
        )
        self.feedback_text = tk.Text(main_frame, height=3, width=50)
        self.feedback_text.grid(row=8, column=0, columnspan=2, pady=5)

        ttk.Button(
            main_frame, text="Submit Feedback", command=self.submit_feedback
        ).grid(row=9, column=0, columnspan=2, pady=5)

        # Make UI responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=2)

    def generate_workflow(self):
        """Generate workflow from natural language input"""
        nl_input = self.input_text.get("1.0", tk.END).strip()
        if not nl_input:
            messagebox.showwarning(
                "Input Required",
                "Please enter a description of the workflow you want to create.",
            )
            return

        try:
            # Using default user_id and empty context for now
            # In a real system, user_id would come from login/auth
            workflow = self.generator.generate_workflow(
                nl_input, user_id="default", context_data={}
            )
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", json.dumps(workflow, indent=2))
            self.output_text.config(state="disabled")
            self.current_workflow = workflow
            self.current_nl_input = nl_input
            # Reset feedback fields
            self.rating_var.set(3)
            self.feedback_text.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror(
                "Generation Error", f"Failed to generate workflow: {str(e)}"
            )

    def save_workflow(self):
        """Save the generated workflow to file or database"""
        if not hasattr(self, "current_workflow"):
            messagebox.showwarning(
                "No Workflow", "Generate a workflow first before saving."
            )
            return

        try:
            # Placeholder for saving logic - would integrate with workflow storage system
            messagebox.showinfo(
                "Save Successful", "Workflow saved successfully! (Placeholder action)"
            )
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save workflow: {str(e)}")

    def edit_workflow(self):
        """Open workflow editor for manual modifications"""
        if not hasattr(self, "current_workflow"):
            messagebox.showwarning(
                "No Workflow", "Generate a workflow first before editing."
            )
            return

        # Placeholder for opening a workflow editor
        messagebox.showinfo("Editor", "Opening workflow editor... (Placeholder action)")

    def submit_feedback(self):
        """Submit user feedback for the current workflow"""
        if not hasattr(self, "current_workflow"):
            messagebox.showwarning(
                "No Workflow", "Generate a workflow first before submitting feedback."
            )
            return

        rating = self.rating_var.get()
        comments = self.feedback_text.get("1.0", tk.END).strip()
        try:
            self.generator.feedback.add_feedback(
                self.current_workflow, self.current_nl_input, rating, comments
            )
            messagebox.showinfo(
                "Feedback Submitted", f"Thank you for your feedback! Rating: {rating}/5"
            )
        except Exception as e:
            messagebox.showerror(
                "Feedback Error", f"Failed to submit feedback: {str(e)}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    generator = NLWorkflowGenerator()
    app = NLWorkflowUI(root, generator)
    root.mainloop()
