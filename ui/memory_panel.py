import customtkinter as ctk

class MemoryPanel(ctk.CTkFrame):
    def __init__(self, master, collections=None, on_search=None, on_refresh=None, on_clear=None, **kwargs):
        super().__init__(master, **kwargs)
        self.collections = collections or []
        self.on_search = on_search
        self.on_refresh = on_refresh
        self.on_clear = on_clear
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        # Список колекцій
        ctk.CTkLabel(self, text="Collections", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.collections_box = ctk.CTkComboBox(self, values=self.collections)
        self.collections_box.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        # Поле пошуку
        ctk.CTkLabel(self, text="Search").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.search_entry = ctk.CTkEntry(self)
        self.search_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkButton(self, text="Search", command=self._search).grid(row=1, column=2, padx=5, pady=5)
        # Область перегляду
        self.content_box = ctk.CTkTextbox(self, height=15)
        self.content_box.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=3, column=0, columnspan=3, sticky="e", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Refresh", command=self._refresh).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Clear", command=self._clear).pack(side="left", padx=5)
    def _search(self):
        if callable(self.on_search):
            self.on_search(self.search_entry.get())
    def _refresh(self):
        if callable(self.on_refresh):
            self.on_refresh()
    def _clear(self):
        if callable(self.on_clear):
            self.on_clear()
        self.content_box.delete("1.0", "end") 