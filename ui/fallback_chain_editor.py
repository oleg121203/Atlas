import customtkinter as ctk
from typing import List, Callable

class FallbackChainEditor(ctk.CTkToplevel):
    """A Toplevel window to edit the fallback chain for an agent."""

    def __init__(self, parent, current_chain: List[str], all_models: List[str], save_callback: Callable[[List[str]], None]):
        super().__init__(parent)
        self.title("Edit Fallback Chain")
        self.geometry("400x500")
        self.transient(parent)
        self.grab_set()

        self.current_chain = current_chain.copy()
        self.all_models = all_models
        self.save_callback = save_callback

        self._create_widgets()
        self._populate_list()

    def _create_widgets(self):
        """Create the UI elements for the editor."""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # --- Controls for adding models ---
        add_frame = ctk.CTkFrame(main_frame)
        add_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        add_frame.grid_columnconfigure(0, weight=1)

        self.model_menu = ctk.CTkOptionMenu(add_frame, values=self.all_models)
        self.model_menu.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        ctk.CTkButton(add_frame, text="Add", width=50, command=self._add_model).grid(row=0, column=1, pady=5)

        # --- Listbox for the chain ---
        self.listbox = ctk.CTkTextbox(main_frame, font=("monospace", 12))
        self.listbox.grid(row=1, column=0, sticky="nsew")

        # --- Buttons to reorder ---
        reorder_frame = ctk.CTkFrame(main_frame)
        reorder_frame.grid(row=1, column=1, sticky="ns", padx=(10, 0))

        ctk.CTkButton(reorder_frame, text="Up", command=self._move_up).pack(pady=5)
        ctk.CTkButton(reorder_frame, text="Down", command=self._move_down).pack(pady=5)
        ctk.CTkButton(reorder_frame, text="Remove", command=self._remove_model).pack(pady=20)

        # --- Save/Cancel buttons ---
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="e", pady=(10, 0))

        ctk.CTkButton(button_frame, text="Save", command=self._save_and_close).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy).pack(side="left")

    def _populate_list(self):
        """Update the listbox with the current chain."""
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")
        if not self.current_chain:
            self.listbox.insert("1.0", "No models in fallback chain.")
            self.listbox.configure(state="disabled")
            return

        for i, model in enumerate(self.current_chain):
            self.listbox.insert(f"{i+1}.0", f"{model}\n")
        self.listbox.configure(state="disabled")

    def _add_model(self):
        """Add the selected model to the chain."""
        model = self.model_menu.get()
        if model and model not in self.current_chain:
            self.current_chain.append(model)
            self._populate_list()

    def _remove_model(self):
        """Remove the selected model from the chain."""
        # This is a simplified implementation. A real implementation would
        # require selecting an item from the listbox.
        if self.current_chain:
            self.current_chain.pop()
            self._populate_list()

    def _move_up(self):
        """Move the selected model up in the chain."""
        # Placeholder for moving an item up
        pass

    def _move_down(self):
        """Move the selected model down in the chain."""
        # Placeholder for moving an item down
        pass

    def _save_and_close(self):
        """Save the changes and close the window."""
        self.save_callback(self.current_chain)
        self.destroy()
