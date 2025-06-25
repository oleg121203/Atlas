"""Modern macOS screenshot utilities using native APIs."""
"""MacOS-specific screenshot utilities.

Provides multiple methods for capturing screenshots on macOS.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import PIL.Image


def capture_screen_native_macos(save_path: Optional[Path] = None) -> PIL.Image.Image:
    """Capture screen using macOS native 'screencapture' command.

    Parameters
    ----------
    save_path : Optional[Path], optional
        Path to save the screenshot, by default None

    Returns
    -------
    PIL.Image.Image
        The captured screenshot as a PIL Image
    """
    if save_path is None:
        # Create a temporary file if no path provided
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp_file.close()
        temp_path = Path(temp_file.name)
    else:
        temp_path = save_path

    try:
        # Use the macOS screencapture command
        result = subprocess.run(
            ["screencapture", "-x", str(temp_path)],
            capture_output=True,
            check=True,
            timeout=5,
        )

        if result.returncode != 0:
            raise Exception(f"screencapture failed: {result.stderr.decode()}")

        # Open the saved image
        img = PIL.Image.open(temp_path)

        # Convert to make sure we have a copy in memory
        img = img.copy()

        # Clean up temporary file if we created one
        if save_path is None:
            os.unlink(temp_path)

        return img

    except Exception as e:
        # Clean up on failure
        if save_path is None and os.path.exists(temp_path):
            os.unlink(temp_path)
        raise Exception(f"Native macOS screenshot failed: {e}")


def capture_screen_applescript() -> PIL.Image.Image:
    """Capture screen using AppleScript.

    Returns
    -------
    PIL.Image.Image
        The captured screenshot as a PIL Image
    """
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    temp_file.close()
    temp_path = Path(temp_file.name)

    try:
        # AppleScript to capture the screen
        script = f'''
        tell application "System Events"
            set filePath to "{temp_path}"
            tell application "Screenshot" to activate
            delay 0.5
            keystroke "1" using {{command down, shift down}}
            delay 1
            keystroke "s" using {{command down}}
            delay 0.5
            keystroke filePath
            delay 0.5
            keystroke return
            delay 0.5
        end tell
        '''

        # Run the AppleScript
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            check=True,
            timeout=10,
        )

        if result.returncode != 0:
            raise Exception(f"AppleScript failed: {result.stderr.decode()}")

        # Wait briefly for the file to be written
        import time
        time.sleep(1)

        # Open the saved image
        img = PIL.Image.open(temp_path)

        # Convert to make sure we have a copy in memory
        img = img.copy()

        # Clean up
        os.unlink(temp_path)

        return img

    except Exception as e:
        # Clean up on failure
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise Exception(f"AppleScript screenshot failed: {e}")


def test_screenshot_methods():
    """Test available screenshot methods on macOS."""
    methods = []

    # Test native screencapture
    try:
        capture_screen_native_macos()
        methods.append("native_screencapture")
        print("✅ Native screencapture: Working")
    except Exception as e:
        print(f"❌ Native screencapture: {e}")

    # Test AppleScript
    try:
        capture_screen_applescript()
        methods.append("applescript")
        print("✅ AppleScript: Working")
    except Exception as e:
        print(f"❌ AppleScript: {e}")

    return methods
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from PIL import Image


def capture_screen_native_macos(save_to: Optional[Path] = None) -> Image.Image:
    """Capture screen using native macOS screencapture command."""
    try:
        #Create temporary file for screenshot
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        #Use native macOS screencapture command
        result = subprocess.run([
            "screencapture",
            "-x",  #Do not play sounds
            "-t", "png",  #Format
            tmp_path,
        ], check=False, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"screencapture failed: {result.stderr}")

        #Load image with PIL
        img = Image.open(tmp_path)

        #Convert to RGB if needed (screencapture usually outputs RGB)
        if img.mode != "RGB":
            img = img.convert("RGB")

        #Save to final destination if requested
        if save_to:
            img.save(save_to)

        #Clean up temporary file
        Path(tmp_path).unlink(missing_ok=True)

        return img

    except Exception as e:
        #Clean up on error
        if "tmp_path" in locals():
            Path(tmp_path).unlink(missing_ok=True)
        raise Exception(f"Native macOS screenshot failed: {e}")

def capture_screen_applescript() -> Image.Image:
    """Capture screen using AppleScript (alternative method)."""
    try:
        #Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        #AppleScript to take screenshot
        applescript = f"""
        tell application "System Events"
            set desktop_picture to (do shell script "screencapture -x '{tmp_path}'")
        end tell
        """

        #Execute AppleScript
        result = subprocess.run([
            "osascript", "-e", applescript,
        ], check=False, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"AppleScript screenshot failed: {result.stderr}")

        #Load and return image
        img = Image.open(tmp_path)
        if img.mode != "RGB":
            img = img.convert("RGB")

        #Clean up
        Path(tmp_path).unlink(missing_ok=True)

        return img

    except Exception as e:
        if "tmp_path" in locals():
            Path(tmp_path).unlink(missing_ok=True)
        raise Exception(f"AppleScript screenshot failed: {e}")

def test_screenshot_methods():
    """Test available screenshot methods on macOS."""
    methods = []

    #Test native screencapture
    try:
        capture_screen_native_macos()
        methods.append("native_screencapture")
        print("✅ Native screencapture: Working")
    except Exception as e:
        print(f"❌ Native screencapture: {e}")

    #Test AppleScript
    try:
        capture_screen_applescript()
        methods.append("applescript")
        print("✅ AppleScript: Working")
    except Exception as e:
        print(f"❌ AppleScript: {e}")

    return methods

if __name__ == "__main__":
    print("Testing macOS screenshot methods...")
    available_methods = test_screenshot_methods()
    print(f"Available methods: {available_methods}")
