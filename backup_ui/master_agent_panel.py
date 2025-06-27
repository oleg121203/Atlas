import customtkinter as ctk


class MasterAgentPanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_run,
        on_pause,
        on_stop,
        on_clear_goal,
        on_open_goal_history,
        on_open_plugin_manager,
        goal_text_var,
        prompt_text_var,
        goal_list_var,
        cyclic_var,
        plan_view,
        progress_bar,
        preview_label,
        update_preview_callback,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.on_run = on_run
        self.on_pause = on_pause
        self.on_stop = on_stop
        self.on_clear_goal = on_clear_goal
        self.on_open_goal_history = on_open_goal_history
        self.on_open_plugin_manager = on_open_plugin_manager
        self.goal_text_var = goal_text_var
        self.prompt_text_var = prompt_text_var
        self.goal_list_var = goal_list_var
        self.cyclic_var = cyclic_var
        self.plan_view = plan_view
        self.progress_bar = progress_bar
        self.preview_label = preview_label
        self.update_preview_callback = update_preview_callback
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Goal Input Frame
        goal_frame = ctk.CTkFrame(self, fg_color="transparent")
        goal_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        goal_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(goal_frame, text="Goal").pack(side="left")
        ctk.CTkButton(
            goal_frame,
            text="Goal History",
            width=100,
            command=self.on_open_goal_history,
        ).pack(side="right", padx=(5, 0))
        ctk.CTkButton(
            goal_frame,
            text="Plugin Manager",
            width=120,
            command=self.on_open_plugin_manager,
        ).pack(side="right", padx=(5, 0))
        ctk.CTkButton(
            goal_frame, text="Clear", width=60, command=self.on_clear_goal
        ).pack(side="right", padx=(5, 0))

        # Goal Textbox
        self.goal_text = ctk.CTkTextbox(self, height=120)
        self.goal_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        if self.goal_text_var is not None:
            self.goal_text.insert("1.0", self.goal_text_var.get())

        # Controls Frame
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        controls_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(controls_frame, text="Master Prompt").grid(
            row=0, column=0, columnspan=2, padx=10, pady=(5, 0), sticky="w"
        )
        self.prompt_text = ctk.CTkTextbox(controls_frame, height=80)
        self.prompt_text.grid(
            row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew"
        )
        if self.prompt_text_var is not None:
            self.prompt_text.insert("1.0", self.prompt_text_var.get())

        # Execution options
        options_frame = ctk.CTkFrame(controls_frame)
        options_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkCheckBox(
            options_frame, text="Goal List", variable=self.goal_list_var
        ).pack(side="left", padx=5)
        ctk.CTkCheckBox(
            options_frame, text="Cyclic Mode", variable=self.cyclic_var
        ).pack(side="left", padx=5)

        # Control buttons
        btn_frame = ctk.CTkFrame(controls_frame)
        btn_frame.grid(row=2, column=1, padx=10, pady=5, sticky="e")
        ctk.CTkButton(btn_frame, text="Run", command=self.on_run).pack(
            side="left", padx=5
        )
        ctk.CTkButton(btn_frame, text="Pause", command=self.on_pause).pack(
            side="left", padx=5
        )
        ctk.CTkButton(btn_frame, text="Stop", command=self.on_stop).pack(
            side="left", padx=5
        )

        # Progress Bar
        if self.progress_bar is not None:
            self.progress_bar.grid(
                row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew"
            )

        # Plan View
        if self.plan_view is not None:
            self.plan_view.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        # Live Screenshot Preview
        preview_frame = ctk.CTkFrame(self)
        preview_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(0, weight=1)
        if self.preview_label is not None:
            self.preview_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        if self.update_preview_callback is not None:
            self.update_preview_callback()

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
