#!/usr/bin/env python3
"""
Test script for UI improvements including:
- Context menu functionality
- Compact chat view
- Keyboard shortcuts
- Text formatting
"""

import tkinter as tk
import customtkinter as ctk
from ui.context_menu import enable_context_menu, setup_context_menus_for_container
from ui.chat_history_view import ChatHistoryView
from agents.chat_context_manager import ChatContextManager

def test_context_menu():
    """Test context menu functionality."""
    print("Testing context menu functionality...")
    
    root = ctk.CTk()
    root.title("Context Menu Test")
    root.geometry("400x300")
    
    # Create text widgets
    textbox = ctk.CTkTextbox(root, height=100)
    textbox.pack(pady=10, padx=10, fill="x")
    textbox.insert("1.0", "Test text for context menu. Try right-clicking or using Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A")
    
    entry = ctk.CTkEntry(root)
    entry.pack(pady=10, padx=10, fill="x")
    entry.insert(0, "Test entry for context menu")
    
    # Enable context menus
    enable_context_menu(textbox)
    enable_context_menu(entry)
    
    # Add some test content
    test_content = """
    This is a test of the context menu functionality.
    
    Features to test:
    - Right-click context menu
    - Ctrl+C (Copy)
    - Ctrl+V (Paste) 
    - Ctrl+X (Cut)
    - Ctrl+A (Select All)
    - Ctrl+Z (Undo)
    
    Try selecting text and using the shortcuts!
    """
    
    textbox.insert("end", test_content)
    
    print("Context menu test window opened. Test the functionality and close when done.")
    root.mainloop()

def test_compact_chat():
    """Test compact chat view functionality."""
    print("Testing compact chat view...")
    
    root = ctk.CTk()
    root.title("Compact Chat Test")
    root.geometry("600x500")
    
    # Create chat view
    chat_view = ChatHistoryView(root)
    chat_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add test messages
    test_messages = [
        ("user", "Hello! This is a test of the compact chat view."),
        ("system", "🌐 Detected English. Processing in English."),
        ("agent", "Hello! I'm testing the compact chat functionality."),
        ("system", "Mode: 🤖 Auto Detection"),
        ("user", "Can you show me how the compact mode works?"),
        ("agent", "Sure! The compact mode shows fewer lines and uses shorter spacing for system messages."),
        ("system", "🔧 Automatic mode detection enabled"),
        ("user", "What about the thinking process messages?"),
        ("agent", "Thinking process messages are displayed in a very dimmed gray color with minimal spacing to show the AI's internal processing."),
        ("system", "🌐 Translation: Ready"),
        ("user", "This is great! The compact mode makes it much easier to follow the conversation."),
        ("agent", "Exactly! The compact mode helps focus on the main conversation while still showing important system information in a subtle way."),
        ("system", "Processing your request..."),
        ("user", "Can I toggle between compact and full view?"),
        ("agent", "Yes! Click the ▼ button in the top-left corner to toggle between compact and full view modes."),
    ]
    
    # Add messages with delays to simulate real conversation
    import threading
    import time
    
    def add_messages():
        for role, text in test_messages:
            chat_view.add_message(role, text)
            time.sleep(0.5)  # Small delay between messages
    
    threading.Thread(target=add_messages, daemon=True).start()
    
    print("Compact chat test window opened. Watch the messages appear and test the compact toggle.")
    root.mainloop()

def test_keyboard_shortcuts():
    """Test keyboard shortcuts in text widgets."""
    print("Testing keyboard shortcuts...")
    
    root = ctk.CTk()
    root.title("Keyboard Shortcuts Test")
    root.geometry("500x400")
    
    # Create a frame for instructions
    instructions = ctk.CTkLabel(root, text="""
    Keyboard Shortcuts Test
    
    Try these shortcuts in the text area below:
    - Ctrl+C: Copy selected text
    - Ctrl+V: Paste from clipboard
    - Ctrl+X: Cut selected text
    - Ctrl+A: Select all text
    - Ctrl+Z: Undo (if supported)
    
    Also try right-clicking for the context menu.
    """, justify="left")
    instructions.pack(pady=10, padx=10)
    
    # Create text widget
    textbox = ctk.CTkTextbox(root, height=200)
    textbox.pack(pady=10, padx=10, fill="both", expand=True)
    
    # Add some test content
    test_content = """This is test content for keyboard shortcuts.

Try selecting some text and using:
- Ctrl+C to copy
- Ctrl+X to cut
- Ctrl+V to paste
- Ctrl+A to select all

You can also right-click for a context menu with the same options.
"""
    
    textbox.insert("1.0", test_content)
    
    # Enable context menu
    enable_context_menu(textbox)
    
    print("Keyboard shortcuts test window opened. Test the shortcuts and close when done.")
    root.mainloop()

def main():
    """Run all UI improvement tests."""
    print("UI Improvements Test Suite")
    print("=" * 40)
    
    while True:
        print("\nChoose a test to run:")
        print("1. Context Menu Test")
        print("2. Compact Chat Test")
        print("3. Keyboard Shortcuts Test")
        print("4. Run All Tests")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            test_context_menu()
        elif choice == "2":
            test_compact_chat()
        elif choice == "3":
            test_keyboard_shortcuts()
        elif choice == "4":
            print("Running all tests...")
            test_context_menu()
            test_compact_chat()
            test_keyboard_shortcuts()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main() 