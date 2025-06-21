"""
Context menu support for CustomTkinter widgets on macOS and other platforms.
Provides right-click copy/paste functionality and text formatting for chat input.
"""

import platform
import tkinter as tk
from typing import Optional

import customtkinter as ctk


class ContextMenu:
    """Provides context menu functionality for text widgets."""

    def __init__(self):
        self.current_widget: Optional[tk.Widget] = None
        self.menu: Optional[tk.Menu] = None

    def add_to_widget(self, widget):
        """Add context menu support to a widget."""
        if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
            #For CTk widgets, we need to access the underlying tkinter widget
            if hasattr(widget, "_textbox"):
                #CTkTextbox case
                inner_widget = widget._textbox
            elif hasattr(widget, "_entry"):
                #CTkEntry case
                inner_widget = widget._entry
            else:
                #Fallback
                inner_widget = widget

            #Bind right-click for all platforms
            inner_widget.bind("<Button-3>", lambda e: self._show_menu(e, widget))
            #For macOS, also bind Control+Click
            if platform.system() == "Darwin":
                inner_widget.bind("<Control-Button-1>", lambda e: self._show_menu(e, widget))

        elif isinstance(widget, (tk.Text, tk.Entry)):
            #Direct tkinter widgets
            widget.bind("<Button-3>", lambda e: self._show_menu(e, widget))
            if platform.system() == "Darwin":
                widget.bind("<Control-Button-1>", lambda e: self._show_menu(e, widget))

    def _show_menu(self, event, widget):
        """Show the context menu."""
        self.current_widget = widget

        #Create menu if it doesn't exist
        if self.menu is None:
            self.menu = tk.Menu(widget, tearoff=0)
            self.menu.add_command(label="Вирізати", command=self._cut)
            self.menu.add_command(label="Копіювати", command=self._copy)
            self.menu.add_command(label="Вставити", command=self._paste)
            self.menu.add_separator()
            self.menu.add_command(label="Виділити все", command=self._select_all)

        #Update menu state based on widget content and selection
        self._update_menu_state()

        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        except tk.TclError:
            pass
        finally:
            self.menu.grab_release()

    def _update_menu_state(self):
        """Update menu item states based on current widget."""
        if not self.current_widget or not self.menu:
            return

        try:
            #Check if widget has content
            has_content = False
            has_selection = False

            if isinstance(self.current_widget, ctk.CTkTextbox):
                content = self.current_widget.get("1.0", "end-1c")
                has_content = bool(content.strip())
                try:
                    sel_start = self.current_widget.index("sel.first")
                    sel_end = self.current_widget.index("sel.last")
                    has_selection = sel_start != sel_end
                except tk.TclError:
                    has_selection = False

            elif isinstance(self.current_widget, ctk.CTkEntry):
                content = self.current_widget.get()
                has_content = bool(content.strip())
                has_selection = bool(self.current_widget.selection_present())

            #Enable/disable menu items
            self.menu.entryconfig(0, state="normal" if has_selection else "disabled")  #Cut
            self.menu.entryconfig(1, state="normal" if has_selection else "disabled")  #Copy
            self.menu.entryconfig(2, state="normal")  #Paste (always enabled)
            self.menu.entryconfig(4, state="normal" if has_content else "disabled")  #Select All

        except (AttributeError, tk.TclError):
            #Fallback: enable all items
            for i in [0, 1, 2, 4]:
                self.menu.entryconfig(i, state="normal")

    def _cut(self):
        """Cut selected text."""
        try:
            if isinstance(self.current_widget, (ctk.CTkTextbox, ctk.CTkEntry)):
                #First copy, then delete selection
                self._copy()
                if isinstance(self.current_widget, ctk.CTkTextbox):
                    self.current_widget.delete("sel.first", "sel.last")
                elif isinstance(self.current_widget, ctk.CTkEntry):
                    self.current_widget.delete(self.current_widget.index("sel.first"),
                                             self.current_widget.index("sel.last"))
        except (AttributeError, tk.TclError):
            pass

    def _copy(self):
        """Copy selected text to clipboard."""
        try:
            if isinstance(self.current_widget, ctk.CTkTextbox):
                selected_text = self.current_widget.get("sel.first", "sel.last")
                self.current_widget.clipboard_clear()
                self.current_widget.clipboard_append(selected_text)
            elif isinstance(self.current_widget, ctk.CTkEntry):
                selected_text = self.current_widget.selection_get()
                self.current_widget.clipboard_clear()
                self.current_widget.clipboard_append(selected_text)
        except (AttributeError, tk.TclError):
            pass

    def _paste(self):
        """Paste from clipboard."""
        try:
            clipboard_text = self.current_widget.clipboard_get()
            if isinstance(self.current_widget, ctk.CTkTextbox):
                #Insert at current cursor position
                self.current_widget.insert("insert", clipboard_text)
            elif isinstance(self.current_widget, ctk.CTkEntry):
                #Replace selection or insert at cursor
                if self.current_widget.selection_present():
                    self.current_widget.delete("sel.first", "sel.last")
                self.current_widget.insert("insert", clipboard_text)
        except (AttributeError, tk.TclError):
            pass

    def _select_all(self):
        """Select all text in widget."""
        try:
            if isinstance(self.current_widget, ctk.CTkTextbox):
                self.current_widget.tag_add("sel", "1.0", "end")
                self.current_widget.mark_set("insert", "1.0")
                self.current_widget.see("insert")
            elif isinstance(self.current_widget, ctk.CTkEntry):
                self.current_widget.select_range(0, "end")
                self.current_widget.icursor("end")
        except (AttributeError, tk.TclError):
            pass


