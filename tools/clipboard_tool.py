"""Clipboard management tool for Atlas (macOS).

Provides cross-platform clipboard operations with macOS native support 
using pyperclip and AppKit APIs.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional

#Try to import pyperclip safely for headless environments
try:
    import pyperclip  #type: ignore
    _PYPERCLIP_AVAILABLE = True
except ImportError:
    _PYPERCLIP_AVAILABLE = False

try:
    from AppKit import NSPasteboard, NSStringPboardType  #type: ignore
    _APPKIT_AVAILABLE = True
except ImportError:
    _APPKIT_AVAILABLE = False

from utils.logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "ClipboardResult",
    "clear_clipboard",
    "get_clipboard_image",
    "get_clipboard_text",
    "set_clipboard_image",
    "set_clipboard_text",
]


@dataclass
class ClipboardResult:
    """Result object for clipboard operations."""
    success: bool
    action: str
    content: Optional[Any] = None
    content_type: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0


def get_clipboard_text() -> ClipboardResult:
    """Get text content from clipboard.
    
    Returns:
        ClipboardResult with text content or error
    """
    start_time = time.time()

    try:
        if not _PYPERCLIP_AVAILABLE and not _APPKIT_AVAILABLE:
            raise RuntimeError("No clipboard access available (missing pyperclip and AppKit)")

        if _APPKIT_AVAILABLE:
            #Use native macOS clipboard
            pasteboard = NSPasteboard.generalPasteboard()
            text = pasteboard.stringForType_(NSStringPboardType)
        elif _PYPERCLIP_AVAILABLE:
            #Fallback to pyperclip
            text = pyperclip.paste()
        else:
            raise RuntimeError("No clipboard access available")

        execution_time = time.time() - start_time

        if text is None:
            text = ""

        logger.info(f"Retrieved {len(text)} characters from clipboard in {execution_time:.3f}s")

        return ClipboardResult(
            success=True,
            action="get_text",
            content=text,
            content_type="text",
            execution_time=execution_time,
        )

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to get clipboard text: {e!s}"
        logger.error(error_msg)

        return ClipboardResult(
            success=False,
            action="get_text",
            error=error_msg,
            execution_time=execution_time,
        )


def set_clipboard_text(text: str) -> ClipboardResult:
    """Set text content to clipboard.
    
    Args:
        text: Text to copy to clipboard
        
    Returns:
        ClipboardResult with operation status
    """
    start_time = time.time()

    try:
        if not _PYPERCLIP_AVAILABLE and not _APPKIT_AVAILABLE:
            raise RuntimeError("No clipboard access available (missing pyperclip and AppKit)")

        if _APPKIT_AVAILABLE:
            #Use native macOS clipboard
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            pasteboard.setString_forType_(text, NSStringPboardType)
        elif _PYPERCLIP_AVAILABLE:
            #Fallback to pyperclip
            pyperclip.copy(text)
        else:
            raise RuntimeError("No clipboard access available")

        execution_time = time.time() - start_time

        logger.info(f"Set {len(text)} characters to clipboard in {execution_time:.3f}s")

        return ClipboardResult(
            success=True,
            action="set_text",
            content=text,
            content_type="text",
            execution_time=execution_time,
        )

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to set clipboard text: {e!s}"
        logger.error(error_msg)

        return ClipboardResult(
            success=False,
            action="set_text",
            content=text,
            error=error_msg,
            execution_time=execution_time,
        )


def get_clipboard_image() -> ClipboardResult:
    """Get image content from clipboard (macOS only).
    
    Returns:
        ClipboardResult with image data or error
    """
    start_time = time.time()

    try:
        if not _APPKIT_AVAILABLE:
            raise NotImplementedError("Image clipboard operations require macOS AppKit")

        pasteboard = NSPasteboard.generalPasteboard()
        image_types = pasteboard.types()

        #Check for image types
        if "public.png" in image_types:
            image_data = pasteboard.dataForType_("public.png")
        elif "public.tiff" in image_types:
            image_data = pasteboard.dataForType_("public.tiff")
        else:
            raise ValueError("No image found in clipboard")

        execution_time = time.time() - start_time

        logger.info(f"Retrieved image from clipboard in {execution_time:.3f}s")

        return ClipboardResult(
            success=True,
            action="get_image",
            content=image_data,
            content_type="image",
            execution_time=execution_time,
        )

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to get clipboard image: {e!s}"
        logger.error(error_msg)

        return ClipboardResult(
            success=False,
            action="get_image",
            error=error_msg,
            execution_time=execution_time,
        )


def set_clipboard_image(image_data: bytes, image_type: str = "png") -> ClipboardResult:
    """Set image content to clipboard (macOS only).
    
    Args:
        image_data: Raw image data bytes
        image_type: Image format ("png" or "tiff")
        
    Returns:
        ClipboardResult with operation status
    """
    start_time = time.time()

    try:
        if not _APPKIT_AVAILABLE:
            raise NotImplementedError("Image clipboard operations require macOS AppKit")

        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()

        #Set appropriate type
        if image_type.lower() == "png":
            pasteboard.setData_forType_(image_data, "public.png")
        elif image_type.lower() == "tiff":
            pasteboard.setData_forType_(image_data, "public.tiff")
        else:
            raise ValueError(f"Unsupported image type: {image_type}")

        execution_time = time.time() - start_time

        logger.info(f"Set image to clipboard in {execution_time:.3f}s")

        return ClipboardResult(
            success=True,
            action="set_image",
            content_type="image",
            execution_time=execution_time,
        )

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to set clipboard image: {e!s}"
        logger.error(error_msg)

        return ClipboardResult(
            success=False,
            action="set_image",
            error=error_msg,
            execution_time=execution_time,
        )


def clear_clipboard() -> ClipboardResult:
    """Clear clipboard contents.
    
    Returns:
        ClipboardResult with operation status
    """
    start_time = time.time()
    try:
        if _PYPERCLIP_AVAILABLE:
            pyperclip.copy('')
            return ClipboardResult(
                success=True,
                action="clear",
                content=None,
                content_type=None,
                error=None,
                execution_time=time.time() - start_time
            )
        else:
            return ClipboardResult(
                success=False,
                action="clear",
                content=None,
                content_type=None,
                error="pyperclip not available",
                execution_time=time.time() - start_time
            )
    except Exception as e:
        return ClipboardResult(
            success=False,
            action="clear",
            content=None,
            content_type=None,
            error=str(e),
            execution_time=time.time() - start_time
        )

def wait_for_clipboard_change(timeout: float = 5.0) -> ClipboardResult:
    """Wait for clipboard content to change.
    
    Args:
        timeout: Maximum time to wait in seconds
        
    Returns:
        ClipboardResult with new clipboard content or error
    """
    start_time = time.time()
    initial_content = get_clipboard_text()
    
    if not initial_content.success:
        return ClipboardResult(
            success=False,
            action="wait_for_change",
            content=None,
            content_type=None,
            error=initial_content.error,
            execution_time=time.time() - start_time
        )
    
    while time.time() - start_time < timeout:
        current_content = get_clipboard_text()
        if current_content.success and current_content.content != initial_content.content:
            return ClipboardResult(
                success=True,
                action="wait_for_change",
                content=current_content.content,
                content_type="text",
                error=None,
                execution_time=time.time() - start_time
            )
        time.sleep(0.1)
    
    return ClipboardResult(
        success=False,
        action="wait_for_change",
        content=None,
        content_type=None,
        error="Timeout waiting for clipboard change",
        execution_time=timeout
    )
