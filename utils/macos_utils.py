"""macOS-specific configurations and utilities for Atlas."""

import os
import sys
from pathlib import Path
from typing import Optional

def setup_macos_environment():
    """Set up macOS-specific environment variables and configurations."""
    
    # Set up PATH for Homebrew installations
    homebrew_paths = [
        "/opt/homebrew/bin",  # Apple Silicon Macs
        "/usr/local/bin",     # Intel Macs
    ]
    
    current_path = os.environ.get("PATH", "")
    for path in homebrew_paths:
        if os.path.exists(path) and path not in current_path:
            os.environ["PATH"] = f"{path}:{current_path}"
    
    # Set up Python path for proper imports
    current_dir = Path(__file__).parent.parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

def configure_macos_gui():
    """Configure GUI settings specific to macOS."""
    try:
        import customtkinter as ctk
        
        # Set appearance mode based on system setting
        try:
            import darkdetect
            if darkdetect.isDark():
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("light")
        except ImportError:
            # Default to system setting if darkdetect not available
            ctk.set_appearance_mode("system")
        
        # Use system color theme
        ctk.set_default_color_theme("blue")
        
    except ImportError:
        print("CustomTkinter not available")

def get_macos_app_support_dir() -> Path:
    """Get the Application Support directory for macOS."""
    home = Path.home()
    app_support = home / "Library" / "Application Support" / "Atlas"
    app_support.mkdir(parents=True, exist_ok=True)
    return app_support

def configure_macos_screenshot():
    """Configure screenshot capabilities for macOS."""
    screenshot_config = {
        'method': 'quartz',  # Prefer native Quartz
        'fallback': 'pyautogui',
        'save_format': 'PNG',
        'default_location': get_macos_app_support_dir() / "screenshots"
    }
    
    # Create screenshots directory
    screenshot_config['default_location'].mkdir(parents=True, exist_ok=True)
    
    return screenshot_config

def check_macos_permissions():
    """Check and inform about required macOS permissions."""
    permissions_needed = [
        "Screen Recording (for screenshots)",
        "Accessibility (for automation)",
        "Camera (if using vision features)",
        "Microphone (if using audio features)"
    ]
    
    print("macOS Permissions Notice:")
    print("Atlas may require the following permissions to function properly:")
    for permission in permissions_needed:
        print(f"  • {permission}")
    print("You may be prompted to grant these permissions when features are first used.")
    print("To manage permissions: System Preferences > Security & Privacy > Privacy")

def setup_macos_dock_icon():
    """Set up dock icon for the application."""
    try:
        import tkinter as tk
        from pathlib import Path
        
        # Look for icon file
        icon_paths = [
            Path(__file__).parent.parent / "assets" / "icon.icns",
            Path(__file__).parent.parent / "assets" / "icon.png",
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists():
                return str(icon_path)
        
    except Exception as e:
        print(f"Could not set up dock icon: {e}")
    
    return None

# Initialize macOS-specific settings when imported
if sys.platform == "darwin":
    setup_macos_environment()
