#!/usr/bin/env python3
"""
Simple GUI test to check if buttons are visible
"""

import sys

import customtkinter as ctk


def test_gui():
    """Test basic GUI functionality with buttons"""

    # Set up CustomTkinter
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    # Create main window
    root = ctk.CTk()
    root.title("Atlas GUI Test")
    root.geometry("600x400")

    # Create main frame
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Title
    title_label = ctk.CTkLabel(
        main_frame, text="Atlas GUI Test", font=ctk.CTkFont(size=24, weight="bold")
    )
    title_label.pack(pady=20)

    # Test buttons frame
    buttons_frame = ctk.CTkFrame(main_frame)
    buttons_frame.pack(pady=20)

    # Test buttons
    test_button1 = ctk.CTkButton(
        buttons_frame, text="Test Button 1", command=lambda: print("Button 1 clicked")
    )
    test_button1.pack(pady=10)

    test_button2 = ctk.CTkButton(
        buttons_frame, text="Test Button 2", command=lambda: print("Button 2 clicked")
    )
    test_button2.pack(pady=10)

    test_button3 = ctk.CTkButton(
        buttons_frame, text="Test Button 3", command=lambda: print("Button 3 clicked")
    )
    test_button3.pack(pady=10)

    # Status label
    status_label = ctk.CTkLabel(
        main_frame,
        text="GUI Test Running - Buttons should be visible above",
        font=ctk.CTkFont(size=14),
    )
    status_label.pack(pady=20)

    # Close button
    close_button = ctk.CTkButton(main_frame, text="Close Test", command=root.quit)
    close_button.pack(pady=10)

    print("GUI Test Window Created")
    print("If you can see buttons, the GUI is working correctly")

    # Start the GUI
    root.mainloop()

    print("GUI Test Completed")


if __name__ == "__main__":
    print("Starting Atlas GUI Test...")
    print(f"Platform: {sys.platform}")
    print(f"Python version: {sys.version}")

    try:
        test_gui()
    except Exception as e:
        print(f"Error in GUI test: {e}")
        import traceback

        traceback.print_exc()
