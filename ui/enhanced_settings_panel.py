import customtkinter as ctk
from ui.enhanced_settings import EnhancedSettingsView

class EnhancedSettingsPanel(ctk.CTkFrame):
    def __init__(self, master, config_manager, plugin_manager, save_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config_manager = config_manager
        self.plugin_manager = plugin_manager
        self.save_callback = save_callback
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.enhanced_settings = EnhancedSettingsView(
            self,
            config_manager=self.config_manager,
            plugin_manager=self.plugin_manager,
            save_callback=self.save_callback,
        )
        self.enhanced_settings.grid(row=0, column=0, sticky="nsew")

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs) 