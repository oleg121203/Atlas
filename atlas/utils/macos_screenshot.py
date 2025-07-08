"""
macOS screenshot utilities using native methods.

This module provides functions to capture screenshots on macOS using
native system tools like screencapture and PyObjC.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import PIL.Image


def capture_screen_native_macos(save_to: Optional[Path] = None) -> PIL.Image.Image:
    """Capture screen using native macOS screencapture command.

    Args:
        save_to: Optional path to save the screenshot

    Returns:
        PIL Image object
    """
    try:
        # Create temporary file if no save path provided
        if save_to is None:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_path = tmp.name
        else:
            temp_path = str(save_to)

        # Use macOS screencapture command
        subprocess.run(
            ["screencapture", "-x", temp_path],
            check=True,
            capture_output=True,
        )

        # Load image
        image = PIL.Image.open(temp_path)

        # Clean up temporary file if we created it
        if save_to is None:
            os.unlink(temp_path)

        return image

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to capture screen: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error during screen capture: {e}") from e


def capture_screen_applescript() -> PIL.Image.Image:
    """Capture screen using AppleScript (alternative method).

    Returns:
        PIL Image object
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name

        applescript = f"""
        tell application "System Events"
            set screenshotPath to "{temp_path}"
            do shell script "screencapture -x " & quoted form of screenshotPath
        end tell
        """

        subprocess.run(
            ["osascript", "-e", applescript],
            check=True,
            capture_output=True,
        )

        image = PIL.Image.open(temp_path)
        os.unlink(temp_path)
        return image

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"AppleScript screen capture failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error in AppleScript capture: {e}") from e


def test_screenshot_methods():
    """Test available screenshot methods on macOS.

    Returns:
        List of working screenshot methods
    """
    methods = []

    # Test native screencapture
    try:
        capture_screen_native_macos()
        methods.append("native_screencapture")
    except Exception:
        pass

    # Test AppleScript method
    try:
        capture_screen_applescript()
        methods.append("applescript")
    except Exception:
        pass

    return methods


def capture_screen_macos(method: str = "auto") -> PIL.Image.Image:
    """Capture screen on macOS using the specified or best available method.

    Args:
        method: Method to use ('auto', 'native', 'applescript')

    Returns:
        PIL Image object
    """
    if method == "auto":
        # Try methods in order of preference
        try:
            return capture_screen_native_macos()
        except Exception:
            try:
                return capture_screen_applescript()
            except Exception:
                raise RuntimeError("No working screenshot method available") from None

    elif method == "native":
        return capture_screen_native_macos()
    elif method == "applescript":
        return capture_screen_applescript()
    else:
        raise ValueError(f"Unknown method: {method}")
