import customtkinter as ctk


class LogPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.log_textbox = ctk.CTkTextbox(
            self, font=("monospace", 12), state="disabled"
        )
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        # Кнопки для копіювання та очищення
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Copy All", command=self.copy_all).pack(
            side="left", padx=5
        )
        ctk.CTkButton(btn_frame, text="Clear", command=self.clear).pack(
            side="left", padx=5
        )

    def add_log(self, text):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", text + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def clear(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    def copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(self.log_textbox.get("1.0", "end"))
