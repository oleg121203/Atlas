import customtkinter as ctk


class PerformancePanel(ctk.CTkFrame):
    def __init__(self, master, metrics_manager=None, on_clear=None, **kwargs):
        super().__init__(master, **kwargs)
        self.metrics_manager = metrics_manager
        self.on_clear = on_clear
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        header = ctk.CTkLabel(
            self, text="Performance Monitoring", font=ctk.CTkFont(weight="bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        # Статистика
        self.stats_label = ctk.CTkLabel(self, text="No data yet.")
        self.stats_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        # Кнопка очищення
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=2, column=0, sticky="e", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Clear Data", command=self._clear).pack(
            side="right", padx=5
        )
        # (Місце для графіків, якщо потрібно)

    def update_stats(self, stats_text):
        self.stats_label.configure(text=stats_text)

    def _clear(self):
        if callable(self.on_clear):
            self.on_clear()
        self.update_stats("No data yet.")
