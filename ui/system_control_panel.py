import customtkinter as ctk
from ui.tooltip import Tooltip

class SystemControlPanel(ctk.CTkFrame):
    def __init__(self, master, agent_manager, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.agent_manager = agent_manager
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="System Control", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=3, pady=(10, 5))

        # Help button
        ctk.CTkButton(self, text="?", width=30, command=self._show_help, fg_color="#3A7CA5").grid(row=0, column=2, padx=10, pady=(10, 5), sticky="e")

        # Mute/Unmute
        mute_btn = ctk.CTkButton(self, text="Mute", command=self._mute)
        mute_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        Tooltip(mute_btn, "Mute system audio")
        unmute_btn = ctk.CTkButton(self, text="Unmute", command=self._unmute)
        unmute_btn.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        Tooltip(unmute_btn, "Unmute system audio")

        # Sleep
        sleep_btn = ctk.CTkButton(self, text="Sleep Mac", command=self._sleep)
        sleep_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        Tooltip(sleep_btn, "Put Mac to sleep")

        # Open App
        ctk.CTkLabel(self, text="Open App:").grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
        self.app_entry = ctk.CTkEntry(self, width=120)
        self.app_entry.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="ew")
        open_btn = ctk.CTkButton(self, text="Open", command=self._open_app)
        open_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        Tooltip(open_btn, "Open the specified app by name")

        # Set Volume
        ctk.CTkLabel(self, text="Set Volume:").grid(row=5, column=0, padx=10, pady=(10, 0), sticky="w")
        self.volume_slider = ctk.CTkSlider(self, from_=0, to=100, number_of_steps=20)
        self.volume_slider.set(50)
        self.volume_slider.grid(row=5, column=1, padx=10, pady=(10, 0), sticky="ew")
        Tooltip(self.volume_slider, "Adjust system volume")
        set_vol_btn = ctk.CTkButton(self, text="Apply Volume", command=self._set_volume)
        set_vol_btn.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        Tooltip(set_vol_btn, "Set system volume to selected level")

        # Current Volume
        self.volume_label = ctk.CTkLabel(self, text="Current Volume: ?")
        self.volume_label.grid(row=7, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")
        refresh_vol_btn = ctk.CTkButton(self, text="Refresh Volume", command=self._refresh_volume)
        refresh_vol_btn.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        Tooltip(refresh_vol_btn, "Get current system volume")

        # Running Apps
        self.apps_label = ctk.CTkLabel(self, text="Running Apps: ?")
        self.apps_label.grid(row=9, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")
        refresh_apps_btn = ctk.CTkButton(self, text="Refresh Apps", command=self._refresh_apps)
        refresh_apps_btn.grid(row=10, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        Tooltip(refresh_apps_btn, "List currently running apps")

        # Feedback
        self.feedback_label = ctk.CTkLabel(self, text="", text_color="#2E8B57")
        self.feedback_label.grid(row=11, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")

        # Status bar
        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor="w", fg_color="#222", text_color="#fff")
        self.status_bar.grid(row=12, column=0, columnspan=3, sticky="ew", padx=0, pady=(10, 0))

        self._refresh_volume()
        self._refresh_apps()

    def _show_help(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("System Control Help")
        dialog.geometry("400x350")
        ctk.CTkLabel(dialog, text="System Control Panel Help", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))
        help_text = (
            "• Mute/Unmute: Control system audio.\n"
            "• Sleep Mac: Put your Mac to sleep.\n"
            "• Open App: Launch any app by name (e.g., Safari, Zoom.us).\n"
            "• Set Volume: Adjust system volume with the slider.\n"
            "• Refresh: Update current volume or running apps.\n"
            "• Status bar: See last action/result.\n"
            "\nTip: Hover over any button for a tooltip."
        )
        ctk.CTkLabel(dialog, text=help_text, wraplength=360, justify="left").pack(padx=20, pady=10)
        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def _mute(self):
        result = self.agent_manager.execute_tool("system_event", {"event": "mute"})
        self._show_feedback(result)
        self._refresh_volume()
        self._set_status("Muted system audio.")

    def _unmute(self):
        result = self.agent_manager.execute_tool("system_event", {"event": "unmute"})
        self._show_feedback(result)
        self._refresh_volume()
        self._set_status("Unmuted system audio.")

    def _sleep(self):
        result = self.agent_manager.execute_tool("system_event", {"event": "sleep"})
        self._show_feedback(result)
        self._set_status("Put Mac to sleep.")

    def _open_app(self):
        app = self.app_entry.get().strip()
        if app:
            result = self.agent_manager.execute_tool("system_event", {"event": "open_app", "app_name": app})
            self._show_feedback(result)
            self._refresh_apps()
            self._set_status(f"Opened app: {app}")
        else:
            self._show_feedback({"status": "error", "error": "Please enter an app name."})
            self._set_status("No app name entered.")

    def _set_volume(self):
        vol = int(self.volume_slider.get())
        result = self.agent_manager.execute_tool("system_event", {"event": "set_volume", "value": vol})
        self._show_feedback(result)
        self._refresh_volume()
        self._set_status(f"Set volume to {vol}%.")

    def _refresh_volume(self):
        result = self.agent_manager.execute_tool("system_event", {"event": "get_volume"})
        if result.get("status") == "success":
            self.volume_label.configure(text=f"Current Volume: {result.get('output')}")
            self._set_status(f"Current volume: {result.get('output')}")
        else:
            self.volume_label.configure(text="Current Volume: ?")
            self._set_status("Could not get volume.")

    def _refresh_apps(self):
        result = self.agent_manager.execute_tool("system_event", {"event": "get_running_apps"})
        if result.get("status") == "success":
            self.apps_label.configure(text=f"Running Apps: {result.get('output')}")
            self._set_status("Refreshed running apps.")
        else:
            self.apps_label.configure(text="Running Apps: ?")
            self._set_status("Could not get running apps.")

    def _show_feedback(self, result):
        if result.get("status") == "success":
            self.feedback_label.configure(text="Success!", text_color="#2E8B57")
        else:
            self.feedback_label.configure(text=f"Error: {result.get('error')}", text_color="#B22222")

    def _set_status(self, msg):
        self.status_bar.configure(text=msg) 