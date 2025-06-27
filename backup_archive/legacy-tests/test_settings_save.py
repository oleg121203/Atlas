#!/usr/bin/env python3
"""
Test script for real-time settings save
"""

import threading
import time

import customtkinter as ctk

from utils.config_manager import ConfigManager


class SettingsTestApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Settings Save Test")
        self.geometry("600x400")

        self.config_manager = ConfigManager()

        # Initialize variables
        self.groq_api_key_var = ctk.StringVar()
        self.current_provider_var = ctk.StringVar(value="gemini")
        self.current_model_var = ctk.StringVar(value="gemini-1.5-flash")

        self._create_widgets()
        self._load_current_settings()

    def _create_widgets(self):
        """Create the UI widgets."""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Settings Save Test",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(pady=10)

        # Groq API Key
        groq_frame = ctk.CTkFrame(main_frame)
        groq_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(groq_frame, text="Groq API Key:").pack(anchor="w", padx=10, pady=5)
        self.groq_entry = ctk.CTkEntry(
            groq_frame, textvariable=self.groq_api_key_var, show="*", width=400
        )
        self.groq_entry.pack(padx=10, pady=5)

        # Provider selection
        provider_frame = ctk.CTkFrame(main_frame)
        provider_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(provider_frame, text="Current Provider:").pack(
            anchor="w", padx=10, pady=5
        )
        self.provider_menu = ctk.CTkOptionMenu(
            provider_frame,
            variable=self.current_provider_var,
            values=["gemini", "groq", "openai", "anthropic", "mistral"],
        )
        self.provider_menu.pack(padx=10, pady=5)

        # Model selection
        model_frame = ctk.CTkFrame(main_frame)
        model_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(model_frame, text="Current Model:").pack(
            anchor="w", padx=10, pady=5
        )
        self.model_menu = ctk.CTkOptionMenu(
            model_frame,
            variable=self.current_model_var,
            values=["gemini-1.5-flash", "llama3-8b-8192", "gpt-4", "claude-3-sonnet"],
        )
        self.model_menu.pack(padx=10, pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        self.save_button = ctk.CTkButton(
            button_frame, text="Save Settings", command=self._save_settings
        )
        self.save_button.pack(side="left", padx=5)

        self.load_button = ctk.CTkButton(
            button_frame, text="Load Settings", command=self._load_settings
        )
        self.load_button.pack(side="left", padx=5)

        self.test_button = ctk.CTkButton(
            button_frame, text="Test Save", command=self._test_save
        )
        self.test_button.pack(side="left", padx=5)

        # Status label
        self.status_label = ctk.CTkLabel(main_frame, text="Ready", text_color="gray")
        self.status_label.pack(pady=10)

        # Current settings display
        self.settings_text = ctk.CTkTextbox(main_frame, height=150)
        self.settings_text.pack(fill="x", padx=10, pady=10)

    def _load_current_settings(self):
        """Load current settings from config file."""
        try:
            settings = self.config_manager.load()

            # Update UI with current settings
            self.groq_api_key_var.set(settings.get("api_keys", {}).get("groq", ""))
            self.current_provider_var.set(settings.get("current_provider", "gemini"))
            self.current_model_var.set(
                settings.get("current_model", "gemini-1.5-flash")
            )

            self._update_settings_display(settings)
            self.status_label.configure(text="Settings loaded", text_color="green")

        except Exception as e:
            self.status_label.configure(text=f"Error loading: {e}", text_color="red")

    def _save_settings(self):
        """Save current settings."""
        try:
            # Get current values from UI
            groq_key = self.groq_api_key_var.get()
            current_provider = self.current_provider_var.get()
            current_model = self.current_model_var.get()

            # Create settings dictionary
            settings = {
                "current_provider": current_provider,
                "current_model": current_model,
                "api_keys": {
                    "groq": groq_key,
                    "gemini": "",
                    "openai": "",
                    "anthropic": "",
                    "mistral": "",
                },
                "plugins_enabled": {},
                "security": {
                    "destructive_op_threshold": 80,
                    "api_usage_threshold": 50,
                    "file_access_threshold": 70,
                    "rules": [],
                    "notifications": {"email": False, "telegram": False, "sms": False},
                },
                "agents": {},
            }

            # Save to config file
            self.config_manager.save(settings)

            self.status_label.configure(
                text=f"Settings saved! Provider: {current_provider}, Model: {current_model}",
                text_color="green",
            )
            self._update_settings_display(settings)

        except Exception as e:
            self.status_label.configure(text=f"Error saving: {e}", text_color="red")

    def _load_settings(self):
        """Load settings from config file."""
        self._load_current_settings()

    def _test_save(self):
        """Test save with specific values."""
        try:
            # Set test values
            self.groq_api_key_var.set("gsk_test-groq-key-123")
            self.current_provider_var.set("groq")
            self.current_model_var.set("llama3-8b-8192")

            # Save immediately
            self._save_settings()

            # Wait a moment and reload to verify
            def verify_save():
                time.sleep(1)
                self._load_current_settings()
                self.status_label.configure(
                    text="Test completed - check if settings persisted",
                    text_color="blue",
                )

            threading.Thread(target=verify_save, daemon=True).start()

        except Exception as e:
            self.status_label.configure(text=f"Test error: {e}", text_color="red")

    def _update_settings_display(self, settings):
        """Update the settings display text."""
        display_text = f"""Current Settings:
Provider: {settings.get("current_provider", "N/A")}
Model: {settings.get("current_model", "N/A")}
Groq Key: {settings.get("api_keys", {}).get("groq", "N/A")[:10]}...

Full Config Path: {self.config_manager.path}
Config Exists: {self.config_manager.path.exists()}
"""

        self.settings_text.delete("1.0", "end")
        self.settings_text.insert("1.0", display_text)


def main():
    app = SettingsTestApp()
    app.mainloop()


if __name__ == "__main__":
    main()
