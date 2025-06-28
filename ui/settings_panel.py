from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class SettingsPanel(QWidget):
    def __init__(
        self,
        parent=None,
        openai_api_key_var=None,
        gemini_api_key_var=None,
        groq_api_key_var=None,
        mistral_api_key_var=None,
        anthropic_api_key_var=None,
        plugin_manager=None,
        plugin_enabled_vars=None,
        loaded_settings=None,
        on_save_settings=None,
        on_reset_tokens=None,
        on_toggle_all_plugins=None,
        on_populate_plugins=None,
        **kwargs,
    ):
        super().__init__(parent)
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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # API Keys Frame
        api_keys_frame = QFrame()
        api_keys_frame.setObjectName("settingsFrame")
        api_keys_frame.setStyleSheet("""
            QFrame#settingsFrame {
                border: 1px solid palette(mid);
                border-radius: 4px;
                background: palette(window);
            }
        """)
        api_keys_layout = QGridLayout(api_keys_frame)
        api_keys_layout.setContentsMargins(10, 10, 10, 10)
        api_keys_layout.setSpacing(5)

        title_label = QLabel("API Keys")
        title_label.setStyleSheet("font-weight: bold;")
        api_keys_layout.addWidget(title_label, 0, 0, 1, 2)

        # Create API key entries
        api_keys = [
            ("OpenAI API Key", self.openai_api_key_var),
            ("Gemini API Key", self.gemini_api_key_var),
            ("Groq API Key", self.groq_api_key_var),
            ("Mistral API Key", self.mistral_api_key_var),
            ("Anthropic API Key", self.anthropic_api_key_var),
        ]

        for idx, (label_text, key_var) in enumerate(api_keys, 1):
            label = QLabel(label_text)
            entry = QLineEdit()
            entry.setEchoMode(QLineEdit.EchoMode.Password)
            if key_var is not None:
                entry.setText(
                    key_var.get() if hasattr(key_var, "get") else str(key_var)
                )
            api_keys_layout.addWidget(label, idx, 0)
            api_keys_layout.addWidget(entry, idx, 1)
            setattr(self, f"{label_text.lower().replace(' ', '_')}_entry", entry)

        layout.addWidget(api_keys_frame)

        # Plugin Management Frame
        plugin_frame = QFrame()
        plugin_frame.setObjectName("pluginFrame")
        plugin_frame.setStyleSheet("""
            QFrame#pluginFrame {
                border: 1px solid palette(mid);
                border-radius: 4px;
                background: palette(window);
            }
        """)
        plugin_layout = QVBoxLayout(plugin_frame)
        plugin_layout.setContentsMargins(10, 10, 10, 10)
        plugin_layout.setSpacing(5)

        plugin_header = QHBoxLayout()
        plugin_title = QLabel("Plugin Management")
        plugin_title.setStyleSheet("font-weight: bold;")
        plugin_header.addWidget(plugin_title)
        plugin_header.addStretch()

        plugin_buttons = QHBoxLayout()
        enable_all_btn = QPushButton("Enable All")
        disable_all_btn = QPushButton("Disable All")
        if self.on_toggle_all_plugins:
            enable_all_btn.clicked.connect(lambda: self.on_toggle_all_plugins(True))
            disable_all_btn.clicked.connect(lambda: self.on_toggle_all_plugins(False))
        plugin_buttons.addWidget(enable_all_btn)
        plugin_buttons.addWidget(disable_all_btn)
        plugin_header.addLayout(plugin_buttons)

        plugin_layout.addLayout(plugin_header)

        # Plugin scroll area
        plugin_scroll = QScrollArea()
        plugin_scroll.setWidgetResizable(True)
        plugin_content = QWidget()
        plugin_scroll.setWidget(plugin_content)
        plugin_layout.addWidget(plugin_scroll)

        if self.on_populate_plugins:
            self.on_populate_plugins(plugin_content)

        layout.addWidget(plugin_frame)

        # Token Usage Statistics
        token_frame = QFrame()
        token_frame.setObjectName("tokenFrame")
        token_frame.setStyleSheet("""
            QFrame#tokenFrame {
                border: 1px solid palette(mid);
                border-radius: 4px;
                background: palette(window);
            }
        """)
        token_layout = QGridLayout(token_frame)
        token_layout.setContentsMargins(10, 10, 10, 10)
        token_layout.setSpacing(5)

        token_title = QLabel("Token Usage Statistics")
        token_title.setStyleSheet("font-weight: bold;")
        token_layout.addWidget(token_title, 0, 0, 1, 3)

        labels = ["Prompt:", "Completion:", "Total:"]
        self.token_labels = {}

        for idx, label_text in enumerate(labels, 1):
            label = QLabel(label_text)
            value = QLabel("0")
            if label_text == "Total:":
                value.setStyleSheet("font-weight: bold;")
            token_layout.addWidget(label, idx, 0)
            token_layout.addWidget(value, idx, 1)
            self.token_labels[label_text.lower().replace(":", "")] = value

        reset_button = QPushButton("Reset")
        if self.on_reset_tokens:
            reset_button.clicked.connect(self.on_reset_tokens)
        token_layout.addWidget(reset_button, 1, 2, 3, 1)

        layout.addWidget(token_frame)

        # Save Button
        save_button = QPushButton("Save Settings")
        if self.on_save_settings:
            save_button.clicked.connect(self.on_save_settings)
        layout.addWidget(save_button)

    def update_token_count(self, prompt_tokens, completion_tokens, total_tokens):
        """Update the token count display"""
        self.token_labels["prompt"].setText(str(prompt_tokens))
        self.token_labels["completion"].setText(str(completion_tokens))
        self.token_labels["total"].setText(str(total_tokens))
