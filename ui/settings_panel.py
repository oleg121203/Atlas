import customtkinter as ctk


class SettingsPanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        openai_api_key_var,
        gemini_api_key_var,
        groq_api_key_var,
        mistral_api_key_var,
        anthropic_api_key_var,
        plugin_manager,
        plugin_enabled_vars,
        loaded_settings,
        on_save_settings,
        on_reset_tokens,
        on_toggle_all_plugins,
        on_populate_plugins,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.openai_api_key_var = openai_api_key_var
        self.gemini_api_key_var = gemini_api_key_var
        self.groq_api_key_var = groq_api_key_var
        self.mistral_api_key_var = mistral_api_key_var
        self.anthropic_api_key_var = anthropic_api_key_var
        self.plugin_manager = plugin_manager
        self.plugin_enabled_vars = plugin_enabled_vars
        self.loaded_settings = loaded_settings
        self.on_save_settings = on_save_settings
        self.on_reset_tokens = on_reset_tokens
        self.on_toggle_all_plugins = on_toggle_all_plugins
        self.on_populate_plugins = on_populate_plugins
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # API Keys Frame
        api_keys_frame = ctk.CTkFrame(self)
        api_keys_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        api_keys_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            api_keys_frame, text="API Keys", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")
        ctk.CTkLabel(api_keys_frame, text="OpenAI API Key").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.openai_api_key_entry = ctk.CTkEntry(
            api_keys_frame, textvariable=self.openai_api_key_var, show="*"
        )
        self.openai_api_key_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(api_keys_frame, text="Gemini API Key").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.gemini_api_key_entry = ctk.CTkEntry(
            api_keys_frame, textvariable=self.gemini_api_key_var, show="*"
        )
        self.gemini_api_key_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(api_keys_frame, text="Groq API Key").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        self.groq_api_key_entry = ctk.CTkEntry(
            api_keys_frame, textvariable=self.groq_api_key_var, show="*"
        )
        self.groq_api_key_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(api_keys_frame, text="Mistral API Key").grid(
            row=4, column=0, padx=10, pady=5, sticky="w"
        )
        self.mistral_api_key_entry = ctk.CTkEntry(
            api_keys_frame, textvariable=self.mistral_api_key_var, show="*"
        )
        self.mistral_api_key_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(api_keys_frame, text="Anthropic API Key").grid(
            row=5, column=0, padx=10, pady=5, sticky="w"
        )
        self.anthropic_api_key_entry = ctk.CTkEntry(
            api_keys_frame, textvariable=self.anthropic_api_key_var, show="*"
        )
        self.anthropic_api_key_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        # Plugin Management Frame
        plugin_outer_frame = ctk.CTkFrame(self)
        plugin_outer_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        plugin_outer_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        plugin_header_frame = ctk.CTkFrame(plugin_outer_frame, fg_color="transparent")
        plugin_header_frame.pack(fill="x", padx=10, pady=(5, 10))
        plugin_header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            plugin_header_frame,
            text="Plugin Management",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        plugin_buttons_frame = ctk.CTkFrame(plugin_header_frame, fg_color="transparent")
        plugin_buttons_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(
            plugin_buttons_frame,
            text="Enable All",
            width=90,
            command=lambda: self.on_toggle_all_plugins(True),
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            plugin_buttons_frame,
            text="Disable All",
            width=90,
            command=lambda: self.on_toggle_all_plugins(False),
        ).pack(side="left")
        self.plugin_scroll_frame = ctk.CTkScrollableFrame(
            plugin_outer_frame, label_text="Available Plugins"
        )
        self.plugin_scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.on_populate_plugins(self.plugin_scroll_frame)

        # Token Usage Statistics
        token_frame = ctk.CTkFrame(self)
        token_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        token_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            token_frame, text="Token Usage Statistics", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="w")
        ctk.CTkLabel(token_frame, text="Prompt:").grid(
            row=1, column=0, padx=10, pady=2, sticky="w"
        )
        self.prompt_tokens_label = ctk.CTkLabel(token_frame, text="0")
        self.prompt_tokens_label.grid(row=1, column=1, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(token_frame, text="Completion:").grid(
            row=2, column=0, padx=10, pady=2, sticky="w"
        )
        self.completion_tokens_label = ctk.CTkLabel(token_frame, text="0")
        self.completion_tokens_label.grid(row=2, column=1, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(token_frame, text="Total:").grid(
            row=3, column=0, padx=10, pady=2, sticky="w"
        )
        self.total_tokens_label = ctk.CTkLabel(
            token_frame, text="0", font=ctk.CTkFont(weight="bold")
        )
        self.total_tokens_label.grid(row=3, column=1, padx=10, pady=2, sticky="w")
        self.reset_tokens_button = ctk.CTkButton(
            token_frame, text="Reset", command=self.on_reset_tokens
        )
        self.reset_tokens_button.grid(row=1, column=2, rowspan=3, padx=10, pady=5)

        # Save Button
        self.save_settings_button = ctk.CTkButton(
            self, text="Save Settings", command=self.on_save_settings
        )
        self.save_settings_button.grid(row=6, column=0, padx=10, pady=10, sticky="s")
