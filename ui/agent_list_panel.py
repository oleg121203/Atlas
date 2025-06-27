import customtkinter as ctk


class AgentListPanel(ctk.CTkFrame):
    def __init__(
        self, master, agents, on_start_agent=None, on_stop_agent=None, **kwargs
    ):
        super().__init__(master, **kwargs)
        self.agents = agents
        self.on_start_agent = on_start_agent
        self.on_stop_agent = on_stop_agent
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        header = ctk.CTkLabel(self, text="Agents", font=ctk.CTkFont(weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Agent List")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.grid_rowconfigure(1, weight=1)
        self._populate_agents()

    def _populate_agents(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        for agent_id, agent in self.agents.items():
            frame = ctk.CTkFrame(self.scroll_frame)
            frame.pack(fill="x", padx=5, pady=3)
            ctk.CTkLabel(
                frame, text=agent_id, font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=5)
            status = getattr(agent, "status", "Unknown")
            ctk.CTkLabel(frame, text=f"Status: {status}").pack(side="left", padx=5)
            if callable(self.on_start_agent):
                ctk.CTkButton(
                    frame,
                    text="Start",
                    width=60,
                    command=lambda aid=agent_id: self.on_start_agent(aid),
                ).pack(side="right", padx=2)
            if callable(self.on_stop_agent):
                ctk.CTkButton(
                    frame,
                    text="Stop",
                    width=60,
                    command=lambda aid=agent_id: self.on_stop_agent(aid),
                ).pack(side="right", padx=2)
