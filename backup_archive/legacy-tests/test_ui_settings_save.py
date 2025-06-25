#!/usr/bin/env python3
"""
Test UI settings save functionality
"""

import customtkinter as ctk
import threading
import time
from utils.config_manager import ConfigManager

class UISettingsTestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("UI Settings Save Test")
        self.geometry("800x600")
        
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
        title_label = ctk.CTkLabel(main_frame, text="UI Settings Save Test", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=10)
        
        # Instructions
        instructions = """Instructions:
1. Enter a Groq API key
2. Select 'groq' as provider
3. Select a Groq model
4. Click 'Save Settings'
5. Check if settings are saved correctly"""
        
        instruction_label = ctk.CTkLabel(main_frame, text=instructions, justify="left")
        instruction_label.pack(pady=10)
        
        # Groq API Key
        groq_frame = ctk.CTkFrame(main_frame)
        groq_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(groq_frame, text="Groq API Key:").pack(anchor="w", padx=10, pady=5)
        self.groq_entry = ctk.CTkEntry(groq_frame, textvariable=self.groq_api_key_var, show="*", width=400)
        self.groq_entry.pack(padx=10, pady=5)
        
        # Provider selection
        provider_frame = ctk.CTkFrame(main_frame)
        provider_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(provider_frame, text="Current Provider:").pack(anchor="w", padx=10, pady=5)
        self.provider_menu = ctk.CTkOptionMenu(
            provider_frame, 
            variable=self.current_provider_var,
            values=["gemini", "groq", "openai", "anthropic", "mistral"]
        )
        self.provider_menu.pack(padx=10, pady=5)
        
        # Model selection
        model_frame = ctk.CTkFrame(main_frame)
        model_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(model_frame, text="Current Model:").pack(anchor="w", padx=10, pady=5)
        self.model_menu = ctk.CTkOptionMenu(
            model_frame, 
            variable=self.current_model_var,
            values=["gemini-1.5-flash", "llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
        )
        self.model_menu.pack(padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.save_button = ctk.CTkButton(button_frame, text="Save Settings", command=self._save_settings)
        self.save_button.pack(side="left", padx=5)
        
        self.load_button = ctk.CTkButton(button_frame, text="Load Settings", command=self._load_settings)
        self.load_button.pack(side="left", padx=5)
        
        self.test_button = ctk.CTkButton(button_frame, text="Test Save from UI", command=self._test_save_from_ui)
        self.test_button.pack(side="left", padx=5)
        
        self.verify_button = ctk.CTkButton(button_frame, text="Verify File", command=self._verify_file)
        self.verify_button.pack(side="left", padx=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(main_frame, text="Ready", text_color="gray")
        self.status_label.pack(pady=10)
        
        # Current settings display
        self.settings_text = ctk.CTkTextbox(main_frame, height=200)
        self.settings_text.pack(fill="x", padx=10, pady=10)
        
    def _load_current_settings(self):
        """Load current settings from config file."""
        try:
            settings = self.config_manager.load()
            
            # Update UI with current settings
            self.groq_api_key_var.set(settings.get("api_keys", {}).get("groq", ""))
            self.current_provider_var.set(settings.get("current_provider", "gemini"))
            self.current_model_var.set(settings.get("current_model", "gemini-1.5-flash"))
            
            self._update_settings_display(settings)
            self.status_label.configure(text="Settings loaded", text_color="green")
            
        except Exception as e:
            self.status_label.configure(text=f"Error loading: {e}", text_color="red")
    
    def _save_settings(self):
        """Save current settings from UI."""
        try:
            # Get current values from UI
            groq_key = self.groq_api_key_var.get()
            current_provider = self.current_provider_var.get()
            current_model = self.current_model_var.get()
            
            # Create settings dictionary (similar to main.py _save_settings)
            settings = {
                "current_provider": current_provider,
                "current_model": current_model,
                "api_keys": {
                    "groq": groq_key,
                    "gemini": "",
                    "openai": "",
                    "anthropic": "",
                    "mistral": ""
                },
                "plugins_enabled": {},
                "security": {
                    "destructive_op_threshold": 80,
                    "api_usage_threshold": 50,
                    "file_access_threshold": 70,
                    "rules": [],
                    "notifications": {
                        "email": False,
                        "telegram": False,
                        "sms": False
                    }
                },
                "agents": {}
            }
            
            # Save to config file
            self.config_manager.save(settings)
            
            self.status_label.configure(text=f"Settings saved! Provider: {current_provider}, Model: {current_model}", text_color="green")
            self._update_settings_display(settings)
            
        except Exception as e:
            self.status_label.configure(text=f"Error saving: {e}", text_color="red")
    
    def _load_settings(self):
        """Load settings from config file."""
        self._load_current_settings()
    
    def _test_save_from_ui(self):
        """Test save with specific UI values."""
        try:
            # Set test values in UI
            self.groq_api_key_var.set("gsk_test-ui-groq-key-789")
            self.current_provider_var.set("groq")
            self.current_model_var.set("llama3-70b-8192")
            
            # Save immediately
            self._save_settings()
            
            # Wait a moment and reload to verify
            def verify_save():
                time.sleep(1)
                self._load_current_settings()
                self.status_label.configure(text="Test completed - check if UI settings persisted", text_color="blue")
            
            threading.Thread(target=verify_save, daemon=True).start()
            
        except Exception as e:
            self.status_label.configure(text=f"Test error: {e}", text_color="red")
    
    def _verify_file(self):
        """Verify the config file content."""
        try:
            config_path = self.config_manager.path
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Check for key values
            checks = []
            checks.append(("groq" in content, "groq provider"))
            checks.append(("llama3" in content or "mixtral" in content, "groq model"))
            checks.append(("gsk_" in content, "groq api key"))
            
            passed = sum(1 for check, _ in checks if check)
            total = len(checks)
            
            status = f"File verification: {passed}/{total} checks passed"
            color = "green" if passed == total else "orange"
            
            self.status_label.configure(text=status, text_color=color)
            
            # Update display with file content
            self.settings_text.delete("1.0", "end")
            self.settings_text.insert("1.0", f"Config file content:\n{content}")
            
        except Exception as e:
            self.status_label.configure(text=f"Verification error: {e}", text_color="red")
    
    def _update_settings_display(self, settings):
        """Update the settings display text."""
        display_text = f"""Current Settings:
Provider: {settings.get('current_provider', 'N/A')}
Model: {settings.get('current_model', 'N/A')}
Groq Key: {settings.get('api_keys', {}).get('groq', 'N/A')[:10]}...

UI Values:
Provider: {self.current_provider_var.get()}
Model: {self.current_model_var.get()}
Groq Key: {self.groq_api_key_var.get()[:10] if self.groq_api_key_var.get() else 'N/A'}...

Config Path: {self.config_manager.path}
Config Exists: {self.config_manager.path.exists()}
"""
        
        self.settings_text.delete("1.0", "end")
        self.settings_text.insert("1.0", display_text)

def main():
    app = UISettingsTestApp()
    app.mainloop()

if __name__ == "__main__":
    main() 