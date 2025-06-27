"""Screenshot capture utilities for Atlas (Cross-platform).

Uses platform-specific capture methods with fallbacks.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Optional

from PIL import Image  # type: ignore

from utils.platform_utils import IS_HEADLESS, IS_LINUX, IS_MACOS

# Import macOS-specific screenshot utilities
if IS_MACOS:
    try:
        from utils.macos_screenshot import (
            capture_screen_applescript,
            capture_screen_native_macos,
        )

        _MACOS_NATIVE_AVAILABLE = True
    except ImportError:
        _MACOS_NATIVE_AVAILABLE = False
else:
    _MACOS_NATIVE_AVAILABLE = False

# Platform-specific imports
_QUARTZ_AVAILABLE = False
_PYAUTOGUI_AVAILABLE = False

if IS_MACOS:
    try:
        # pyobjc Quartz is preferred on macOS (legacy support)
        from Quartz import (
            CGMainDisplayID,
            CGRectInfinite,
            CGWindowListCreateImage,
            kCGWindowImageDefault,
            kCGWindowListOptionOnScreenOnly,
        )

        _QUARTZ_AVAILABLE = True
    except ImportError as e:
        _QUARTZ_AVAILABLE = False
        print(f"Quartz not available: {e}")
    except Exception:  # pragma: no cover
        _QUARTZ_AVAILABLE = False


# Try to import pyautogui safely for headless environments
# Skip if in headless environment or if display is not available
import types

try:
    import pyautogui as pyautogui  # noqa: F401 - re-export for unit-test patching

    _PYAUTOGUI_AVAILABLE = not IS_HEADLESS
except Exception as e:  # pragma: no cover – keep attribute for tests
    pyautogui = types.ModuleType("pyautogui")

    def _noop(*_a, **_kw):
        raise RuntimeError("pyautogui unavailable")

    pyautogui.screenshot = _noop  # type: ignore[attr-defined]
    _PYAUTOGUI_AVAILABLE = False
    if not IS_HEADLESS:
        print(f"Warning: PyAutoGUI import failed: {e}")
else:
    _PYAUTOGUI_AVAILABLE = False
    print(
        "Warning: PyAutoGUI not available for mouse/keyboard: Headless environment detected"
    )

__all__ = ["capture_screen"]


def _capture_quartz() -> Image.Image:
    """Capture the full screen via Quartz and return a PIL Image."""
    try:
        # Create screenshot using Quartz API
        image_ref = CGWindowListCreateImage(
            CGRectInfinite,
            kCGWindowListOptionOnScreenOnly,
            CGMainDisplayID(),
            kCGWindowImageDefault,
        )

        if not image_ref:
            raise Exception("Failed to create CGImage")

        # Use modern pyobjc API
        from Quartz import (
            CGDataProviderCopyData,
            CGImageGetBytesPerRow,
            CGImageGetDataProvider,
            CGImageGetHeight,
            CGImageGetWidth,
        )

        width = CGImageGetWidth(image_ref)
        height = CGImageGetHeight(image_ref)
        bytes_per_row = CGImageGetBytesPerRow(image_ref)
        data_provider = CGImageGetDataProvider(image_ref)
        data = CGDataProviderCopyData(data_provider)

        # Convert CFData to bytes - use bytes() method if available, else convert directly
        buffer = data.bytes() if hasattr(data, "bytes") else bytes(data)

        # Create PIL Image from buffer
        # Note: Quartz returns BGRA format typically
        img = Image.frombuffer(
            "RGBA", (width, height), buffer, "raw", "BGRA", bytes_per_row, 1
        )

        # Convert to RGB for consistency
        if img.mode == "RGBA":
            # Create a white background and composite
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
            return rgb_img

        return img

    except Exception as e:
        # If Quartz fails, raise exception to trigger fallback
        raise Exception(f"Quartz capture failed: {e}") from e


def capture_screen(save_to: Optional[Path] = None) -> Image.Image:
    """Capture the current screen and optionally save to *save_to*.

    Parameters
    ----------
    save_to: pathlib.Path | None
        If provided, the resulting PNG screenshot is written to this path.
    """
    img = None
    last_error = None

    # Ordered attempt list ------------------------------------------------

    # 1. Quartz (only if available)
    if img is None and _QUARTZ_AVAILABLE:
        try:
            img = _capture_quartz()
        except Exception as e:
            last_error = f"Quartz capture failed: {e}"
            print(last_error)

    # 2. PyAutoGUI (works cross-platform; tests patch this path)
    if img is None and _PYAUTOGUI_AVAILABLE:
        try:
            pyautogui.FAILSAFE = False  # type: ignore[attr-defined]
            img = pyautogui.screenshot()  # type: ignore[attr-defined]
            if not isinstance(img, Image.Image):
                img = Image.fromarray(img)
        except Exception as e:
            last_error = f"PyAutoGUI capture failed: {e}"
            if not IS_HEADLESS:
                print(last_error)

    # 3. macOS native screencapture / AppleScript fallbacks
    if img is None and IS_MACOS and _MACOS_NATIVE_AVAILABLE:
        try:
            img = capture_screen_native_macos(None)
        except Exception as e:
            last_error = f"Native screencapture failed: {e}"
            print(last_error)

        if img is None:
            try:
                img = capture_screen_applescript()
            except Exception as e:
                last_error = f"AppleScript failed: {e}"
                print(last_error)

    # Last resort: create a dummy image
    if img is None:
        print(
            f"Creating dummy screenshot - no capture method available. Last error: {last_error}"
        )
        img = Image.new("RGB", (800, 600), color="lightgray")
        # Add some text to indicate this is a dummy
        try:
            from PIL import ImageDraw

            draw = ImageDraw.Draw(img)
            draw.text((50, 250), "Screenshot not available", fill="black")
            draw.text((50, 300), f"(Error: {last_error})", fill="red")
            draw.text(
                (50, 350),
                f"Platform: {'macOS' if IS_MACOS else 'Linux' if IS_LINUX else 'Unknown'}",
                fill="blue",
            )
        except Exception:
            pass  # Font issues, just use plain gray

    # Save if requested (adding timestamp & ensuring directory)
    if save_to and img:
        save_to = Path(save_to)
        # Create parent directory if it doesn't exist
        save_to.parent.mkdir(parents=True, exist_ok=True)

        # Append timestamp before extension if exactly 'screenshot.png'
        timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        if save_to.stem == "screenshot":
            save_to = save_to.with_name(f"{save_to.stem}_{timestamp}{save_to.suffix}")

        try:
            img.save(save_to)
        except Exception as e:
            print(f"Failed to save screenshot: {e}")

    return img
