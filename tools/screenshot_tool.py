"""Screenshot capture utilities for Atlas (Cross-platform).

Uses platform-specific capture methods with fallbacks.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image  #type: ignore
from utils.platform_utils import IS_MACOS, IS_LINUX, IS_HEADLESS

#Import macOS-specific screenshot utilities
if IS_MACOS:
    try:
        from utils.macos_screenshot import capture_screen_native_macos, capture_screen_applescript
        _MACOS_NATIVE_AVAILABLE = True
    except ImportError:
        _MACOS_NATIVE_AVAILABLE = False
else:
    _MACOS_NATIVE_AVAILABLE = False

#Platform-specific imports
_QUARTZ_AVAILABLE = False
_PYAUTOGUI_AVAILABLE = False

if IS_MACOS:
    try:
        #pyobjc Quartz is preferred on macOS (legacy support)
        from Quartz import (
            CGWindowListCreateImage,
            CGMainDisplayID,
            kCGWindowListOptionOnScreenOnly,
            kCGWindowImageDefault,
            CGRectInfinite,

        )
        _QUARTZ_AVAILABLE = True
    except ImportError as e:
        _QUARTZ_AVAILABLE = False
        print(f"Quartz not available: {e}")
    except Exception:  #pragma: no cover
        _QUARTZ_AVAILABLE = False


#Try to import pyautogui safely for headless environments
#Skip if in headless environment or if display is not available
if not IS_HEADLESS:
    try:
        _PYAUTOGUI_AVAILABLE = True
    except Exception as e:
        _PYAUTOGUI_AVAILABLE = False
        print(f"Warning: PyAutoGUI not available in this environment: {e}")
else:
    _PYAUTOGUI_AVAILABLE = False
    print("Warning: PyAutoGUI not available for mouse/keyboard: Headless environment detected")

__all__ = ["capture_screen"]

def _capture_quartz() -> Image.Image:
    """Capture the full screen via Quartz and return a PIL Image."""
    try:
        #Create screenshot using Quartz API
        image_ref = CGWindowListCreateImage(
            CGRectInfinite, kCGWindowListOptionOnScreenOnly, CGMainDisplayID(), kCGWindowImageDefault
        )
        
        if not image_ref:
            raise Exception("Failed to create CGImage")
        
        #Use modern pyobjc API
        from Quartz import CGImageGetWidth, CGImageGetHeight, CGImageGetBytesPerRow
        from Quartz import CGImageGetDataProvider, CGDataProviderCopyData
        
        width = CGImageGetWidth(image_ref)
        height = CGImageGetHeight(image_ref)
        bytes_per_row = CGImageGetBytesPerRow(image_ref)
        data_provider = CGImageGetDataProvider(image_ref)
        data = CGDataProviderCopyData(data_provider)
        
        #Convert CFData to bytes
        if hasattr(data, 'bytes'):
            #Modern pyobjc returns CFData with bytes() method
            buffer = data.bytes()
        else:
            #Fallback if different data type
            buffer = bytes(data)
        
        #Create PIL Image from buffer
        #Note: Quartz returns BGRA format typically
        img = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", bytes_per_row, 1)
        
        #Convert to RGB for consistency
        if img.mode == "RGBA":
            #Create a white background and composite
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1])  #Use alpha channel as mask
            return rgb_img
        
        return img
        
    except Exception as e:
        #If Quartz fails, raise exception to trigger fallback
        raise Exception(f"Quartz capture failed: {e}")

def capture_screen(save_to: Optional[Path] = None) -> Image.Image:
    """Capture the current screen and optionally save to *save_to*.

    Parameters
    ----------
    save_to: pathlib.Path | None
        If provided, the resulting PNG screenshot is written to this path.
    """
    img = None
    last_error = None
    
    #Try different capture methods based on platform and availability
    if IS_MACOS:
        #Try native macOS methods first (most reliable)
        if _MACOS_NATIVE_AVAILABLE:
            try:
                img = capture_screen_native_macos(save_to)
                return img  #Return immediately if successful
            except Exception as e:
                last_error = f"Native screencapture failed: {e}"
                print(last_error)
            
            #Try AppleScript as backup
            try:
                img = capture_screen_applescript()
                if save_to and img:
                    img.save(save_to)
                return img
            except Exception as e:
                last_error = f"AppleScript failed: {e}"
                print(last_error)
        
        #Try Quartz as fallback (if available)
        if _QUARTZ_AVAILABLE and img is None:
            try:
                img = _capture_quartz()
            except Exception as e:
                last_error = f"Quartz capture failed: {e}"
                print(last_error)
    
    #Fallback to PyAutoGUI if macOS methods failed or not macOS
    if img is None and _PYAUTOGUI_AVAILABLE:
        try:
            import pyautogui
            #Disable PyAutoGUI fail-safe for programmatic use
            pyautogui.FAILSAFE = False
            img = pyautogui.screenshot()
            if isinstance(img, Image.Image):
                pass  #Already PIL Image
            else:
                #Convert if needed
                img = Image.fromarray(img)
        except Exception as e:
            last_error = f"PyAutoGUI capture failed: {e}"
            print(last_error)
    
    #Last resort: create a dummy image
    if img is None:
        print(f"Creating dummy screenshot - no capture method available. Last error: {last_error}")
        img = Image.new('RGB', (800, 600), color='lightgray')
        #Add some text to indicate this is a dummy
        try:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.text((50, 250), "Screenshot not available", fill='black')
            draw.text((50, 300), f"(Error: {last_error})", fill='red')
            draw.text((50, 350), f"Platform: {'macOS' if IS_MACOS else 'Linux' if IS_LINUX else 'Unknown'}", fill='blue')
        except Exception:
            pass  #Font issues, just use plain gray
    
    #Save if requested and not already saved
    if save_to and img:
        try:
            img.save(save_to)
        except Exception as e:
            print(f"Failed to save screenshot: {e}")
    
    return img
