"""
UI component for displaying chat-style history messages.
"""

import customtkinter as ctk
from typing import Dict, List
import re
from typing import List, Dict, Any, Optional

from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.token import Token


class ChatHistoryView(ctk.CTkFrame):
    """A frame that contains a single CTkTextbox for displaying chat history."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.history: List[Dict[str, str]] = []

        self.textbox = ctk.CTkTextbox(self, wrap="word", state="disabled", font=("Helvetica", 13))
        self.textbox.grid(row=0, column=0, sticky="nsew")

        # --- Tag Configurations ---
        # Note: CustomTkinter doesn't allow font in tag_config, so we use only colors
        self.textbox.tag_config("user_prefix", foreground="#00A0E0")
        self.textbox.tag_config("agent_prefix", foreground="#FF9500")  # Orange for agent
        self.textbox.tag_config("system_prefix", foreground="#9E4784")  # Purple for system
        
        self.textbox.tag_config("user", foreground="#00A0E0")
        self.textbox.tag_config("agent", foreground="#FFB84D")  # Lighter orange for agent text
        self.textbox.tag_config("system", foreground="#B666A3")  # Lighter purple for system text

                # self.textbox.tag_config("title", font=("Helvetica", 14, "bold")) # Font attribute is forbidden by customtkinter
        self.textbox.tag_config("plan_step", lmargin1=20, lmargin2=20)
        self.textbox.tag_config("step_start", foreground="#A0A0A0", lmargin1=20, lmargin2=20)
        self.textbox.tag_config("step_end", foreground="#A0A0A0", lmargin1=20, lmargin2=20)
        self.textbox.tag_config("error", foreground="#E00000")

        # Improved code block styling
        self.textbox.tag_config("code_block_bg", 
                              background="#1E1E1E", 
                              foreground="#D4D4D4",
                              lmargin1=20, 
                              lmargin2=20, 
                              rmargin=20,
                              spacing1=5,
                              spacing3=5)
        
        # Inline code styling  
        self.textbox.tag_config("inline_code",
                              background="#2D2D2D",
                              foreground="#E1E1E1")
        
        # Improved Pygments syntax highlighting tags with VS Code Dark theme colors
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
        # Enhanced markdown styling
        self.textbox.tag_config("markdown_bold", foreground="#FFFFFF")
        self.textbox.tag_config("markdown_header", foreground="#FFD700")  # Gold for headers
        self.textbox.tag_config("markdown_bullet", foreground="#87CEEB")  # Sky blue for bullets
        self.textbox.tag_config("markdown_emoji", foreground="#FFA500")   # Orange for emojis

    def add_message(self, role: str, text: str):
        """Adds a new message to the textbox and saves it to history with improved formatting."""
        self.history.append({"role": role, "text": text})
        
        self.textbox.configure(state="normal")
        
        # Enhanced prefixes with emojis and better styling
        prefixes = {
            "user": ("👤 You", "user_prefix"),
            "agent": ("🤖 Atlas", "agent_prefix"),
            "assistant": ("🤖 Atlas", "agent_prefix"),  # Assistant is the same as agent
            "system": ("⚙️ System", "system_prefix")
        }
        
        prefix_text, prefix_tag = prefixes.get(role, ("🤖 Atlas", "agent_prefix"))  # Default to Atlas instead of Unknown
        
        # Add prefix with styling
        self.textbox.insert("end", f"{prefix_text}: ", (prefix_tag,))

        # Apply syntax highlighting and use appropriate text color
        text_tag = role if role in ["user", "agent", "assistant", "system"] else "agent"  # Map assistant to agent colors
        self._apply_syntax_highlighting(text, text_tag)
        self.textbox.insert("end", "\n\n")

        self.textbox.configure(state="disabled")
        self.textbox.yview_moveto(1.0)

    def get_history(self) -> List[Dict[str, str]]:
        """Returns the entire chat history as a list of dictionaries."""
        return self.history

    def _apply_syntax_highlighting(self, text: str, default_tag: str):
        """Enhanced syntax highlighting for code blocks, inline code, and markdown formatting."""
        # Process code blocks first, then inline code, then markdown
        code_block_pattern = r"```(python|bash|sh|javascript|js|html|css|json|yaml|sql)?\n(.*?)\n```"
        inline_code_pattern = r"`([^`\n]+)`"
        
        # Process text in chunks, handling code first to avoid conflicts with markdown
        processed_ranges = []
        
        # Find all code blocks
        for match in re.finditer(code_block_pattern, text, re.DOTALL):
            start, end = match.span()
            processed_ranges.append((start, end, 'code_block', match))
        
        # Find all inline code
        for match in re.finditer(inline_code_pattern, text):
            start, end = match.span()
            # Check if this overlaps with any code block
            overlaps = any(s <= start < e or s < end <= e for s, e, _, _ in processed_ranges)
            if not overlaps:
                processed_ranges.append((start, end, 'inline_code', match))
        
        # Sort by start position
        processed_ranges.sort(key=lambda x: x[0])
        
        last_end = 0
        for start, end, code_type, match in processed_ranges:
            # Process text before this code section (apply markdown formatting)
            before_text = text[last_end:start]
            if before_text:
                self._apply_markdown_formatting(before_text, default_tag)
            
            # Process the code section
            if code_type == 'code_block':
                lang = match.group(1) or "text"
                code = match.group(2)
                
                # Add opening ```
                self.textbox.insert("end", f"```{lang}\n", ("code_block_bg",))
                
                try:
                    lexer = get_lexer_by_name(lang, stripall=True)
                except Exception:
                    try:
                        lexer = guess_lexer(code)
                    except Exception:
                        # Fallback to plain text
                        self.textbox.insert("end", code, ("code_block_bg",))
                        self.textbox.insert("end", "\n```", ("code_block_bg",))
                        last_end = end
                        continue

                # Highlight the code within the block
                for token, content in lex(code, lexer):
                    self.textbox.insert("end", content, (str(token), "code_block_bg"))
                
                # Add closing ```
                self.textbox.insert("end", "\n```", ("code_block_bg",))
                
            elif code_type == 'inline_code':
                inline_code = match.group(1)
                self.textbox.insert("end", f"`{inline_code}`", ("inline_code",))
            
            last_end = end

        # Process any remaining text after the last code
        remaining_text = text[last_end:]
        if remaining_text:
            self._apply_markdown_formatting(remaining_text, default_tag)

    def _apply_markdown_formatting(self, text: str, default_tag: str):
        """Apply markdown-like formatting to text."""
        # Patterns for markdown formatting
        bold_pattern = r'\*\*(.*?)\*\*'
        header_pattern = r'^(#{1,6})\s+(.+)$'
        bullet_pattern = r'^(\s*)[•·*-]\s+(.+)$'
        emoji_pattern = r'([🔧🤖💬❓🎯⚙️📊🌐👤🔄❌✅📋🖥️🖱️📷🔍⚡🛠️📱💡🚀🔒🔓📝📊])'
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if i > 0:
                self.textbox.insert("end", "\n", (default_tag,))
            
            # Check for headers first
            header_match = re.match(header_pattern, line)
            if header_match:
                hashes, header_text = header_match.groups()
                self.textbox.insert("end", hashes + " ", (default_tag,))
                self._process_inline_formatting(header_text, "markdown_header")
                continue
            
            # Check for bullets
            bullet_match = re.match(bullet_pattern, line)
            if bullet_match:
                indent, bullet_text = bullet_match.groups()
                self.textbox.insert("end", indent + "• ", ("markdown_bullet",))
                self._process_inline_formatting(bullet_text, default_tag)
                continue
            
            # Process regular line with inline formatting
            self._process_inline_formatting(line, default_tag)

    def _process_inline_formatting(self, text: str, default_tag: str):
        """Process inline formatting like bold text and emojis."""
        bold_pattern = r'\*\*(.*?)\*\*'
        emoji_pattern = r'([🔧🤖💬❓🎯⚙️📊🌐👤🔄❌✅📋🖥️🖱️📷🔍⚡🛠️📱💡🚀🔒🔓📝📊🔨⭐🎉🎈🏆🌟💎🎁🍀💯])'
        
        # Combine patterns to process in order
        combined_pattern = f"({bold_pattern})|({emoji_pattern})"
        
        last_end = 0
        for match in re.finditer(combined_pattern, text):
            start, end = match.span()
            
            # Add text before the formatting
            before_text = text[last_end:start]
            if before_text:
                self.textbox.insert("end", before_text, (default_tag,))
            
            if match.group(1):  # Bold text
                bold_text = match.group(2)
                self.textbox.insert("end", bold_text, ("markdown_bold",))
            elif match.group(3):  # Emoji
                emoji = match.group(3)
                self.textbox.insert("end", emoji, ("markdown_emoji",))
            
            last_end = end
        
        # Add any remaining text
        remaining_text = text[last_end:]
        if remaining_text:
            self.textbox.insert("end", remaining_text, (default_tag,))

    def add_structured_message(self, message_data: Dict[str, Any]):
        """Adds a structured message from the agent to the view, with formatting."""
        msg_type = message_data.get("type")
        data = message_data.get("data")

        if not msg_type or data is None:
            return

        self.textbox.configure(state="normal")
        if msg_type == "plan":
            self.textbox.insert("end", "Master Agent Plan:\n", ("title",))
            for i, step in enumerate(data):
                self.textbox.insert("end", f"{i+1}. {step.get('description', 'No description')}\n", ("plan_step",))
        elif msg_type == "step_start":
            self.textbox.insert("end", f"\nExecuting: {data.get('description')}...\n", ("step_start",))
        elif msg_type == "step_end":
            result = str(data.get('result', 'No result'))
            self.textbox.insert("end", f"Result: {result}\n", ("step_end",))
        elif msg_type == "error":
            self.textbox.insert("end", f"Error: {data.get('message')}\n", ("error",))
        
        self.textbox.insert("end", "---\n")
        self.textbox.configure(state="disabled")
        self.textbox.yview_moveto(1.0)

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
