import customtkinter as ctk


class SecurityPanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        plugin_manager,
        plugin_enabled_vars,
        notification_email_var,
        notification_telegram_var,
        notification_sms_var,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.plugin_manager = plugin_manager
        self.plugin_enabled_vars = plugin_enabled_vars
        self.notification_email_var = notification_email_var
        self.notification_telegram_var = notification_telegram_var
        self.notification_sms_var = notification_sms_var
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Settings Frame
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        settings_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(settings_frame, text="Destructive Op Confirmation Threshold").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.destructive_slider = ctk.CTkSlider(
            settings_frame, from_=0, to=100, number_of_steps=10
        )
        self.destructive_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.destructive_slider.set(80)

        ctk.CTkLabel(settings_frame, text="API Usage Alert Threshold").grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        self.api_usage_slider = ctk.CTkSlider(
            settings_frame, from_=0, to=100, number_of_steps=10
        )
        self.api_usage_slider.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.api_usage_slider.set(50)

        ctk.CTkLabel(settings_frame, text="File Access Warning Threshold").grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )
        self.file_access_slider = ctk.CTkSlider(
            settings_frame, from_=0, to=100, number_of_steps=10
        )
        self.file_access_slider.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.file_access_slider.set(70)

        # Rules Textbox
        ctk.CTkLabel(self, text="Security Rules (one per line)").grid(
            row=1, column=0, padx=10, pady=(10, 0), sticky="w"
        )
        self.security_rules_text = ctk.CTkTextbox(self, height=150)
        self.security_rules_text.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.security_rules_text.insert(
            "1.0",
            "#Example Rule: Deny all shell commands that contain 'rm -rf'\nDENY,TERMINAL,.*rm -rf.*",
        )

        # Plugin Management Frame
        plugin_frame = ctk.CTkFrame(self)
        plugin_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        plugin_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            plugin_frame, text="Plugin Management", font=ctk.CTkFont(weight="bold")
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=10,
            pady=(5, 10),
            sticky="w",
        )

        all_plugins = self.plugin_manager.get_all_plugins()
        row = 1
        if not all_plugins:
            ctk.CTkLabel(
                plugin_frame, text="No plugins found.", text_color="gray"
            ).grid(
                row=row,
                column=0,
                columnspan=2,
                padx=10,
                pady=5,
                sticky="w",
            )
        else:
            for plugin_id, plugin_data in all_plugins.items():
                manifest = plugin_data.get("manifest", {})
                plugin_name = manifest.get("name", plugin_id)
                description = manifest.get("description", "No description provided.")

                var = self.plugin_enabled_vars.get(plugin_id)
                if var is None:
                    var = ctk.BooleanVar()
                    self.plugin_enabled_vars[plugin_id] = var

                cb = ctk.CTkCheckBox(plugin_frame, text=plugin_name, variable=var)
                cb.grid(row=row, column=0, padx=10, pady=5, sticky="w")
                desc_label = ctk.CTkLabel(
                    plugin_frame, text=f"({description})", text_color="gray"
                )
                desc_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")
                row += 1

        # Bottom Frame for Notifications and Buttons
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)

        # Notification Channels
        notification_frame = ctk.CTkFrame(bottom_frame)
        notification_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(notification_frame, text="Notification Channels:").pack(
            side="left", padx=(10, 5)
        )
        ctk.CTkCheckBox(
            notification_frame, text="Email", variable=self.notification_email_var
        ).pack(side="left", padx=5)
        ctk.CTkCheckBox(
            notification_frame, text="Telegram", variable=self.notification_telegram_var
        ).pack(side="left", padx=5)
        ctk.CTkCheckBox(
            notification_frame, text="SMS", variable=self.notification_sms_var
        ).pack(side="left", padx=5)

        # Save/Load Buttons
        button_frame = ctk.CTkFrame(bottom_frame)
        button_frame.grid(row=0, column=1, sticky="e")
        # Add buttons as needed (e.g., Load Settings)

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
