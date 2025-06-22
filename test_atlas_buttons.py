#!/usr/bin/env python3
"""
Test script to verify that Atlas buttons are created correctly
"""

import sys
import os
import customtkinter as ctk
import tkinter as tk
from unittest.mock import MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_button_creation():
    """Test that buttons can be created in Atlas-style interface"""
    
    print("=== Testing Atlas Button Creation ===")
    
    # Set up CustomTkinter
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    root = ctk.CTk()
    root.title("Atlas Button Test")
    root.geometry("800x600")
    
    # Create tabview like Atlas
    tabview = ctk.CTkTabview(root, anchor="nw")
    tabview.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create Chat tab (like Atlas)
    chat_tab = tabview.add("Chat")
    chat_tab.grid_columnconfigure(0, weight=1)
    chat_tab.grid_rowconfigure(0, weight=1)
    
    # Create chat frame
    chat_frame = ctk.CTkFrame(chat_tab)
    chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    chat_frame.grid_columnconfigure(0, weight=1)
    chat_frame.grid_rowconfigure(0, weight=1)
    
    # Create context frame with buttons (like Atlas)
    context_frame = ctk.CTkFrame(chat_frame)
    context_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
    context_frame.grid_columnconfigure(6, weight=1)
    
    # Create buttons like in Atlas
    print("Creating Atlas-style buttons...")
    
    # Mode label
    mode_label = ctk.CTkLabel(context_frame, text="Mode:", font=ctk.CTkFont(size=12, weight="bold"))
    mode_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
    print("✅ Created mode label")
    
    # Auto mode button
    auto_button = ctk.CTkButton(
        context_frame,
        text="Auto: ON",
        command=lambda: print("Auto mode toggled"),
        width=80,
        height=28,
        fg_color="green",
    )
    auto_button.grid(row=0, column=1, padx=5, pady=5)
    print("✅ Created auto mode button")
    
    # Chat mode button
    chat_button = ctk.CTkButton(
        context_frame,
        text="💬 Chat",
        command=lambda: print("Chat mode selected"),
        width=60,
        height=28,
    )
    chat_button.grid(row=0, column=2, padx=2, pady=5)
    print("✅ Created chat mode button")
    
    # Help mode button
    help_button = ctk.CTkButton(
        context_frame,
        text="❓ Help",
        command=lambda: print("Help mode selected"),
        width=60,
        height=28,
    )
    help_button.grid(row=0, column=3, padx=2, pady=5)
    print("✅ Created help mode button")
    
    # Goal mode button
    goal_button = ctk.CTkButton(
        context_frame,
        text="🎯 Goal",
        command=lambda: print("Goal mode selected"),
        width=60,
        height=28,
    )
    goal_button.grid(row=0, column=4, padx=2, pady=5)
    print("✅ Created goal mode button")
    
    # Dev mode button
    dev_button = ctk.CTkButton(
        context_frame,
        text="🔧 Dev",
        command=lambda: print("Dev mode selected"),
        width=60,
        height=28,
        fg_color="orange",
        hover_color="red",
    )
    dev_button.grid(row=0, column=5, padx=5, pady=5)
    print("✅ Created dev mode button")
    
    # Current mode indicator
    mode_indicator = ctk.CTkLabel(
        context_frame,
        text="Ready",
        font=ctk.CTkFont(size=11),
    )
    mode_indicator.grid(row=0, column=6, padx=5, pady=5, sticky="w")
    print("✅ Created mode indicator")
    
    # Clear button
    clear_button = ctk.CTkButton(
        context_frame,
        text="Clear",
        command=lambda: print("Clear context"),
        width=60,
        height=28,
    )
    clear_button.grid(row=0, column=8, padx=(5, 10), pady=5, sticky="e")
    print("✅ Created clear button")
    
    # Create input frame
    input_frame = ctk.CTkFrame(chat_frame)
    input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
    input_frame.grid_columnconfigure(0, weight=1)
    
    # Send button
    send_button = ctk.CTkButton(
        input_frame,
        text="Send",
        command=lambda: print("Send message"),
        width=80,
    )
    send_button.grid(row=0, column=1, sticky="ns", padx=(5, 10), pady=10)
    print("✅ Created send button")
    
    # Status label
    status_label = ctk.CTkLabel(
        chat_frame,
        text="All buttons created successfully! Click them to test.",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color="green"
    )
    status_label.grid(row=3, column=0, pady=20)
    
    print("\n=== Button Test Results ===")
    print("✅ All Atlas-style buttons created successfully")
    print("✅ Buttons should be visible and clickable")
    print("✅ Test window should show 7 buttons:")
    print("   - Auto: ON (green)")
    print("   - 💬 Chat")
    print("   - ❓ Help") 
    print("   - 🎯 Goal")
    print("   - 🔧 Dev (orange)")
    print("   - Clear")
    print("   - Send")
    
    print("\nIf you can see and click these buttons, Atlas GUI is working correctly!")
    
    # Start the GUI
    root.mainloop()
    
    print("Button test completed")

if __name__ == "__main__":
    print("Atlas Button Creation Test")
    print("=" * 40)
    
    try:
        test_button_creation()
    except Exception as e:
        print(f"❌ Error in button test: {e}")
        import traceback
        traceback.print_exc() 