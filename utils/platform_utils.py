"""Platform detection utilities for Atlas."""

import platform
import os
import sys
from typing import Dict, Any

# Platform detection
CURRENT_OS = platform.system().lower()
IS_MACOS = CURRENT_OS == 'darwin'
IS_LINUX = CURRENT_OS == 'linux'
IS_WINDOWS = CURRENT_OS == 'windows'

# Check if running in headless environment
IS_HEADLESS = (
    os.environ.get('DISPLAY') is None and IS_LINUX
) or (
    os.environ.get('CI') == 'true'
) or (
    'pytest' in sys.modules
)

def get_platform_info() -> Dict[str, Any]:
    """Get comprehensive platform information."""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'is_macos': IS_MACOS,
        'is_linux': IS_LINUX,
        'is_windows': IS_WINDOWS,
        'is_headless': IS_HEADLESS,
        'has_display': os.environ.get('DISPLAY') is not None or IS_MACOS or IS_WINDOWS,
    }

def configure_for_platform():
    """Configure application settings based on platform."""
    if IS_HEADLESS:
        # Configure matplotlib for headless operation
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
        except ImportError:
            pass
    
    # Platform-specific configurations
    if IS_MACOS:
        # macOS specific settings
        pass
    elif IS_LINUX:
        # Linux specific settings
        if not IS_HEADLESS:
            # Set up X11 if needed
            pass
    elif IS_WINDOWS:
        # Windows specific settings
        pass

def get_screenshot_method():
    """Determine the best screenshot method for the current platform."""
    methods = []
    
    if IS_MACOS:
        try:
            from Quartz import CGWindowListCreateImage
            methods.append('quartz')
        except ImportError:
            pass
    
    # Check for PyAutoGUI availability
    if not IS_HEADLESS:
        try:
            import pyautogui
            methods.append('pyautogui')
        except ImportError:
            pass
    
    if not methods:
        methods.append('dummy')
    
    return methods[0] if methods else 'dummy'

# Initialize platform configuration on import
configure_for_platform()
