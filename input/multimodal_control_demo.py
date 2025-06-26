import os
import sys
import time
import traceback
import tkinter as tk

# Add the root Atlas directory to the path so we can import from modules
atlas_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(atlas_root)

try:
    from input.voice_command_parser import VoiceCommandParser
    from input.gesture_hotkey_mapper import GestureHotkeyMapper
except ImportError as e:
    print(f"Import error for input modules: {e}")
    print("Unable to run demo due to missing input dependencies.")
    traceback.print_exc()
    sys.exit(1)

try:
    from ui.command_palette import CommandPalette
except ImportError as e:
    print(f"Import error for UI modules: {e}")
    print("Continuing demo without UI components.")
    traceback.print_exc()
    CommandPalette = None

def demonstrate_multimodal_control():
    """Demonstrate the multimodal control interface"""
    print("Initializing Multimodal Control Interface Demo...")
    
    # Initialize voice command parser
    print("\nInitializing Voice Command Parser...")
    voice_parser = VoiceCommandParser()
    
    # Initialize hotkey mapper
    print("\nInitializing Hotkey Mapper...")
    hotkey_mapper = GestureHotkeyMapper()
    
    # Register example hotkeys for the demo with macOS-friendly options
    hotkeys = [
        ("command+shift+left", {"action": "create_workflow", "parameters": {"name": "quick workflow"}}),
        ("command+shift+right", {"action": "open_dashboard", "parameters": {"name": "main dashboard"}})
    ]
    
    for hotkey, action in hotkeys:
        try:
            hotkey_mapper.register_hotkey(hotkey, action)
            print(f"Registered hotkey: {hotkey}")
        except Exception as e:
            print(f"Failed to register hotkey: {hotkey}. Error: {e}")
    
    command_palette = None
    if CommandPalette:
        # Initialize command palette (GUI)
        print("\nInitializing Command Palette...")
        root = tk.Tk()
        root.title("Multimodal Control Demo")
        root.geometry("600x400")
        
        command_palette = CommandPalette(root)
        
        # Add a button to show the command palette
        def show_palette():
            command_palette.show(context="workflow_editor")
        
        palette_button = tk.Button(root, text="Show Command Palette (Command+Shift+P)", command=show_palette)
        palette_button.pack(pady=10)
        
        # Add instructions
        instructions = tk.Label(root, text="1. Press Command+Shift+Left to create a workflow\n2. Press Command+Shift+Right to open dashboard\n3. Say voice commands like 'create workflow test'\n4. Click button to show command palette", justify=tk.LEFT)
        instructions.pack(pady=10)
    else:
        print("Skipping command palette UI initialization due to missing dependencies.")
    
    # Start listening for hotkeys
    print("\nStarting to listen for hotkeys...")
    print("Instructions:")
    print("- Press Command+Shift+Left to create a workflow")
    print("- Press Command+Shift+Right to open a dashboard")
    print("- Say voice commands like 'create workflow test'")
    if command_palette:
        print("- Click the button to show the command palette")
    print("Press Ctrl+C in terminal to exit.")
    
    try:
        # Start hotkey listening in a separate thread if supported
        hotkey_mapper.start_listening()
        print("Started listening for hotkeys")
    except Exception as e:
        print(f"Failed to start listening for hotkeys: {e}")
        print("Hotkey functionality may be limited on this system. On macOS, you may need to run the script with sudo or grant keyboard access permissions in System Preferences > Security & Privacy > Accessibility.")
        print("Continuing demo without hotkey listening.")

    try:
        print("Starting voice command listening...")
        voice_parser.calibrate_microphone(duration=5)
        
        if command_palette:
            # Run GUI main loop
            root.mainloop()
        
    except KeyboardInterrupt:
        print("\nMultimodal control demo terminated by user.")
    finally:
        hotkey_mapper.stop_listening()
        try:
            if command_palette and root.winfo_exists():
                root.destroy()
                print("GUI window closed.")
            elif command_palette:
                print("GUI window already closed or not initialized.")
        except Exception as e:
            print(f"Error closing GUI window: {e}")
            print("Continuing with demo shutdown.")

if __name__ == "__main__":
    try:
        demonstrate_multimodal_control()
    except Exception as e:
        print(f"An error occurred during the demo: {e}")
        traceback.print_exc()
        sys.exit(1)
