"""Screenshot capture utilities for Atlas (Cross-platform).

Uses platform-specific capture methods with fallbacks.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PIL import Image  # type: ignore
from utils.platform_utils import IS_MACOS, IS_LINUX, IS_WINDOWS, IS_HEADLESS

# Platform-specific imports
_QUARTZ_AVAILABLE = False
_PYAUTOGUI_AVAILABLE = False

if IS_MACOS:
    try:
        # pyobjc Quartz is preferred on macOS
        from Quartz import (
            CGWindowListCreateImage,
            CGMainDisplayID,
            kCGWindowListOptionOnScreenOnly,
            kCGWindowImageDefault,
            CGRectInfinite,
        )
        _QUARTZ_AVAILABLE = True
    except Exception:  # pragma: no cover
        _QUARTZ_AVAILABLE = False

import datetime

# Try to import pyautogui safely for headless environments
# Skip if in headless environment or if display is not available
if not IS_HEADLESS:
    try:
        import pyautogui  # type: ignore
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
    image_ref = CGWindowListCreateImage(
        CGRectInfinite, kCGWindowListOptionOnScreenOnly, CGMainDisplayID(), kCGWindowImageDefault
    )
    width = image_ref.width()
    height = image_ref.height()
    bytes_per_row = image_ref.bytesPerRow()
    data_provider = image_ref.dataProvider()
    data = data_provider.data()
    buffer = bytes(data)
    img = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", bytes_per_row, 1)
    return img

def capture_screen(save_to: Optional[Path] = None) -> Image.Image:
    """Capture the current screen and optionally save to *save_to*.

    Parameters
    ----------
    save_to: pathlib.Path | None
        If provided, the resulting PNG screenshot is written to this path.
    """
    img = None
    
    # Try different capture methods based on platform and availability
    if IS_MACOS and _QUARTZ_AVAILABLE:
        try:
            img = _capture_quartz()
        except Exception as e:
            print(f"Quartz capture failed: {e}")
    
    # Fallback to PyAutoGUI if Quartz failed or not available
    if img is None and _PYAUTOGUI_AVAILABLE:
        try:
            import pyautogui
            # Disable PyAutoGUI fail-safe for programmatic use
            pyautogui.FAILSAFE = False
            img = pyautogui.screenshot()
            if isinstance(img, Image.Image):
                pass  # Already PIL Image
            else:
                # Convert if needed
                img = Image.fromarray(img)
        except Exception as e:
            print(f"PyAutoGUI capture failed: {e}")
    
    # Last resort: create a dummy image
    if img is None:
        print("Creating dummy screenshot - no capture method available")
        img = Image.new('RGB', (800, 600), color='lightgray')
        # Add some text to indicate this is a dummy
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            draw.text((50, 300), "Screenshot not available\n(Headless environment)", 
                     fill='black')
        except Exception:
            pass  # Font issues, just use plain gray
    
    # Save if requested
    if save_to:
        try:
            img.save(save_to)
        except Exception as e:
            print(f"Failed to save screenshot: {e}")
    
    return img
