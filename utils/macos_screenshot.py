"""Modern macOS screenshot utilities using native APIs."""

import subprocess
import tempfile
from pathlib import Path
from PIL import Image
from typing import Optional

def capture_screen_native_macos(save_to: Optional[Path] = None) -> Image.Image:
    """Capture screen using native macOS screencapture command."""
    try:
        #Create temporary file for screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        #Use native macOS screencapture command
        result = subprocess.run([
            'screencapture', 
            '-x',  #Do not play sounds
            '-t', 'png',  #Format
            tmp_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"screencapture failed: {result.stderr}")
        
        #Load image with PIL
        img = Image.open(tmp_path)
        
        #Convert to RGB if needed (screencapture usually outputs RGB)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        #Save to final destination if requested
        if save_to:
            img.save(save_to)
        
        #Clean up temporary file
        Path(tmp_path).unlink(missing_ok=True)
        
        return img
        
    except Exception as e:
        #Clean up on error
        if 'tmp_path' in locals():
            Path(tmp_path).unlink(missing_ok=True)
        raise Exception(f"Native macOS screenshot failed: {e}")

def capture_screen_applescript() -> Image.Image:
    """Capture screen using AppleScript (alternative method)."""
    try:
        #Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        #AppleScript to take screenshot
        applescript = f'''
        tell application "System Events"
            set desktop_picture to (do shell script "screencapture -x '{tmp_path}'")
        end tell
        '''
        
        #Execute AppleScript
        result = subprocess.run([
            'osascript', '-e', applescript
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"AppleScript screenshot failed: {result.stderr}")
        
        #Load and return image
        img = Image.open(tmp_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        #Clean up
        Path(tmp_path).unlink(missing_ok=True)
        
        return img
        
    except Exception as e:
        if 'tmp_path' in locals():
            Path(tmp_path).unlink(missing_ok=True)
        raise Exception(f"AppleScript screenshot failed: {e}")

def test_screenshot_methods():
    """Test available screenshot methods on macOS."""
    methods = []
    
    #Test native screencapture
    try:
        capture_screen_native_macos()
        methods.append('native_screencapture')
        print("✅ Native screencapture: Working")
    except Exception as e:
        print(f"❌ Native screencapture: {e}")
    
    #Test AppleScript
    try:
        capture_screen_applescript()
        methods.append('applescript')
        print("✅ AppleScript: Working")
    except Exception as e:
        print(f"❌ AppleScript: {e}")
    
    return methods

if __name__ == "__main__":
    print("Testing macOS screenshot methods...")
    available_methods = test_screenshot_methods()
    print(f"Available methods: {available_methods}")
