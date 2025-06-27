#!/usr/bin/env python3
"""
Simple test for scrolling functionality without problematic elements
"""

import customtkinter as ctk


def test_simple_scrolling():
    """Test basic scrolling with many items."""
    root = ctk.CTk()
    root.title("Simple Scrolling Test - Fixed")
    root.geometry("600x500")

    # Create scrollable frame
    scroll_frame = ctk.CTkScrollableFrame(root, label_text="Test Items", height=300)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Add many items to test scrolling
    for i in range(30):
        item_frame = ctk.CTkFrame(scroll_frame, height=35)
        item_frame.pack(fill="x", padx=5, pady=1)

        # Item number
        num_label = ctk.CTkLabel(item_frame, text=f"{i + 1:2d}.", width=30)
        num_label.pack(side="left", padx=5, pady=5)

        # Item title
        title_label = ctk.CTkLabel(item_frame, text=f"Task Item {i + 1}")
        title_label.pack(side="left", padx=5, pady=5)

        # Status indicator
        if i < 5:
            status_label = ctk.CTkLabel(
                item_frame, text="●", text_color="green", font=ctk.CTkFont(size=16)
            )
        elif i < 15:
            status_label = ctk.CTkLabel(
                item_frame, text="●", text_color="orange", font=ctk.CTkFont(size=16)
            )
        else:
            status_label = ctk.CTkLabel(
                item_frame, text="●", text_color="gray", font=ctk.CTkFont(size=16)
            )
        status_label.pack(side="right", padx=10, pady=5)

        # Progress bar
        progress = (i + 1) / 30.0
        progress_bar = ctk.CTkProgressBar(item_frame, width=80)
        progress_bar.pack(side="right", padx=5, pady=5)
        progress_bar.set(progress)

    # Add info label
    info_label = ctk.CTkLabel(
        root, text="Test scrolling with 30 items. Use scroll wheel or scrollbar."
    )
    info_label.pack(pady=5)

    # Add status label
    status_label = ctk.CTkLabel(root, text="Status: Ready - No problematic buttons")
    status_label.pack(pady=5)

    print(
        "Simple scrolling test started. You should see 30 items and be able to scroll to see all of them."
    )
    print("No problematic buttons - just natural scrolling.")

    root.mainloop()


def test_hierarchical_structure():
    """Test hierarchical structure without complex scrolling."""
    root = ctk.CTk()
    root.title("Hierarchical Structure Test")
    root.geometry("800x600")

    # Create main frame
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create scrollable frame
    scroll_frame = ctk.CTkScrollableFrame(
        main_frame, label_text="Hierarchical Tasks", height=400
    )
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create hierarchical structure
    levels = [
        ("🎯 Strategic Level", "green", 0),
        ("📋 Tactical Level", "orange", 1),
        ("⚡ Operational Level", "blue", 2),
    ]

    for level_name, color, level in levels:
        # Level header
        level_header = ctk.CTkLabel(
            scroll_frame,
            text=level_name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=color,
        )
        level_header.pack(anchor="w", padx=10, pady=(10, 5))

        # Add tasks for this level
        for i in range(8):
            task_frame = ctk.CTkFrame(scroll_frame, height=35)
            task_frame.pack(fill="x", padx=(level * 20 + 10, 10), pady=1)

            # Task title
            title = f"Task {level}.{i + 1}"
            title_label = ctk.CTkLabel(
                task_frame, text=title, font=ctk.CTkFont(size=11)
            )
            title_label.pack(side="left", padx=10, pady=5)

            # Status
            status_label = ctk.CTkLabel(
                task_frame, text="●", text_color=color, font=ctk.CTkFont(size=16)
            )
            status_label.pack(side="right", padx=10, pady=5)

            # Progress
            progress = (i + 1) / 8.0
            progress_bar = ctk.CTkProgressBar(task_frame, width=60)
            progress_bar.pack(side="right", padx=5, pady=5)
            progress_bar.set(progress)

    # Add instructions
    instructions = ctk.CTkLabel(
        root,
        text="""
    Hierarchical Structure Test:

    • Scroll through the tree structure
    • Notice the indentation levels
    • All items should be accessible
    • No problematic buttons or controls

    Use mouse wheel or scrollbar to navigate.
    """,
        justify="left",
    )
    instructions.pack(pady=10)

    print("Hierarchical structure test started.")

    root.mainloop()


def main():
    """Run the tests."""
    print("Simple Scrolling Tests - Fixed Version")
    print("=" * 40)

    while True:
        print("\nChoose a test:")
        print("1. Simple Scrolling Test (30 items)")
        print("2. Hierarchical Structure Test")
        print("3. Run Both Tests")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            test_simple_scrolling()
        elif choice == "2":
            test_hierarchical_structure()
        elif choice == "3":
            print("Running both tests...")
            test_simple_scrolling()
            test_hierarchical_structure()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()
