import customtkinter as ctk


class TasksPanel(ctk.CTkFrame):
    def __init__(
        self, master, tasks=None, mode="flat", on_refresh=None, on_action=None, **kwargs
    ):
        super().__init__(master, **kwargs)
        self.tasks = tasks or []
        self.mode = mode
        self.on_refresh = on_refresh
        self.on_action = on_action
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        header = ctk.CTkLabel(
            self,
            text="Hierarchical Tasks" if self.mode == "hierarchical" else "Tasks",
            font=ctk.CTkFont(weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        self.tree_frame = ctk.CTkScrollableFrame(
            self, label_text="Task Tree" if self.mode == "hierarchical" else "Task List"
        )
        self.tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.grid_rowconfigure(1, weight=1)
        self._populate_tree()
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=2, column=0, sticky="e", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Refresh", command=self._refresh).pack(
            side="left", padx=5
        )

    def _populate_tree(self):
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        if self.mode == "hierarchical":
            for task in self.tasks:
                frame = ctk.CTkFrame(self.tree_frame)
                frame.pack(fill="x", padx=5, pady=3)
                ctk.CTkLabel(frame, text=str(task), font=ctk.CTkFont(size=12)).pack(
                    side="left", padx=5
                )
                if self.on_action and callable(self.on_action):
                    ctk.CTkButton(
                        frame,
                        text="Action",
                        width=60,
                        command=lambda t=task: self.on_action(t),
                    ).pack(side="right", padx=2)
        else:
            for task in self.tasks:
                frame = ctk.CTkFrame(self.tree_frame)
                frame.pack(fill="x", padx=5, pady=3)
                ctk.CTkLabel(frame, text=str(task), font=ctk.CTkFont(size=12)).pack(
                    side="left", padx=5
                )
                if self.on_action and callable(self.on_action):
                    ctk.CTkButton(
                        frame,
                        text="Action",
                        width=60,
                        command=lambda t=task: self.on_action(t),
                    ).pack(side="right", padx=2)

    def _refresh(self):
        if self.on_refresh and callable(self.on_refresh):
            self.on_refresh()
