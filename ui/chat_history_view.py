"""
UI component for displaying chat-style history messages.
"""

import re
import tkinter as tk
from typing import Dict, List

import customtkinter as ctk
from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer


class ChatHistoryView(ctk.CTkFrame):
    """A frame that contains a single CTkTextbox for displaying chat history."""

    def __init__(self, master, **kwargs):
        print("[LOG] ChatHistoryView: __init__ called")
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.history: List[Dict[str, str]] = []
        self.compact_mode = True  # Default to compact mode
        self.max_compact_lines = 10  # Maximum lines to show in compact mode

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
            command=self._copy_all_chat,
        )
        self.top_copy_button.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        # Compact mode toggle button
        self.compact_toggle_button = ctk.CTkButton(
            self.top_copy_frame,
            text="▼",
            width=25,
            height=25,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color="gray50",
            hover_color="gray30",
            command=self._toggle_compact_mode,
        )
        self.compact_toggle_button.grid(row=0, column=1, padx=5, pady=2, sticky="w")

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
            command=self._copy_all_chat,
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

        # System message styling (dimmed and compact)
        self.textbox.tag_config("system_dim", foreground="#808080", spacing1=1, spacing3=1)  # Gray and minimal spacing
        self.textbox.tag_config("processing_dim", foreground="#707070", spacing1=1, spacing3=1)  # Even more dimmed
        self.textbox.tag_config("thinking_dim", foreground="#606060", spacing1=1, spacing3=1)  # Very dimmed for thinking

        # Compact mode styling
        self.textbox.tag_config("compact", spacing1=1, spacing3=1)
        self.textbox.tag_config("compact_user", foreground="#00A0E0", spacing1=1, spacing3=1)
        self.textbox.tag_config("compact_agent", foreground="#FFB84D", spacing1=1, spacing3=1)
        self.textbox.tag_config("compact_system", foreground="#B666A3", spacing1=1, spacing3=1)

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

    def _toggle_compact_mode(self):
        """Toggle between compact and full view modes."""
        self.compact_mode = not self.compact_mode
        
        if self.compact_mode:
            self.compact_toggle_button.configure(text="▼")
            self._apply_compact_view()
        else:
            self.compact_toggle_button.configure(text="▲")
            self._apply_full_view()

    def _apply_compact_view(self):
        """Apply compact view showing only recent messages."""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        
        # Show only the last few messages
        recent_messages = self.history[-self.max_compact_lines:] if len(self.history) > self.max_compact_lines else self.history
        
        for msg in recent_messages:
            self._add_message_internal(msg["role"], msg["text"], compact=True)
        
        self.textbox.configure(state="disabled")

    def _apply_full_view(self):
        """Apply full view showing all messages."""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        
        for msg in self.history:
            self._add_message_internal(msg["role"], msg["text"], compact=False)
        
        self.textbox.configure(state="disabled")

    def add_message(self, role: str, text: str):
        """Adds a new message to the textbox and saves it to history with improved formatting."""
        self.history.append({"role": role, "text": text})

        # Add message to display
        self._add_message_internal(role, text, compact=self.compact_mode)

    def _add_message_internal(self, role: str, text: str, compact: bool = False):
        """Internal method to add a message with specified compact mode."""
        self.textbox.configure(state="normal")

        # Check if this is a system message that should be dimmed
        is_system_dim = self._is_system_message_dim(text)
        is_processing = text.startswith("Processing your request") or "Detected" in text or "Analyzing" in text
        is_thinking = "thinking" in text.lower() or "analyzing" in text.lower() or "processing" in text.lower()

        #Enhanced prefixes with emojis and better styling
        prefixes = {
            "user": ("👤 You", "user_prefix"),
            "agent": ("🤖 Atlas", "agent_prefix"),
            "assistant": ("🤖 Atlas", "agent_prefix"),  #Assistant is the same as agent
            "system": ("⚙️ System", "system_prefix"),
        }

        prefix_text, prefix_tag = prefixes.get(role, ("🤖 Atlas", "agent_prefix"))  #Default to Atlas instead of Unknown

        # Use dimmed styling for certain system messages
        if is_system_dim or is_processing or is_thinking:
            if is_thinking:
                prefix_tag = "thinking_dim"
                text_tag = "thinking_dim"
            elif is_processing:
                prefix_tag = "processing_dim"
                text_tag = "processing_dim"
            else:
                prefix_tag = "system_dim"
                text_tag = "system_dim"
        else:
            text_tag = role if role in ["user", "agent", "assistant", "system"] else "agent"

        # Apply compact styling if needed
        if compact:
            prefix_tag = f"compact_{prefix_tag.replace('_prefix', '')}"
            text_tag = f"compact_{text_tag}"

        #Add prefix with styling
        self.textbox.insert("end", f"{prefix_text}: ", (prefix_tag,))

        #Apply syntax highlighting and use appropriate text color
        self._apply_syntax_highlighting(text, text_tag)

        # Use shorter spacing for dimmed messages and compact mode
        if is_system_dim or is_processing or is_thinking or compact:
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
            "Processing your request",
            "🌐 Detected",
            "🌐 Active:",
            "🌐 Translation:",
            "Mode:",
            "🔧 Manual mode",
            "🔧 Automatic mode",
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
            processed_ranges.append((match.start(), match.end(), "code_block", match))

        #Find all inline code
        for match in re.finditer(inline_code_pattern, text):
            processed_ranges.append((match.start(), match.end(), "inline_code", match))

        #Sort by start position
        processed_ranges.sort(key=lambda x: x[0])

        #Process text in order
        last_end = 0
        for start, end, code_type, match in processed_ranges:
            #Process text before this code section (apply markdown formatting)
            before_text = text[last_end:start]
            if before_text:
                self._apply_markdown_formatting(before_text, default_tag)

            #Process the code section
            if code_type == "code_block":
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

            elif code_type == "inline_code":
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
            self.textbox.mark_set("insert", "1.0")
            self.textbox.see("insert")
        except tk.TclError:
            pass

    def clear(self):
        """Clear the chat history."""
        self.history.clear()
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

    def load_history(self, history: List[Dict[str, str]]):
        """Load chat history from a list of dictionaries."""
        self.history = history.copy()
        self._apply_full_view()
