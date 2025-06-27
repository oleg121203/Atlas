import customtkinter as ctk


class PluginManagerPanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        plugin_manager,
        plugin_enabled_vars,
        on_toggle_all_plugins,
        on_plugin_toggle,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.plugin_manager = plugin_manager
        self.plugin_enabled_vars = plugin_enabled_vars
        self.on_toggle_all_plugins = on_toggle_all_plugins
        self.on_plugin_toggle = on_plugin_toggle
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        # Header
        header = ctk.CTkLabel(
            self, text="Available Plugins", font=ctk.CTkFont(weight="bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=0, column=1, sticky="e", padx=10, pady=(10, 5))
        ctk.CTkButton(
            btn_frame,
            text="Enable All",
            width=90,
            command=lambda: self.on_toggle_all_plugins(True),
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Disable All",
            width=90,
            command=lambda: self.on_toggle_all_plugins(False),
        ).pack(side="left")
        # Scrollable list
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Plugins")
        self.scroll_frame.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5
        )
        self.grid_rowconfigure(1, weight=1)
        self._populate_plugins()

    def _populate_plugins(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        all_plugins = self.plugin_manager.get_all_plugins()
        if not all_plugins:
            ctk.CTkLabel(
                self.scroll_frame, text="No plugins found.", text_color="gray"
            ).pack(padx=10, pady=10)
        else:
            for plugin_id, plugin_data in sorted(all_plugins.items()):
                manifest = plugin_data.get("manifest", {})
                plugin_name = manifest.get("name", plugin_id)
                if plugin_id not in self.plugin_enabled_vars:
                    self.plugin_enabled_vars[plugin_id] = ctk.BooleanVar(value=True)
                var = self.plugin_enabled_vars[plugin_id]
                cb = ctk.CTkCheckBox(
                    self.scroll_frame,
                    text=plugin_name,
                    variable=var,
                    command=lambda pid=plugin_id, v=var: self.on_plugin_toggle(
                        pid, v.get()
                    ),
                )
                cb.pack(fill="x", padx=10, pady=5)