#Global instance for easy access
context_menu = ContextMenu()


def enable_context_menu(widget):
    """Enable context menu for a widget."""
    context_menu.add_to_widget(widget)


def setup_context_menus_for_container(container):
    """Recursively add context menus to all text widgets in a container."""
    def _recursive_setup(widget):
        #Add context menu to text widgets
        if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
            enable_context_menu(widget)

        #Recursively process children
        try:
            for child in widget.winfo_children():
                _recursive_setup(child)
        except (AttributeError, tk.TclError):
            pass

    _recursive_setup(container)


class TextFormattingContextMenu:
    """Provides a context menu with text formatting options for chat input."""

    def __init__(self, chat_context_manager):
        self.current_widget = None
        self.menu = None
        self.chat_context_manager = chat_context_manager

    def add_to_widget(self, widget):
        """Add formatting context menu to a widget."""
        if isinstance(widget, (ctk.CTkTextbox)):
            #For CTk widgets, we need to access the underlying tkinter widget
            if hasattr(widget, "_textbox"):
                #CTkTextbox case
                inner_widget = widget._textbox
            else:
                #Fallback
                inner_widget = widget

            #Bind right-click for all platforms
            inner_widget.bind("<Button-3>", lambda e: self._show_menu(e, widget))
            #For macOS, also bind Control+Click
            if platform.system() == "Darwin":
                inner_widget.bind("<Control-Button-1>", lambda e: self._show_menu(e, widget))

    def _show_menu(self, event, widget):
        """Show the formatting context menu."""
        self.current_widget = widget

        #Create menu if it doesn't exist
        if self.menu is None:
            self.menu = tk.Menu(widget, tearoff=0)
            #Standard edit actions
            self.menu.add_command(label="Вирізати", command=self._cut)
            self.menu.add_command(label="Копіювати", command=self._copy)
            self.menu.add_command(label="Вставити", command=self._paste)
            self.menu.add_separator()

            #Text formatting submenu
            format_menu = tk.Menu(self.menu, tearoff=0)
            format_menu.add_command(label="Жирний", command=self._format_bold)
            format_menu.add_command(label="Курсив", command=self._format_italic)
            format_menu.add_command(label="Підкреслений", command=self._format_underline)
            format_menu.add_separator()
            format_menu.add_command(label="Код", command=self._format_code)
            format_menu.add_command(label="Блок коду", command=self._format_code_block)
            format_menu.add_separator()
            format_menu.add_command(label="Цитата", command=self._format_quote)
            format_menu.add_command(label="Посилання", command=self._format_link)

            self.menu.add_cascade(label="Форматування", menu=format_menu)
            self.menu.add_command(label="Виділити все", command=self._select_all)

        #Update menu state based on widget content and selection
        self._update_menu_state()

        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        except tk.TclError:
            pass
        finally:
            self.menu.grab_release()

    def _update_menu_state(self):
        """Update menu item states based on current widget."""
        if not self.current_widget or not self.menu:
            return

        try:
            #Check if widget has content
            has_content = False
            has_selection = False

            if isinstance(self.current_widget, ctk.CTkTextbox):
                content = self.current_widget.get("1.0", "end-1c")
                has_content = bool(content.strip())
                try:
                    sel_start = self.current_widget._textbox.index("sel.first")
                    sel_end = self.current_widget._textbox.index("sel.last")
                    has_selection = sel_start != sel_end
                except tk.TclError:
                    has_selection = False

            #Enable/disable menu items
            self.menu.entryconfig(0, state="normal" if has_selection else "disabled")  #Cut
            self.menu.entryconfig(1, state="normal" if has_selection else "disabled")  #Copy
            self.menu.entryconfig(2, state="normal")  #Paste (always enabled)
            self.menu.entryconfig(4, state="normal" if has_selection else "disabled")  #Format submenu
            self.menu.entryconfig(5, state="normal" if has_content else "disabled")  #Select All

        except (AttributeError, tk.TclError):
            #Fallback: enable all items
            for i in [0, 1, 2, 4, 5]:
                self.menu.entryconfig(i, state="normal")

    def _cut(self):
        """Cut selected text."""
        try:
            if isinstance(self.current_widget, ctk.CTkTextbox):
                #First copy, then delete selection
                self._copy()
                self.current_widget.delete("sel.first", "sel.last")
        except (AttributeError, tk.TclError):
            pass

    def _copy(self):
        """Copy selected text to clipboard."""
        try:
            if isinstance(self.current_widget, ctk.CTkTextbox):
                selected_text = self.current_widget.get("sel.first", "sel.last")
                self.current_widget._textbox.clipboard_clear()
                self.current_widget._textbox.clipboard_append(selected_text)
        except (AttributeError, tk.TclError):
            pass

    def _paste(self):
        """Paste from clipboard."""
        try:
            clipboard_text = self.current_widget._textbox.clipboard_get()
            if isinstance(self.current_widget, ctk.CTkTextbox):
                #Insert at current cursor position
                self.current_widget.insert("insert", clipboard_text)
        except (AttributeError, tk.TclError):
            pass

    def _select_all(self):
        """Select all text in widget."""
        try:
            if isinstance(self.current_widget, ctk.CTkTextbox):
                self.current_widget.tag_add("sel", "1.0", "end")
                self.current_widget.mark_set("insert", "1.0")
                self.current_widget.see("insert")
        except (AttributeError, tk.TclError):
            pass

    def _format_bold(self):
        """Apply bold formatting to selected text."""
        self._apply_formatting(self.chat_context_manager.format_bold)

    def _format_italic(self):
        """Apply italic formatting to selected text."""
        self._apply_formatting(self.chat_context_manager.format_italic)

    def _format_underline(self):
        """Apply underline formatting to selected text."""
        self._apply_formatting(self.chat_context_manager.format_underline)

    def _format_code(self):
        """Apply code formatting to selected text."""
        self._apply_formatting(self.chat_context_manager.format_code)

    def _format_code_block(self):
        """Apply code block formatting to selected text."""
        self._apply_formatting(lambda text: self.chat_context_manager.format_code_block(text))

    def _format_quote(self):
        """Apply quote formatting to selected text."""
        self._apply_formatting(self.chat_context_manager.format_quote)

    def _format_link(self):
        """Apply link formatting to selected text."""
        self._apply_formatting(lambda text: self.chat_context_manager.format_link(text, "URL"))

    def _apply_formatting(self, format_func):
        """Apply formatting function to selected text."""
        try:
            if isinstance(self.current_widget, ctk.CTkTextbox):
                try:
                    # Get selected text
                    selected_text = self.current_widget.get("sel.first", "sel.last")
                    if selected_text:
                        # Apply formatting function
                        formatted_text = format_func(selected_text)

                        # Replace selected text with formatted text
                        self.current_widget.delete("sel.first", "sel.last")
                        self.current_widget.insert("insert", formatted_text)
                except tk.TclError:
                    # No selection, do nothing
                    pass
        except (AttributeError, tk.TclError):
            pass


# Formatting context menu global instance
formatting_context_menu = None

def enable_formatting_context_menu(widget, chat_context_manager):
    """Enable formatting context menu for a widget."""
    global formatting_context_menu
    if formatting_context_menu is None and chat_context_manager is not None:
        formatting_context_menu = TextFormattingContextMenu(chat_context_manager)

    if formatting_context_menu is not None:
        formatting_context_menu.add_to_widget(widget)


def setup_formatting_context_menus_for_container(container, chat_context_manager):
    """Recursively add formatting context menus to all text widgets in a container."""
    def _recursive_setup(widget):
        #Add formatting context menu to text widgets
        if isinstance(widget, ctk.CTkTextbox):
            enable_formatting_context_menu(widget, chat_context_manager)

        #Recursively process children
        try:
            for child in widget.winfo_children():
                _recursive_setup(child)
        except (AttributeError, tk.TclError):
            pass

    _recursive_setup(container)
