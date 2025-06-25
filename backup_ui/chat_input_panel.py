import customtkinter as ctk
import tkinter as tk

class ChatInputPanel(ctk.CTkFrame):
    """Панель вводу чату з кнопкою Send, мікрофоном, гарячими клавішами та контекстним меню."""
    def __init__(self, master, on_send_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.on_send_callback = on_send_callback
        self.grid_columnconfigure(1, weight=1)

        # Voice input button (left)
        self.voice_button = ctk.CTkButton(
            self,
            text="🎤",
            width=35,
            height=35,
            font=ctk.CTkFont(size=16),
            fg_color="#e0e0e0",
            text_color="black",
            hover_color="#b0b0b0",
            command=self._on_voice_input
        )
        self.voice_button.grid(row=0, column=0, padx=4, pady=2)

        # Message entry field
        self.message_entry = ctk.CTkEntry(self, font=("Helvetica", 13))
        self.message_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=2)

        # Send button (right)
        self.send_button = ctk.CTkButton(
            self,
            text="Send",
            width=50,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#00A0E0",
            text_color="white",
            hover_color="#0077b6",
            command=self._on_send_message
        )
        self.send_button.grid(row=0, column=2, padx=4, pady=2)

        # Bind Enter/Shift+Enter/Ctrl+Enter
        self.message_entry.bind("<Return>", self._on_enter)
        self.message_entry.bind("<Shift-Return>", self._on_shift_enter)
        self.message_entry.bind("<Control-Return>", self._on_ctrl_enter)
        # Mac hotkeys
        self.message_entry.bind("<Command-c>", lambda e: self.message_entry.event_generate("<<Copy>>"))
        self.message_entry.bind("<Command-v>", lambda e: self.message_entry.event_generate("<<Paste>>"))
        self.message_entry.bind("<Command-x>", lambda e: self.message_entry.event_generate("<<Cut>>"))
        self.message_entry.bind("<Command-a>", lambda e: self.message_entry.event_generate("<<SelectAll>>"))
        # Win/Linux hotkeys
        self.message_entry.bind("<Control-c>", lambda e: self.message_entry.event_generate("<<Copy>>"))
        self.message_entry.bind("<Control-v>", lambda e: self.message_entry.event_generate("<<Paste>>"))
        self.message_entry.bind("<Control-x>", lambda e: self.message_entry.event_generate("<<Cut>>"))
        self.message_entry.bind("<Control-a>", lambda e: self.message_entry.event_generate("<<SelectAll>>"))
        # Context menu
        self._setup_entry_context_menu(self.message_entry)

    def _on_send_message(self, event=None):
        text = self.message_entry.get().strip()
        if text:
            self.on_send_callback(text)
            self.message_entry.delete(0, "end")
        return "break"

    def _on_enter(self, event):
        return self._on_send_message(event)

    def _on_shift_enter(self, event):
        # Додає новий рядок, якщо Entry багаторядковий (CTkEntry — ні, але для розширення)
        return None

    def _on_ctrl_enter(self, event):
        # Додає новий рядок, якщо Entry багаторядковий (CTkEntry — ні, але для розширення)
        return None

    def _on_voice_input(self):
        # TODO: інтеграція з voice_assistant, як у chat_history_view
        pass

    def _setup_entry_context_menu(self, entry):
        menu = tk.Menu(entry, tearoff=0)
        menu.add_command(label="Cut", command=lambda: entry.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: entry.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: entry.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: entry.event_generate("<<SelectAll>>"))
        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        entry.bind("<Button-3>", show_menu)
        # Mac: Control+Click
        import platform
        if platform.system() == "Darwin":
            entry.bind("<Control-Button-1>", show_menu)