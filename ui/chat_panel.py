import customtkinter as ctk
from ui.chat_input_panel import ChatInputPanel

class ChatPanel(ctk.CTkFrame):
    def __init__(self, master, chat_history_view, chat_input_panel=None):
        super().__init__(master)
        self.chat_history_view = chat_history_view
        if chat_input_panel is None:
            self.chat_input_panel = ChatInputPanel(self, self._on_send_message)
        else:
            self.chat_input_panel = chat_input_panel
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.chat_history_view.grid(row=0, column=0, sticky="nsew")
        self.chat_input_panel.grid(row=1, column=0, sticky="ew")

    def _on_send_message(self, text):
        # Додає повідомлення користувача в історію чату
        if hasattr(self.chat_history_view, "add_message"):
            self.chat_history_view.add_message("user", text)

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs) 