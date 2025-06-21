"""
UI component for displaying chat-style history messages.
"""

import customtkinter as ctk
from typing import Dict, List
import re
import tkinter as tk

from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer


class ChatHistoryView(ctk.CTkFrame):
    """A frame that contains a single CTkTextbox for displaying chat history."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.history: List[Dict[str, str]] = []

        # Add top copy button frame
        self.top_copy_frame = ctk.CTkFrame(self, height=30)
        self.top_copy_frame.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        self.top_copy_frame.grid_columnconfigure(1, weight=1)
        
        # Top copy button (small and subtle)
        self.top_copy_button = ctk.CTkButton(
            self.top_copy_frame,
            text="📋",
            width=25,
            height=25,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color="gray50",
            hover_color="gray30",
            command=self._copy_all_chat
        )
        self.top_copy_button.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.textbox = ctk.CTkTextbox(self, wrap="word", state="disabled", font=("Helvetica", 13))
        self.textbox.grid(row=1, column=0, sticky="nsew")
        
        # Add bottom copy button frame
        self.bottom_copy_frame = ctk.CTkFrame(self, height=30)
        self.bottom_copy_frame.grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        self.bottom_copy_frame.grid_columnconfigure(0, weight=1)
        
        # Bottom copy button (small and subtle)
        self.bottom_copy_button = ctk.CTkButton(
            self.bottom_copy_frame,
            text="📋",
            width=25,
            height=25,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color="gray50",
            hover_color="gray30",
            command=self._copy_all_chat
        )
        self.bottom_copy_button.grid(row=0, column=1, padx=5, pady=2, sticky="e")

        # Add context menu support
        self._setup_context_menu()

        #--- Tag Configurations ---
        #Note: CustomTkinter doesn't allow font in tag_config, so we use only colors
        self.textbox.tag_config("user_prefix", foreground="#00A0E0")
        self.textbox.tag_config("agent_prefix", foreground="#FF9500")  # Orange for agent
        self.textbox.tag_config("system_prefix", foreground="#9E4784")  # Purple for system
        
        self.textbox.tag_config("user", foreground="#00A0E0")
        self.textbox.tag_config("agent", foreground="#FFB84D")  # Lighter orange for agent text
        self.textbox.tag_config("system", foreground="#B666A3")  # Lighter purple for system text
        
        # System message styling (dimmed)
        self.textbox.tag_config("system_dim", foreground="#808080", spacing1=2, spacing3=2)  # Gray and less spacing
        self.textbox.tag_config("processing_dim", foreground="#707070", spacing1=1, spacing3=1)  # Even more dimmed
        
        self.textbox.tag_config("user", foreground="#00A0E0")
        self.textbox.tag_config("agent", foreground="#FFB84D")  # Lighter orange for agent text
        self.textbox.tag_config("system", foreground="#B666A3")  # Lighter purple for system text

                #self.textbox.tag_config("title", font=("Helvetica", 14, "bold")) # Font attribute is forbidden by customtkinter
        self.textbox.tag_config("plan_step", lmargin1=20, lmargin2=20)
        self.textbox.tag_config("step_start", foreground="#A0A0A0", lmargin1=20, lmargin2=20)
        self.textbox.tag_config("step_end", foreground="#A0A0A0", lmargin1=20, lmargin2=20)
        self.textbox.tag_config("error", foreground="#E00000")

        #Improved code block styling
        self.textbox.tag_config("code_block_bg", 
                              background="#1E1E1E", 
                              foreground="#D4D4D4",
                              lmargin1=20, 
                              lmargin2=20, 
                              rmargin=20,
                              spacing1=5,
                              spacing3=5)
        
        #Inline code styling  
        self.textbox.tag_config("inline_code",
                              background="#2D2D2D",
                              foreground="#E1E1E1")
        
        #Improved Pygments syntax highlighting tags with VS Code Dark theme colors
        self.textbox.tag_config("Token.Keyword", foreground="#569CD6")          # Blue
        self.textbox.tag_config("Token.Name.Function", foreground="#DCDCAA")    # Yellow
        self.textbox.tag_config("Token.String", foreground="#CE9178")           # Orange
        self.textbox.tag_config("Token.Comment", foreground="#6A9955")          # Green
        self.textbox.tag_config("Token.Operator", foreground="#D4D4D4")         # Light gray
        self.textbox.tag_config("Token.Number", foreground="#B5CEA8")           # Light green
        self.textbox.tag_config("Token.Literal.String.Doc", foreground="#6A9955") # Green
        self.textbox.tag_config("Token.Name.Class", foreground="#4EC9B0")       # Cyan
        self.textbox.tag_config("Token.Name.Builtin", foreground="#4EC9B0")     # Cyan
        self.textbox.tag_config("Token.Name.Variable", foreground="#9CDCFE")    # Light blue
        #Enhanced markdown styling
        self.textbox.tag_config("markdown_bold", foreground="#FFFFFF")
        self.textbox.tag_config("markdown_header", foreground="#FFD700")  # Gold for headers
        self.textbox.tag_config("markdown_bullet", foreground="#87CEEB")  # Sky blue for bullets
        self.textbox.tag_config("markdown_emoji", foreground="#FFA500")   # Orange for emojis

    def add_message(self, role: str, text: str):
        """Adds a new message to the textbox and saves it to history with improved formatting."""
        self.history.append({"role": role, "text": text})
        
        self.textbox.configure(state="normal")
        
        # Check if this is a system message that should be dimmed
        is_system_dim = self._is_system_message_dim(text)
        is_processing = text.startswith("Processing your request") or "Detected" in text or "Analyzing" in text
        
        #Enhanced prefixes with emojis and better styling
        prefixes = {
            "user": ("👤 You", "user_prefix"),
            "agent": ("🤖 Atlas", "agent_prefix"),
            "assistant": ("🤖 Atlas", "agent_prefix"),  #Assistant is the same as agent
            "system": ("⚙️ System", "system_prefix")
        }
        
        prefix_text, prefix_tag = prefixes.get(role, ("🤖 Atlas", "agent_prefix"))  #Default to Atlas instead of Unknown
        
        # Use dimmed styling for certain system messages
        if is_system_dim or is_processing:
            if is_processing:
                prefix_tag = "processing_dim"
                text_tag = "processing_dim"
            else:
                prefix_tag = "system_dim"
                text_tag = "system_dim"
        else:
            text_tag = role if role in ["user", "agent", "assistant", "system"] else "agent"
        
        #Add prefix with styling
        self.textbox.insert("end", f"{prefix_text}: ", (prefix_tag,))

        #Apply syntax highlighting and use appropriate text color
        self._apply_syntax_highlighting(text, text_tag)
        
        # Use shorter spacing for dimmed messages
        if is_system_dim or is_processing:
            self.textbox.insert("end", "\n")
        else:
            self.textbox.insert("end", "\n\n")

        self.textbox.configure(state="disabled")
        self.textbox.yview_moveto(1.0)
    
    def _is_system_message_dim(self, text: str) -> bool:
        """Check if a message should be displayed as dimmed."""
        dim_patterns = [
            "Detected Ukrainian",
            "Processing in English", 
            "translate response back",
            "Analyzing as",
            "confidence:",
            "Processing your request"
        ]
        return any(pattern in text for pattern in dim_patterns)

    def get_history(self) -> List[Dict[str, str]]:
        """Returns the entire chat history as a list of dictionaries."""
        return self.history

    def _apply_markdown_formatting(self, text: str, default_tag: str):
        """Placeholder for markdown formatting. Inserts text with the default tag."""
        self.textbox.insert("end", text, (default_tag,))

    def _apply_syntax_highlighting(self, text: str, default_tag: str):
        """Enhanced syntax highlighting for code blocks, inline code, and markdown formatting."""
        #Process code blocks first, then inline code, then markdown
        code_block_pattern = r"```(python|bash|sh|javascript|js|html|css|json|yaml|sql)?\n(.*?)\n```"
        inline_code_pattern = r"`([^`\n]+)`"
        
        #Process text in chunks, handling code first to avoid conflicts with markdown
        processed_ranges = []
        
        #Find all code blocks
        for match in re.finditer(code_block_pattern, text, re.DOTALL):
            start, end = match.span()
            processed_ranges.append((start, end, 'code_block', match))
        
        #Find all inline code
        for match in re.finditer(inline_code_pattern, text):
            start, end = match.span()
            #Check if this overlaps with any code block
            overlaps = any(s <= start < e or s < end <= e for s, e, _, _ in processed_ranges)
            if not overlaps:
                processed_ranges.append((start, end, 'inline_code', match))
        
        #Sort by start position
        processed_ranges.sort(key=lambda x: x[0])
        
        last_end = 0
        for start, end, code_type, match in processed_ranges:
            #Process text before this code section (apply markdown formatting)
            before_text = text[last_end:start]
            if before_text:
                self._apply_markdown_formatting(before_text, default_tag)
            
            #Process the code section
            if code_type == 'code_block':
                lang = match.group(1) or "text"
                code = match.group(2)
                
                #Add opening ```
                self.textbox.insert("end", f"```{lang}\n", ("code_block_bg",))
                
                try:
                    lexer = get_lexer_by_name(lang, stripall=True)
                except Exception:
                    try:
                        lexer = guess_lexer(code)
                    except Exception:
                        #Fallback to plain text
                        self.textbox.insert("end", code, ("code_block_bg",))
                        self.textbox.insert("end", "\n```", ("code_block_bg",))
                        last_end = end
                        continue

                #Highlight the code within the block
                for token, content in lex(code, lexer):
                    self.textbox.insert("end", content, (str(token), "code_block_bg"))
                
                #Add closing ```
                self.textbox.insert("end", "\n```", ("code_block_bg",))
                
            elif code_type == 'inline_code':
                inline_code = match.group(1)
                self.textbox.insert("end", f"`{inline_code}`", ("inline_code",))
            
            last_end = end

        #Process any remaining text after the last code
        remaining_text = text[last_end:]
        if remaining_text:
            self._apply_markdown_formatting(remaining_text, default_tag)

    def _setup_context_menu(self):
        """Setup context menu for the textbox."""
        self.context_menu = tk.Menu(self.textbox, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self._copy_selection)
        self.context_menu.add_command(label="Copy All", command=self._copy_all_chat)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self._select_all)
        
        # Bind right-click to show context menu
        self.textbox.bind("<Button-3>", self._show_context_menu)
        # For macOS, also bind Control+Click
        import platform
        if platform.system() == "Darwin":
            self.textbox.bind("<Control-Button-1>", self._show_context_menu)
    
    def _show_context_menu(self, event):
        """Show the context menu."""
        try:
            # Check if there's a selection
            has_selection = False
            try:
                self.textbox.index("sel.first")
                has_selection = True
            except tk.TclError:
                has_selection = False
            
            # Enable/disable menu items
            self.context_menu.entryconfig(0, state="normal" if has_selection else "disabled")  # Copy
            self.context_menu.entryconfig(1, state="normal")  # Copy All
            self.context_menu.entryconfig(3, state="normal")  # Select All
            
            self.context_menu.tk_popup(event.x_root, event.y_root)
        except tk.TclError:
            pass
        finally:
            self.context_menu.grab_release()
    
    def _copy_selection(self):
        """Copy selected text to clipboard."""
        try:
            selected_text = self.textbox.get("sel.first", "sel.last")
            self.textbox.clipboard_clear()
            self.textbox.clipboard_append(selected_text)
        except tk.TclError:
            pass
    
    def _copy_all_chat(self):
        """Copy all chat content to clipboard."""
        try:
            all_text = self.textbox.get("1.0", "end-1c")
            self.textbox.clipboard_clear()
            self.textbox.clipboard_append(all_text)
        except tk.TclError:
            pass
    
    def _select_all(self):
        """Select all text in the textbox."""
        try:
            self.textbox.tag_add("sel", "1.0", "end")
        except tk.TclError:
            pass

    def clear(self):
        """Removes all messages from the view and history."""
        self.history.clear()
        self.textbox.configure(state="normal")
        self.textbox.delete(1.0, "end")
        self.textbox.configure(state="disabled")

    def load_history(self, history: List[Dict[str, str]]):
        """Clears the current view and loads a new history."""
        self.clear()
        self.textbox.configure(state="normal")
        for msg in history:
            self.history.append(msg)
            prefix = "You" if msg["role"] == "user" else "Agent"
            self.textbox.insert("end", f"{prefix}: ", (f"{msg['role']}_prefix",))
            self._apply_syntax_highlighting(msg["text"], msg["role"])
            self.textbox.insert("end", "\n\n")
        self.textbox.configure(state="disabled")
        self.textbox.yview_moveto(1.0)
