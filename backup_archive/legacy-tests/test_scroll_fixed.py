#!/usr/bin/env python3
"""
Simple scrolling test without interactive menu
"""

import customtkinter as ctk

def test_scrolling():
    """Test basic scrolling functionality."""
    root = ctk.CTk()
    root.title("Scrolling Test - Fixed")
    root.geometry("600x500")
    
    # Create scrollable frame
    scroll_frame = ctk.CTkScrollableFrame(root, label_text="Test Items", height=300)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add many items to test scrolling
    for i in range(40):
        item_frame = ctk.CTkFrame(scroll_frame, height=35)
        item_frame.pack(fill="x", padx=5, pady=1)
        
        # Item number
        num_label = ctk.CTkLabel(item_frame, text=f"{i+1:2d}.", width=30)
        num_label.pack(side="left", padx=5, pady=5)
        
        # Item title
        title_label = ctk.CTkLabel(item_frame, text=f"Task Item {i+1}")
        title_label.pack(side="left", padx=5, pady=5)
        
        # Status indicator
        if i < 10:
            status_label = ctk.CTkLabel(item_frame, text="●", text_color="green", font=ctk.CTkFont(size=16))
        elif i < 25:
            status_label = ctk.CTkLabel(item_frame, text="●", text_color="orange", font=ctk.CTkFont(size=16))
        else:
            status_label = ctk.CTkLabel(item_frame, text="●", text_color="gray", font=ctk.CTkFont(size=16))
        status_label.pack(side="right", padx=10, pady=5)
        
        # Progress bar
        progress = (i + 1) / 40.0
        progress_bar = ctk.CTkProgressBar(item_frame, width=80)
        progress_bar.pack(side="right", padx=5, pady=5)
        progress_bar.set(progress)
    
    # Add info label
    info_label = ctk.CTkLabel(root, text="Test scrolling with 40 items. Use scroll wheel or scrollbar.")
    info_label.pack(pady=5)
    
    # Add status label
    status_label = ctk.CTkLabel(root, text="Status: Ready - No problematic buttons")
    status_label.pack(pady=5)
    
    print("Scrolling test started. You should see 40 items and be able to scroll to see all of them.")
    print("No problematic buttons - just natural scrolling.")
    
    root.mainloop()

if __name__ == "__main__":
    test_scrolling() 