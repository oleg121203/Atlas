"""
Custom logging handler to display log messages in a Tkinter widget.
"""

import logging
import queue
import customtkinter as ctk

class GuiLogger(logging.Handler):
    """A thread-safe handler class which writes logging records to a CTkTextbox widget."""

    def __init__(self, textbox: ctk.CTkTextbox):
        super().__init__()
        self.textbox = textbox
        self.log_queue = queue.Queue()

        #Define color tags for different log levels
        self.textbox.tag_config("INFO", foreground="white")
        self.textbox.tag_config("WARNING", foreground="yellow")
        self.textbox.tag_config("ERROR", foreground="red")
        self.textbox.tag_config("CRITICAL", foreground="red")
        self.textbox.tag_config("DEBUG", foreground="gray")

        self.textbox.configure(state='disabled')
        self.start_polling()

    def emit(self, record: logging.LogRecord):
        """Add the log record to the queue for thread-safe processing."""
        self.log_queue.put(record)

    def start_polling(self):
        """Starts the polling loop to check for new log messages."""
        self.textbox.after(100, self.process_queue)

    def process_queue(self):
        """Process the log queue and update the GUI. Runs on the main thread."""
        try:
            while not self.log_queue.empty():
                record = self.log_queue.get_nowait()
                msg = self.format(record)
                
                #Determine the tag based on log level
                level_tag = record.levelname
                if level_tag not in ["INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"]:
                    level_tag = "INFO" #Default tag

                self.textbox.configure(state='normal')
                self.textbox.insert(ctk.END, msg + '\n', (level_tag,))
                self.textbox.configure(state='disabled')
                self.textbox.see(ctk.END) #Scroll to the bottom
        except queue.Empty:
            pass  #This can happen if the queue becomes empty between the check and get
        finally:
            #Reschedule the next check
            self.textbox.after(100, self.process_queue)
