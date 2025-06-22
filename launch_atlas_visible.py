#!/usr/bin/env python3
"""
Enhanced Atlas launcher that ensures the GUI window is visible
"""

import sys
import os
import platform
import subprocess
import time

def ensure_gui_visibility():
    """Ensure the GUI window is visible and focused"""
    print("=== GUI Visibility Enhancement ===")
    
    if platform.system() == "Darwin":  # macOS
        print("macOS detected - ensuring window visibility")
        
        # Use osascript to bring window to front
        try:
            subprocess.run([
                "osascript", "-e", 
                'tell application "System Events" to set frontmost of every process whose name contains "Python" to true'
            ], check=False)
            print("✅ Attempted to bring Python windows to front")
        except Exception as e:
            print(f"⚠️  Could not bring windows to front: {e}")
    
    elif platform.system() == "Linux":
        print("Linux detected - checking display")
        if os.environ.get("DISPLAY"):
            print("✅ Display environment available")
        else:
            print("⚠️  No display environment detected")
    
    elif platform.system() == "Windows":
        print("Windows detected - GUI should be visible")
    
    print("If Atlas window is not visible, try:")
    print("1. Check if it's minimized in the dock/taskbar")
    print("2. Look for it behind other windows")
    print("3. Press Cmd+Tab (macOS) or Alt+Tab (Windows/Linux) to switch windows")

def launch_atlas_with_visibility():
    """Launch Atlas with enhanced visibility"""
    print("\n=== Launching Atlas with Enhanced Visibility ===")
    
    # Set environment variables for GUI mode
    env = os.environ.copy()
    env['ATLAS_HEADLESS'] = 'false'
    
    # Additional environment variables for better GUI support
    if platform.system() == "Darwin":
        env['PYTHONUNBUFFERED'] = '1'
        env['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
    
    try:
        print("Starting Atlas...")
        print("The window should appear within 10-15 seconds")
        print("If you don't see it, check the dock/taskbar for minimized windows")
        
        # Launch Atlas
        process = subprocess.Popen([
            sys.executable, 'main.py', '--debug'
        ], env=env)
        
        # Wait a moment for the window to appear
        time.sleep(3)
        
        # Try to bring window to front
        ensure_gui_visibility()
        
        print("\nAtlas is now running!")
        print("Look for the Atlas window with tabs like:")
        print("- Chat")
        print("- Master Agent") 
        print("- Tasks")
        print("- Settings")
        print("\nIf you still don't see buttons, try:")
        print("1. Click on different tabs")
        print("2. Resize the window")
        print("3. Check if the window is behind other applications")
        
        # Wait for the process to complete
        process.wait()
        
        print(f"\nAtlas exited with code: {process.returncode}")
        
    except KeyboardInterrupt:
        print("\nAtlas interrupted by user")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"Error launching Atlas: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("Atlas Enhanced Visibility Launcher")
    print("=" * 50)
    
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    
    # Check if we're in a terminal that supports GUI
    if platform.system() == "Darwin":
        print("✅ macOS detected - GUI should work")
    elif platform.system() == "Linux":
        if os.environ.get("DISPLAY"):
            print("✅ Linux with display detected - GUI should work")
        else:
            print("⚠️  Linux without display - GUI may not work")
    elif platform.system() == "Windows":
        print("✅ Windows detected - GUI should work")
    
    # Launch Atlas
    launch_atlas_with_visibility()

if __name__ == "__main__":
    main() 