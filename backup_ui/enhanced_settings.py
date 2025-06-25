#!/usr/bin/env python3
"""
Enhanced Settings View for Atlas

Provides comprehensive settings management including security thresholds,
plugin management, and system configuration.
"""

import json
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, Optional

import customtkinter as ctk


class EnhancedSettingsView(ctk.CTkFrame):
    """Enhanced settings view with comprehensive configuration options."""

    def __init__(self, parent, config_manager=None, plugin_manager=None, save_callback: Optional[Callable] = None):
        print("[LOG] EnhancedSettingsView: __init__ called")
        super().__init__(parent)
        self.config_manager = config_manager
        self.plugin_manager = plugin_manager
        self.save_callback = save_callback
        self.settings_vars = {}
        self.plugin_enabled_vars = {}
        
        # Store widgets that should be read-only
        self.readonly_widgets = []
        self.edit_mode = False  # Track edit mode
        
        self.setup_ui()
        self.load_settings()
        self.setup_readonly_fields()

    def setup_ui(self):
        """Setup the enhanced settings UI."""
        #Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        #Create notebook for tabbed interface
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        #Create tabs
        self.setup_general_tab()
        self.setup_security_tab()
        self.setup_llm_tab()
        self.setup_plugins_tab()
        self.setup_notifications_tab()
        self.setup_advanced_tab()

        #Save/Reset buttons at bottom
        self.setup_control_buttons()

    def setup_general_tab(self):
        """Setup general settings tab."""
        tab = self.notebook.add("General")

        #Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        #Application Settings
        app_frame = ctk.CTkFrame(scroll_frame)
        app_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(app_frame, text="Application Settings", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        #Theme selection
        theme_frame = ctk.CTkFrame(app_frame)
        theme_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left", padx=10, pady=5)
        self.settings_vars["theme"] = tk.StringVar(value="system")
        theme_combo = ctk.CTkComboBox(
            theme_frame,
            variable=self.settings_vars["theme"],
            values=["system", "light", "dark"],
        )
        theme_combo.pack(side="right", padx=10, pady=5)

        #Auto-save settings
        self.settings_vars["auto_save"] = tk.BooleanVar(value=True)
        auto_save_check = ctk.CTkCheckBox(
            app_frame,
            text="Auto-save settings on change",
            variable=self.settings_vars["auto_save"],
        )
        auto_save_check.pack(anchor="w", padx=10, pady=2)

        #Enable logging
        self.settings_vars["enable_logging"] = tk.BooleanVar(value=True)
        logging_check = ctk.CTkCheckBox(
            app_frame,
            text="Enable detailed logging",
            variable=self.settings_vars["enable_logging"],
        )
        logging_check.pack(anchor="w", padx=10, pady=2)

        #Log level
        log_level_frame = ctk.CTkFrame(app_frame)
        log_level_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(log_level_frame, text="Log Level:").pack(side="left", padx=10, pady=5)
        self.settings_vars["log_level"] = tk.StringVar(value="INFO")
        log_combo = ctk.CTkComboBox(
            log_level_frame,
            variable=self.settings_vars["log_level"],
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        log_combo.pack(side="right", padx=10, pady=5)

        #Performance Settings
        perf_frame = ctk.CTkFrame(scroll_frame)
        perf_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(perf_frame, text="Performance Settings", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        #Max concurrent operations
        max_ops_frame = ctk.CTkFrame(perf_frame)
        max_ops_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(max_ops_frame, text="Max Concurrent Operations:").pack(side="left", padx=10, pady=5)
        self.settings_vars["max_concurrent_ops"] = tk.StringVar(value="5")
        max_ops_entry = ctk.CTkEntry(max_ops_frame, textvariable=self.settings_vars["max_concurrent_ops"], width=60)
        max_ops_entry.pack(side="right", padx=10, pady=5)

        #Memory limit
        memory_frame = ctk.CTkFrame(perf_frame)
        memory_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(memory_frame, text="Memory Limit (MB):").pack(side="left", padx=10, pady=5)
        self.settings_vars["memory_limit"] = tk.StringVar(value="1024")
        memory_entry = ctk.CTkEntry(memory_frame, textvariable=self.settings_vars["memory_limit"], width=80)
        memory_entry.pack(side="right", padx=10, pady=5)

    def setup_security_tab(self):
        """Setup security settings tab."""
        tab = self.notebook.add("Security")

        #Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        #Security Agent Settings
        security_frame = ctk.CTkFrame(scroll_frame)
        security_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(security_frame, text="Security Agent Settings", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        #Enable security agent
        self.settings_vars["enable_security_agent"] = tk.BooleanVar(value=True)
        security_check = ctk.CTkCheckBox(
            security_frame,
            text="Enable Security Agent monitoring",
            variable=self.settings_vars["enable_security_agent"],
        )
        security_check.pack(anchor="w", padx=10, pady=2)

        #Security thresholds
        threshold_frame = ctk.CTkFrame(security_frame)
        threshold_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(threshold_frame, text="Security Thresholds", font=("Arial", 12, "bold")).pack(
            anchor="w", padx=5, pady=2,
        )

        #File access threshold
        file_threshold_frame = ctk.CTkFrame(threshold_frame)
        file_threshold_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(file_threshold_frame, text="File Access Risk Level:").pack(side="left", padx=5, pady=2)
        self.settings_vars["file_access_threshold"] = tk.StringVar(value="Medium")
        file_combo = ctk.CTkComboBox(
            file_threshold_frame,
            variable=self.settings_vars["file_access_threshold"],
            values=["Low", "Medium", "High", "Critical"],
        )
        file_combo.pack(side="right", padx=5, pady=2)

        #System command threshold
        sys_threshold_frame = ctk.CTkFrame(threshold_frame)
        sys_threshold_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(sys_threshold_frame, text="System Command Risk Level:").pack(side="left", padx=5, pady=2)
        self.settings_vars["system_cmd_threshold"] = tk.StringVar(value="High")
        sys_combo = ctk.CTkComboBox(
            sys_threshold_frame,
            variable=self.settings_vars["system_cmd_threshold"],
            values=["Low", "Medium", "High", "Critical"],
        )
        sys_combo.pack(side="right", padx=5, pady=2)

        #Network access threshold
        net_threshold_frame = ctk.CTkFrame(threshold_frame)
        net_threshold_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(net_threshold_frame, text="Network Access Risk Level:").pack(side="left", padx=5, pady=2)
        self.settings_vars["network_threshold"] = tk.StringVar(value="Medium")
        net_combo = ctk.CTkComboBox(
            net_threshold_frame,
            variable=self.settings_vars["network_threshold"],
            values=["Low", "Medium", "High", "Critical"],
        )
        net_combo.pack(side="right", padx=5, pady=2)

        #Restricted directories
        restricted_frame = ctk.CTkFrame(security_frame)
        restricted_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(restricted_frame, text="Restricted Directories", font=("Arial", 12, "bold")).pack(
            anchor="w", padx=5, pady=2,
        )

        self.restricted_dirs_text = ctk.CTkTextbox(restricted_frame, height=80)
        self.restricted_dirs_text.pack(fill="x", padx=5, pady=2)

        #Add default restricted directories
        default_restricted = "/etc\n/usr/bin\n/System\n/Windows/System32"
        self.restricted_dirs_text.insert(1.0, default_restricted)

    def setup_llm_tab(self):
        """Setup comprehensive LLM settings tab."""
        tab = self.notebook.add("LLM Settings")

        #Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        #Provider Selection
        provider_frame = ctk.CTkFrame(scroll_frame)
        provider_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(provider_frame, text="LLM Provider & Model", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        #Current provider and model
        current_frame = ctk.CTkFrame(provider_frame)
        current_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(current_frame, text="Current Provider:").pack(side="left", padx=10, pady=5)
        self.settings_vars["current_provider"] = tk.StringVar(value="groq")
        provider_combo = ctk.CTkComboBox(
            current_frame,
            variable=self.settings_vars["current_provider"],
            values=["openai", "gemini", "ollama", "groq", "mistral"],
            command=self.on_provider_change,
        )
        provider_combo.pack(side="left", padx=10, pady=5)

        ctk.CTkLabel(current_frame, text="Model:").pack(side="left", padx=(20, 10), pady=5)
        self.settings_vars["current_model"] = tk.StringVar(value="llama3-8b-8192")
        self.model_combo = ctk.CTkComboBox(
            current_frame,
            variable=self.settings_vars["current_model"],
            values=["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
        )
        self.model_combo.pack(side="left", padx=10, pady=5)

        #API Keys Section
        api_frame = ctk.CTkFrame(scroll_frame)
        api_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(api_frame, text="API Keys", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        #OpenAI API Key
        openai_frame = ctk.CTkFrame(api_frame)
        openai_frame.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(openai_frame, text="OpenAI API Key:", width=120).pack(side="left", padx=10, pady=5)
        self.settings_vars["openai_api_key"] = tk.StringVar()
        openai_entry = ctk.CTkEntry(openai_frame, textvariable=self.settings_vars["openai_api_key"],
                                   show="*", width=300)
        openai_entry.pack(side="left", padx=10, pady=5)

        #Gemini API Key
        gemini_frame = ctk.CTkFrame(api_frame)
        gemini_frame.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(gemini_frame, text="Gemini API Key:", width=120).pack(side="left", padx=10, pady=5)
        self.settings_vars["gemini_api_key"] = tk.StringVar()
        gemini_entry = ctk.CTkEntry(gemini_frame, textvariable=self.settings_vars["gemini_api_key"],
                                   show="*", width=300)
        gemini_entry.pack(side="left", padx=10, pady=5)

        #Groq API Key
        groq_frame = ctk.CTkFrame(api_frame)
        groq_frame.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(groq_frame, text="Groq API Key:", width=120).pack(side="left", padx=10, pady=5)
        self.settings_vars["groq_api_key"] = tk.StringVar()
        groq_entry = ctk.CTkEntry(groq_frame, textvariable=self.settings_vars["groq_api_key"],
                                 show="*", width=300)
        groq_entry.pack(side="left", padx=10, pady=5)

        #Mistral API Key
        mistral_frame = ctk.CTkFrame(api_frame)
        mistral_frame.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(mistral_frame, text="Mistral API Key:", width=120).pack(side="left", padx=10, pady=5)
        self.settings_vars["mistral_api_key"] = tk.StringVar()
        mistral_entry = ctk.CTkEntry(mistral_frame, textvariable=self.settings_vars["mistral_api_key"],
                                    show="*", width=300)
        mistral_entry.pack(side="left", padx=10, pady=5)

        #Ollama Settings
        ollama_frame = ctk.CTkFrame(api_frame)
        ollama_frame.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(ollama_frame, text="Ollama URL:", width=120).pack(side="left", padx=10, pady=5)
        self.settings_vars["ollama_url"] = tk.StringVar(value="http://localhost:11434")
        ollama_entry = ctk.CTkEntry(ollama_frame, textvariable=self.settings_vars["ollama_url"], width=300)
        ollama_entry.pack(side="left", padx=10, pady=5)

        #Model Configuration
        model_config_frame = ctk.CTkFrame(scroll_frame)
        model_config_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(model_config_frame, text="Model Configuration", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        #Temperature
        temp_frame = ctk.CTkFrame(model_config_frame)
        temp_frame.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(temp_frame, text="Temperature:", width=120).pack(side="left", padx=10, pady=5)
        self.settings_vars["temperature"] = tk.StringVar(value="0.7")
        temp_entry = ctk.CTkEntry(temp_frame, textvariable=self.settings_vars["temperature"], width=80)
        temp_entry.pack(side="left", padx=10, pady=5)

        #Max tokens
        tokens_frame = ctk.CTkFrame(model_config_frame)
        tokens_frame.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(tokens_frame, text="Max Tokens:", width=120).pack(side="left", padx=10, pady=5)
        self.settings_vars["max_tokens"] = tk.StringVar(value="4096")
        tokens_entry = ctk.CTkEntry(tokens_frame, textvariable=self.settings_vars["max_tokens"], width=80)
        tokens_entry.pack(side="left", padx=10, pady=5)

        #Provider Status
        status_frame = ctk.CTkFrame(scroll_frame)
        status_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(status_frame, text="Provider Status", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        #Test connection button
        test_frame = ctk.CTkFrame(status_frame)
        test_frame.pack(fill="x", padx=10, pady=5)

        self.test_connection_btn = ctk.CTkButton(
            test_frame,
            text="Test Current Provider",
            command=self.test_llm_connection,
        )
        self.test_connection_btn.pack(side="left", padx=10, pady=5)

        self.connection_status_label = ctk.CTkLabel(test_frame, text="Status: Not tested")
        self.connection_status_label.pack(side="left", padx=20, pady=5)

        #Ollama model status
        ollama_status_frame = ctk.CTkFrame(status_frame)
        ollama_status_frame.pack(fill="x", padx=10, pady=5)

        self.check_ollama_btn = ctk.CTkButton(
            ollama_status_frame,
            text="Check Ollama Models",
            command=self.check_ollama_models,
        )
        self.check_ollama_btn.pack(side="left", padx=10, pady=5)

        self.ollama_status_label = ctk.CTkLabel(ollama_status_frame, text="Ollama: Not checked")
        self.ollama_status_label.pack(side="left", padx=20, pady=5)

        #Update model list based on initial provider
        self.on_provider_change("groq")

    def on_provider_change(self, provider: str):
        """Update available models when provider changes."""
        model_lists = {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
            "gemini": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"],
            "ollama": ["llama3.2", "llama3.1", "mistral", "codellama", "phi3", "qwen2", "llama2"],
            "groq": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
            "mistral": ["mistral-tiny", "mistral-small", "mistral-medium", "mistral-large-latest", "open-mistral-7b"],
        }

        models = model_lists.get(provider, ["gpt-3.5-turbo"])
        self.model_combo.configure(values=models)

        #Set default model for the provider
        if models:
            self.settings_vars["current_model"].set(models[0])

    def test_llm_connection(self):
        """Test connection to the current LLM provider."""
        self.connection_status_label.configure(text="Status: Testing...")
        self.test_connection_btn.configure(state="disabled")

        #Import here to avoid circular imports
        try:
            from modules.agents.token_tracker import TokenTracker
            from utils.llm_manager import LLMManager
            from utils.config_manager import ConfigManager
            import requests

            #Create temporary LLM manager for testing
            token_tracker = TokenTracker()
            config_manager = ConfigManager()
            llm_manager = LLMManager(token_tracker, config_manager)

            #Get current settings
            provider = self.settings_vars["current_provider"].get()
            model = self.settings_vars["current_model"].get()

            #Ollama: не потрібен API ключ, просто перевіряємо локальний сервер
            if provider == "ollama":
                def check_ollama():
                    try:
                        response = requests.get("http://localhost:11434/api/version", timeout=5)
                        if response.status_code == 200:
                            self.after(0, lambda: self.connection_status_label.configure(
                                text="Status: ✅ Ollama server is running", text_color="green",
                            ))
                        else:
                            self.after(0, lambda: self.connection_status_label.configure(
                                text="Status: ❌ Ollama server not responding", text_color="red",
                            ))
                    except Exception:
                        self.after(0, lambda: self.connection_status_label.configure(
                            text=f"Status: ❌ Ollama error: {str(e)[:50]}", text_color="red",
                        ))
                    finally:
                        self.after(0, lambda: self.test_connection_btn.configure(state="normal"))
                import threading
                threading.Thread(target=check_ollama, daemon=True).start()
                return

            #Get API key for the current provider
            api_key = ""
            if provider == "groq":
                api_key = self.settings_vars["groq_api_key"].get()
            elif provider == "openai":
                api_key = self.settings_vars["openai_api_key"].get()
            elif provider == "gemini":
                api_key = self.settings_vars["gemini_api_key"].get()
            elif provider == "mistral":
                api_key = self.settings_vars["mistral_api_key"].get()
            
            #Check if API key is provided (тільки для не-ollama)
            if not api_key:
                self.connection_status_label.configure(
                    text=f"Status: ❌ No API key for {provider}", text_color="red"
                )
                self.test_connection_btn.configure(state="normal")
                return

            #Set the provider and model in config manager
            config_manager.set_llm_provider_and_model(provider, model)
            
            #Set API key for the provider in config manager
            config_manager.set_llm_api_key(provider, api_key)

            #Test with a simple message
            test_messages = [{"role": "user", "content": "Hello, this is a connection test. Please respond with 'OK' if you can see this message."}]

            #Run test in a separate thread to avoid blocking UI
            import threading

            def run_test():
                try:
                    #Update settings before testing
                    llm_manager.update_settings()
                    
                    #Test the connection
                    result = llm_manager.chat(test_messages)
                    
                    if result and hasattr(result, 'response_text') and result.response_text:
                        response_preview = result.response_text[:50] + "..." if len(result.response_text) > 50 else result.response_text
                        self.after(0, lambda: self.connection_status_label.configure(
                            text=f"Status: ✅ Connected to {provider} ({model})", text_color="green",
                        ))
                    else:
                        self.after(0, lambda: self.connection_status_label.configure(
                            text=f"Status: ❌ No response from {provider}", text_color="red",
                        ))
                except Exception as e:
                    error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
                    self.after(0, lambda: self.connection_status_label.configure(
                        text=f"Status: ❌ Error: {error_msg}", text_color="red",
                    ))
                finally:
                    self.after(0, lambda: self.test_connection_btn.configure(state="normal"))

            thread = threading.Thread(target=run_test, daemon=True)
            thread.start()

        except Exception as e:
            self.connection_status_label.configure(text=f"Status: ❌ Error: {e!s}", text_color="red")
            self.test_connection_btn.configure(state="normal")

    def check_ollama_models(self):
        """Check which Ollama models are available."""
        self.ollama_status_label.configure(text="Ollama: Checking...")
        self.check_ollama_btn.configure(state="disabled")

        import threading

        def check_models():
            try:
                #Check if Ollama is running
                import requests
                try:
                    response = requests.get("http://localhost:11434/api/version", timeout=5)
                    if response.status_code != 200:
                        self.after(0, lambda: self.ollama_status_label.configure(
                            text="Ollama: Not running", text_color="red",
                        ))
                        return
                except requests.exceptions.RequestException:
                    self.after(0, lambda: self.ollama_status_label.configure(
                        text="Ollama: Not running", text_color="red",
                    ))
                    return

                #Check available models using Ollama API
                try:
                    models_response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    if models_response.status_code == 200:
                        models_data = models_response.json()
                        if "models" in models_data:
                            installed_models = [model["name"] for model in models_data["models"]]
                            if installed_models:
                                status_text = f"Ollama: ✅ {len(installed_models)} models available"
                                self.after(0, lambda: self.ollama_status_label.configure(
                                    text=status_text, text_color="green",
                                ))
                            else:
                                self.after(0, lambda: self.ollama_status_label.configure(
                                    text="Ollama: ❌ No models installed", text_color="orange",
                                ))
                        else:
                            self.after(0, lambda: self.ollama_status_label.configure(
                                text="Ollama: Running but no models", text_color="orange",
                            ))
                    else:
                        self.after(0, lambda: self.ollama_status_label.configure(
                            text="Ollama: API error", text_color="red",
                        ))
                except Exception:
                    self.after(0, lambda: self.ollama_status_label.configure(
                        text=f"Ollama: Error - {str(e)[:30]}...", text_color="red",
                    ))

            except Exception as e:
                # Capture e in the lambda
                self.after(0, lambda e=e: self.ollama_status_label.configure(
                    text=f"Ollama: Error - {str(e)[:30]}...", text_color="red",
                ))
            finally:
                self.after(0, lambda: self.check_ollama_btn.configure(state="normal"))

        thread = threading.Thread(target=check_models, daemon=True)
        thread.start()

    def setup_plugins_tab(self):
        """Setup plugins management tab."""
        tab = self.notebook.add("Plugins")

        #Main frame
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        #Header
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(header_frame, text="Plugin Management", font=("Arial", 14, "bold")).pack(
            side="left", padx=10, pady=10,
        )

        ctk.CTkButton(
            header_frame,
            text="Open Plugin Manager",
            command=self.open_plugin_manager,
            width=150,
        ).pack(side="right", padx=10, pady=10)

        #Plugin list frame
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        #Create scrollable frame for plugins
        scroll_frame = ctk.CTkScrollableFrame(list_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.plugins_container = scroll_frame
        self.load_plugin_controls()

    def setup_notifications_tab(self):
        """Setup notifications settings tab."""
        tab = self.notebook.add("Notifications")

        #Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        #Notification Settings
        notif_frame = ctk.CTkFrame(scroll_frame)
        notif_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(notif_frame, text="Notification Settings", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        #Enable notifications
        self.settings_vars["enable_notifications"] = tk.BooleanVar(value=True)
        notif_check = ctk.CTkCheckBox(
            notif_frame,
            text="Enable notifications",
            variable=self.settings_vars["enable_notifications"],
        )
        notif_check.pack(anchor="w", padx=10, pady=2)

        #Desktop notifications
        self.settings_vars["desktop_notifications"] = tk.BooleanVar(value=True)
        desktop_check = ctk.CTkCheckBox(
            notif_frame,
            text="Desktop notifications",
            variable=self.settings_vars["desktop_notifications"],
        )
        desktop_check.pack(anchor="w", padx=10, pady=2)

        #Sound notifications
        self.settings_vars["sound_notifications"] = tk.BooleanVar(value=False)
        sound_check = ctk.CTkCheckBox(
            notif_frame,
            text="Sound notifications",
            variable=self.settings_vars["sound_notifications"],
        )
        sound_check.pack(anchor="w", padx=10, pady=2)

        #Email notifications
        email_frame = ctk.CTkFrame(scroll_frame)
        email_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(email_frame, text="Email Notifications", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        self.settings_vars["email_notifications"] = tk.BooleanVar(value=False)
        email_check = ctk.CTkCheckBox(
            email_frame,
            text="Enable email notifications",
            variable=self.settings_vars["email_notifications"],
        )
        email_check.pack(anchor="w", padx=10, pady=2)

        #Email settings
        email_settings_frame = ctk.CTkFrame(email_frame)
        email_settings_frame.pack(fill="x", padx=10, pady=5)

        #Email address
        email_addr_frame = ctk.CTkFrame(email_settings_frame)
        email_addr_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(email_addr_frame, text="Email Address:").pack(side="left", padx=5, pady=2)
        self.settings_vars["notification_email"] = tk.StringVar()
        email_entry = ctk.CTkEntry(email_addr_frame, textvariable=self.settings_vars["notification_email"], width=250)
        email_entry.pack(side="right", padx=5, pady=2)

    def setup_advanced_tab(self):
        """Setup advanced settings tab."""
        tab = self.notebook.add("Advanced")

        #Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        #Development Settings
        dev_frame = ctk.CTkFrame(scroll_frame)
        dev_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(dev_frame, text="Development Settings", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        #Debug mode
        self.settings_vars["debug_mode"] = tk.BooleanVar(value=False)
        debug_check = ctk.CTkCheckBox(
            dev_frame,
            text="Enable debug mode",
            variable=self.settings_vars["debug_mode"],
        )
        debug_check.pack(anchor="w", padx=10, pady=2)

        #Verbose logging
        self.settings_vars["verbose_logging"] = tk.BooleanVar(value=False)
        verbose_check = ctk.CTkCheckBox(
            dev_frame,
            text="Verbose logging",
            variable=self.settings_vars["verbose_logging"],
        )
        verbose_check.pack(anchor="w", padx=10, pady=2)

        #Experimental features
        exp_frame = ctk.CTkFrame(scroll_frame)
        exp_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(exp_frame, text="Experimental Features", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        #Enable experimental features
        self.settings_vars["experimental_features"] = tk.BooleanVar(value=False)
        exp_check = ctk.CTkCheckBox(
            exp_frame,
            text="Enable experimental features (may be unstable)",
            variable=self.settings_vars["experimental_features"],
        )
        exp_check.pack(anchor="w", padx=10, pady=2)

        #Auto-update
        self.settings_vars["auto_update"] = tk.BooleanVar(value=True)
        update_check = ctk.CTkCheckBox(
            exp_frame,
            text="Auto-update plugins",
            variable=self.settings_vars["auto_update"],
        )
        update_check.pack(anchor="w", padx=10, pady=2)

        #Data export/import
        data_frame = ctk.CTkFrame(scroll_frame)
        data_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(data_frame, text="Data Management", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5),
        )

        data_buttons_frame = ctk.CTkFrame(data_frame)
        data_buttons_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            data_buttons_frame,
            text="Export Settings",
            command=self.export_settings,
            width=120,
        ).pack(side="left", padx=5, pady=5)

        ctk.CTkButton(
            data_buttons_frame,
            text="Import Settings",
            command=self.import_settings,
            width=120,
        ).pack(side="left", padx=5, pady=5)

        ctk.CTkButton(
            data_buttons_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults,
            width=120,
            fg_color="darkred",
            hover_color="red",
        ).pack(side="right", padx=5, pady=5)

    def setup_control_buttons(self):
        """Setup save/cancel buttons."""
        #Control buttons frame
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        #Save button (повертаю)
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            fg_color="#4CAF50",
            hover_color="#45a049",
            command=self._on_save_button
        )
        save_btn.pack(side="left", padx=5, pady=5)

        #Reload button
        reload_btn = ctk.CTkButton(
            button_frame,
            text="Reload Settings",
            command=self.load_settings,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        reload_btn.pack(side="left", padx=5, pady=5)

        #Reset button
        reset_btn = ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        reset_btn.pack(side="left", padx=5, pady=5)

        #Export/Import buttons
        export_btn = ctk.CTkButton(
            button_frame,
            text="Export Settings",
            command=self.export_settings,
        )
        export_btn.pack(side="right", padx=5, pady=5)

        import_btn = ctk.CTkButton(
            button_frame,
            text="Import Settings",
            command=self.import_settings,
        )
        import_btn.pack(side="right", padx=5, pady=5)

    def _on_save_button(self):
        """Handle Save Settings button click: збирає всі налаштування і викликає save_callback."""
        if self.save_callback:
            # Зібрати всі налаштування з self.settings_vars
            settings = {}
            api_keys = {}
            
            for key, var in self.settings_vars.items():
                if isinstance(var, tk.BooleanVar):
                    value = var.get()
                else:
                    value = var.get()
                
                # Обробляємо API ключі окремо
                if key in ["openai_api_key", "gemini_api_key", "groq_api_key", "mistral_api_key"]:
                    # Витягуємо назву провайдера (частину перед "_api_key")
                    provider = key.replace("_api_key", "")
                    api_keys[provider] = value
                else:
                    settings[key] = value
            
            # Додаємо API ключі як вкладений словник
            if api_keys:
                settings["api_keys"] = api_keys
            
            # Додати плагіни
            plugin_settings = {}
            for plugin_id, var in self.plugin_enabled_vars.items():
                plugin_settings[plugin_id] = var.get()
            settings["plugins_enabled"] = plugin_settings
            
            # Викликати callback
            self.save_callback(settings)

    def load_plugin_controls(self):
        """Load plugin enable/disable controls."""
        #Clear existing controls
        for widget in self.plugins_container.winfo_children():
            widget.destroy()

        if self.plugin_manager:
            #Get plugin list from plugin manager
            plugins = getattr(self.plugin_manager, "plugins", {})

            for plugin_id, plugin_info in plugins.items():
                plugin_frame = ctk.CTkFrame(self.plugins_container)
                plugin_frame.pack(fill="x", pady=2)

                #Plugin name and description
                info_frame = ctk.CTkFrame(plugin_frame)
                info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

                name_label = ctk.CTkLabel(info_frame, text=plugin_info.get("name", plugin_id),
                                         font=("Arial", 12, "bold"))
                name_label.pack(anchor="w", padx=5)

                desc_label = ctk.CTkLabel(info_frame, text=plugin_info.get("description", "No description"),
                                         wraplength=400)
                desc_label.pack(anchor="w", padx=5)

                #Enable/disable checkbox
                self.plugin_enabled_vars[plugin_id] = tk.BooleanVar(value=plugin_info.get("enabled", False))
                plugin_check = ctk.CTkCheckBox(
                    plugin_frame,
                    text="Enabled",
                    variable=self.plugin_enabled_vars[plugin_id],
                )
                plugin_check.pack(side="right", padx=10, pady=5)

    def load_settings(self):
        """Load settings from configuration."""
        if self.config_manager:
            try:
                # Load the full configuration
                if hasattr(self.config_manager, "load"):
                    config = self.config_manager.load()
                else:
                    config = {}
                
                print(f"🔍 Loading settings from config: {list(config.keys())}")
                
                # Load general settings
                for key, var in self.settings_vars.items():
                    value = None
                    
                    # Handle different setting types
                    if key in ["openai_api_key", "gemini_api_key", "groq_api_key", "mistral_api_key"]:
                        # Витягуємо назву провайдера (частину перед "_api_key")
                        provider = key.replace("_api_key", "")
                        value = config.get("api_keys", {}).get(provider, "")
                    elif key == "current_provider":
                        value = config.get("current_provider", "groq")
                    elif key == "current_model":
                        value = config.get("current_model", "llama3-8b-8192")
                    elif key == "temperature":
                        value = config.get("temperature", 0.7)
                    elif key == "max_tokens":
                        value = config.get("max_tokens", 4096)
                    elif key == "ollama_url":
                        value = config.get("ollama_url", "http://localhost:11434")
                    elif key in ["enable_security_agent", "enable_notifications", "desktop_notifications", 
                               "sound_notifications", "email_notifications", "debug_mode", 
                               "verbose_logging", "experimental_features", "auto_update"]:
                        # Boolean settings with defaults
                        value = config.get(key, False)
                    elif key == "notification_email":
                        value = config.get("notification_email", "")
                    elif key == "theme":
                        value = config.get("theme", "system")
                    elif key == "auto_save":
                        value = config.get("auto_save", True)
                    elif key == "enable_logging":
                        value = config.get("enable_logging", True)
                    elif key == "log_level":
                        value = config.get("log_level", "INFO")
                    elif key == "max_concurrent_ops":
                        value = config.get("max_concurrent_ops", 5)
                    elif key == "memory_limit":
                        value = config.get("memory_limit", 1024)
                    elif key in ["file_access_threshold", "system_cmd_threshold", "network_threshold"]:
                        # Security thresholds with defaults
                        value = config.get(key, "Medium")
                    else:
                        # Plugin settings
                        if key.startswith("plugin_"):
                            plugin_name = key.replace("plugin_", "")
                            value = config.get("plugins_enabled", {}).get(plugin_name, False)
                        else:
                            value = config.get(key, "")
                    
                    # Set the value
                    if value is not None:
                        if isinstance(var, tk.BooleanVar):
                            var.set(bool(value))
                        elif isinstance(var, tk.StringVar):
                            var.set(str(value))
                        elif isinstance(var, tk.DoubleVar):
                            var.set(float(value))
                        elif isinstance(var, tk.IntVar):
                            var.set(int(value))
                        print(f"   ✅ Loaded {key}: {value}")
                    else:
                        # Set default values for missing settings
                        if isinstance(var, tk.BooleanVar):
                            var.set(False)
                            print(f"   ⚠️ No value found for {key}, using default: False")
                        elif isinstance(var, tk.StringVar):
                            var.set("")
                            print(f"   ⚠️ No value found for {key}, using default: ''")
                        elif isinstance(var, tk.DoubleVar):
                            var.set(0.0)
                            print(f"   ⚠️ No value found for {key}, using default: 0.0")
                        elif isinstance(var, tk.IntVar):
                            var.set(0)
                            print(f"   ⚠️ No value found for {key}, using default: 0")
                        else:
                            var.set("")
                            print(f"   ⚠️ No value found for {key}, using default: ''")

                # Load restricted directories
                restricted_dirs = config.get("restricted_directories", [])
                if hasattr(self, "restricted_dirs_text"):
                    self.restricted_dirs_text.delete(1.0, tk.END)
                    self.restricted_dirs_text.insert(1.0, "\n".join(restricted_dirs))
                
                # Load plugin settings
                plugin_states = config.get("plugins_enabled", {})
                for plugin_id, var in self.plugin_enabled_vars.items():
                    enabled = plugin_states.get(plugin_id, True)  # Default to enabled
                    var.set(enabled)
                    print(f"   ✅ Loaded plugin {plugin_id}: {enabled}")
                
                print("✅ Settings loaded successfully!")
                
            except Exception as e:
                print(f"❌ Error loading settings: {e}")
                import traceback
                traceback.print_exc()

    def open_plugin_manager(self):
        """Open the enhanced plugin manager."""
        from ui.enhanced_plugin_manager import EnhancedPluginManagerWindow
        EnhancedPluginManagerWindow(self.winfo_toplevel(), self.plugin_manager)

    def export_settings(self):
        """Export settings to a file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if file_path:
            try:
                settings = {}
                for key, var in self.settings_vars.items():
                    if isinstance(var, tk.BooleanVar):
                        settings[key] = var.get()
                    else:
                        settings[key] = var.get()

                with open(file_path, "w") as f:
                    json.dump(settings, f, indent=2)

                messagebox.showinfo("Export", f"Settings exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export settings:\n{e}")

    def import_settings(self):
        """Import settings from a file."""
        file_path = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if file_path:
            try:
                with open(file_path) as f:
                    settings = json.load(f)

                #Apply imported settings
                for key, value in settings.items():
                    if key in self.settings_vars:
                        var = self.settings_vars[key]
                        if isinstance(var, tk.BooleanVar):
                            var.set(bool(value))
                        else:
                            var.set(str(value))

                messagebox.showinfo("Import", "Settings imported successfully!")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import settings:\n{e}")

    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        result = messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?\nThis action cannot be undone.",
        )

        if result:
            #Set default values
            defaults = {
                "theme": "system",
                "auto_save": True,
                "enable_logging": True,
                "log_level": "INFO",
                "max_concurrent_ops": "5",
                "memory_limit": "1024",
                "enable_security_agent": True,
                "file_access_threshold": "Medium",
                "system_cmd_threshold": "High",
                "network_threshold": "Medium",
                "default_model": "gpt-4",
                "temperature": "0.7",
                "max_tokens": "4096",
                "daily_token_limit": "100000",
                "enable_notifications": True,
                "desktop_notifications": True,
                "sound_notifications": False,
                "email_notifications": False,
                "debug_mode": False,
                "verbose_logging": False,
                "experimental_features": False,
                "auto_update": True,
            }

            for key, value in defaults.items():
                if key in self.settings_vars:
                    var = self.settings_vars[key]
                    if isinstance(var, tk.BooleanVar):
                        var.set(bool(value))
                    else:
                        var.set(str(value))

            messagebox.showinfo("Reset", "Settings reset to defaults!")

    def setup_readonly_fields(self):
        """Set up read-only fields for important configuration values."""
        # Make important configuration fields read-only to prevent accidental editing
        
        # Store important widgets that should be read-only by default
        self.readonly_widgets = []
        
        # Make restricted directories text read-only (important security setting)
        if hasattr(self, 'restricted_dirs_text'):
            self.restricted_dirs_text.configure(state="disabled")
            self.readonly_widgets.append(self.restricted_dirs_text)
            
            # Add a small label to indicate it's read-only
            try:
                readonly_label = ctk.CTkLabel(
                    self.restricted_dirs_text.master, 
                    text="🔒 Read-only", 
                    font=("Arial", 10),
                    text_color="#888888"
                )
                readonly_label.pack(side="right", padx=(5, 0))
            except:
                pass
        
        # Make API key fields read-only (should be managed through secure methods)
        # Note: These will be made read-only by default, but can be unlocked via edit mode
        api_key_fields = ["openai_api_key", "gemini_api_key", "groq_api_key", "mistral_api_key"]
        
        # Find and store API key entry widgets
        def find_api_key_widgets(parent):
            for child in parent.winfo_children():
                if hasattr(child, 'winfo_children'):
                    find_api_key_widgets(child)
                elif hasattr(child, 'cget'):
                    try:
                        textvar = child.cget('textvariable')
                        if textvar and any(key in textvar for key in api_key_fields):
                            child.configure(state="disabled")
                            self.readonly_widgets.append(child)
                    except:
                        pass
        
        find_api_key_widgets(self)
        
        # Update button text based on initial state
        if hasattr(self, 'edit_mode_btn'):
            self.edit_mode_btn.configure(text="🔒 Locked (Click to Edit)")

    def toggle_edit_mode(self):
        """Toggle edit mode."""
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.edit_mode_btn.configure(text="✏️ Unlocked (Click to Lock)")
            for widget in self.readonly_widgets:
                widget.configure(state="normal")
        else:
            self.edit_mode_btn.configure(text="🔒 Locked (Click to Edit)")
            for widget in self.readonly_widgets:
                widget.configure(state="disabled")
