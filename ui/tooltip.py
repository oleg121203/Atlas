import customtkinter as ctk
import tkinter as tk

class Tooltip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay  # milliseconds
        self.tipwindow = None
        self.id = None
        self.widget.bind("<Enter>", self._enter)
        self.widget.bind("<Leave>", self._leave)
        self.widget.bind("<ButtonPress>", self._leave)

    def _enter(self, event=None):
        self._schedule()

    def _leave(self, event=None):
        self._unschedule()
        self._hide_tip()

    def _schedule(self):
        self._unschedule()
        self.id = self.widget.after(self.delay, self._show_tip)

    def _unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def _show_tip(self):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 20
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(tw, text=self.text, fg_color="#222", text_color="#fff", corner_radius=4, font=("Arial", 10))
        label.pack(ipadx=8, ipady=4)

    def _hide_tip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None 