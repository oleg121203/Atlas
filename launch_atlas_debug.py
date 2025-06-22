#!/usr/bin/env python3
"""
Debug launch script for Atlas with GUI verification
"""

import sys
import os
import platform
import subprocess

def check_environment():
    """Check environment for GUI support"""
    print("=== Environment Check ===")
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print(f"Display: {os.environ.get('DISPLAY', 'Not set')}")
    print(f"CI: {os.environ.get('CI', 'Not set')}")
    print(f"ATLAS_HEADLESS: {os.environ.get('ATLAS_HEADLESS', 'Not set')}")
    
    # Check if we're in a headless environment
    is_headless = (
        os.environ.get("DISPLAY") is None and platform.system().lower() == "linux"
    ) or (
        os.environ.get("CI") == "true"
    ) or (
        "pytest" in sys.modules
    ) or (
        os.environ.get("ATLAS_HEADLESS") == "true"
    )
    
    print(f"Detected as headless: {is_headless}")
    return is_headless

def check_dependencies():
    """Check if required GUI dependencies are available"""
    print("\n=== Dependency Check ===")
    
    try:
        import customtkinter as ctk
        print("✅ CustomTkinter available")
    except ImportError as e:
        print(f"❌ CustomTkinter not available: {e}")
        return False
    
    try:
        import tkinter as tk
        print("✅ Tkinter available")
    except ImportError as e:
        print(f"❌ Tkinter not available: {e}")
        return False
    
    try:
        import matplotlib
        print("✅ Matplotlib available")
    except ImportError as e:
        print(f"❌ Matplotlib not available: {e}")
    
    return True

def launch_atlas():
    """Launch Atlas with debug information"""
    print("\n=== Launching Atlas ===")
    
    # Set environment to ensure GUI mode
    env = os.environ.copy()
    env['ATLAS_HEADLESS'] = 'false'
    
    try:
        # Launch Atlas with debug mode
        result = subprocess.run([
            sys.executable, 'main.py', '--debug'
        ], env=env, capture_output=False, text=True)
        
        print(f"Atlas exited with code: {result.returncode}")
        
    except KeyboardInterrupt:
        print("\nAtlas interrupted by user")
    except Exception as e:
        print(f"Error launching Atlas: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("Atlas Debug Launcher")
    print("=" * 50)
    
    # Check environment
    is_headless = check_environment()
    
    if is_headless:
        print("\n⚠️  Warning: Running in headless environment")
        print("GUI may not display properly")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborting...")
            return
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing required dependencies")
        print("Please install missing packages")
        return
    
    # Launch Atlas
    launch_atlas()

if __name__ == "__main__":
    main() 