"""Platform detection utilities for Atlas."""
"""Platform detection and utility functions."""

import os
import platform
import sys
from typing import Dict, Any

# Platform constants
IS_MACOS = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_ARM = platform.machine().startswith("arm") or platform.machine() == "aarch64"
IS_APPLE_SILICON = IS_MACOS and (platform.machine() == "arm64" or platform.machine().startswith("arm"))

# Environment detection
IS_HEADLESS = not os.environ.get("DISPLAY") and not IS_MACOS and not IS_WINDOWS

def get_platform_info() -> Dict[str, Any]:
    """Get detailed information about the current platform.

    Returns
    -------
    Dict[str, Any]
        Dictionary with platform information
    """
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "is_64bit": sys.maxsize > 2**32,
        "is_macos": IS_MACOS,
        "is_windows": IS_WINDOWS,
        "is_linux": IS_LINUX,
        "is_arm": IS_ARM,
        "is_apple_silicon": IS_APPLE_SILICON,
        "is_headless": IS_HEADLESS,
    }

    # Add display information if available
    try:
        if IS_MACOS:
            # Get screen resolution on macOS
            import subprocess
            result = subprocess.run(["system_profiler", "SPDisplaysDataType"], 
                                   capture_output=True, text=True, check=True)
            info["display_info"] = result.stdout

            # Try to extract resolution
            import re
            resolution = re.search(r"Resolution: (\d+ x \d+)", result.stdout)
            if resolution:
                info["display_resolution"] = resolution.group(1)
    except Exception as e:
        info["display_error"] = str(e)

    return info
import importlib.util
import os
import platform
import sys
from typing import Any, Dict

#Platform detection
CURRENT_OS = platform.system().lower()
IS_MACOS = CURRENT_OS == "darwin"
IS_LINUX = CURRENT_OS == "linux"
IS_WINDOWS = CURRENT_OS == "windows"

#Check if running in headless environment
IS_HEADLESS = (
    os.environ.get("DISPLAY") is None and IS_LINUX
) or (
    os.environ.get("CI") == "true"
) or (
    "pytest" in sys.modules
) or (
    os.environ.get("ATLAS_HEADLESS") == "true"
)

def get_platform_info() -> Dict[str, Any]:
    """Get comprehensive platform information."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "is_macos": IS_MACOS,
        "is_linux": IS_LINUX,
        "is_windows": IS_WINDOWS,
        "is_headless": IS_HEADLESS,
        "has_display": os.environ.get("DISPLAY") is not None or IS_MACOS or IS_WINDOWS,
    }

def configure_for_platform():
    """Configure application settings based on platform."""
    if IS_HEADLESS:
        #Configure matplotlib for headless operation
        try:
            import matplotlib
            matplotlib.use("Agg")  #Use non-interactive backend
        except ImportError:
            pass

    #Platform-specific configurations
    if IS_MACOS:
        #macOS specific settings
        pass
    elif IS_LINUX:
        #Linux specific settings
        if not IS_HEADLESS:
            #Set up X11 if needed
            pass
    elif IS_WINDOWS:
        #Windows specific settings
        pass

def get_screenshot_method():
    """Determine the best screenshot method for the current platform."""
    methods = []

    if IS_MACOS:
        if importlib.util.find_spec("Quartz"):
            methods.append("quartz")

    # Check for PyAutoGUI availability
    if not IS_HEADLESS:
        if importlib.util.find_spec("pyautogui"):
            methods.append("pyautogui")

    if not methods:
        methods.append("dummy")

    return methods[0] if methods else "dummy"

#Initialize platform configuration on import
configure_for_platform()
