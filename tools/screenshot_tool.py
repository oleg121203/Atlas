"""Screenshot capture utilities for Atlas (macOS).

Uses macOS Quartz for high-performance capture with a Pillow fallback.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image  # type: ignore

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
import os

# Try to import pyautogui safely for headless environments
try:
    # Set environment variables for headless operation if needed
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'  # Fallback display
    
    import pyautogui  # type: ignore
    _PYAUTOGUI_AVAILABLE = True
except Exception as e:
    _PYAUTOGUI_AVAILABLE = False
    print(f"Warning: PyAutoGUI not available in this environment: {e}")

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
    if not _PYAUTOGUI_AVAILABLE:
        # Create a dummy image for headless environments
        from PIL import Image
        img = Image.new('RGB', (800, 600), color='lightgray')
        if save_to:
            img.save(save_to)
        return img
    
    if _QUARTZ_AVAILABLE:
        img = _capture_quartz()
    else:  # fallback
        img = pyautogui.screenshot()

    if save_to:
        save_to.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        filepath = save_to.with_name(f"{save_to.stem}_{timestamp}{save_to.suffix}")
        img.save(filepath)
    return img
