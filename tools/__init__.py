"""Atlas tools package.

Core automation tools for screen capture, OCR, image recognition,
mouse/keyboard control, clipboard management, and terminal operations.
"""

from .clipboard_tool import (
    ClipboardResult,
    clear_clipboard,
    get_clipboard_image,
    get_clipboard_text,
    set_clipboard_image,
    set_clipboard_text,
)
from .image_recognition_tool import find_object_in_image, find_template_in_image
from .mouse_keyboard_tool import (
    MouseButton,
    MouseKeyboardResult,
    click_at,
    move_mouse,
    press_key,
    type_text,
)
from .ocr_tool import ocr_file, ocr_image
from .screenshot_tool import capture_screen
from .terminal_tool import (
    TerminalResult,
    change_directory,
    execute_command,
    execute_script,
    get_environment,
    kill_process,
)
from .web_browser_tool import open_url

__all__ = [
    #Screenshot
    "capture_screen",
    #OCR
    "ocr_image", "ocr_file",
    #Image recognition
    "find_template_in_image", "find_object_in_image",
    #Mouse & Keyboard
    "MouseButton", "click_at", "move_mouse", "type_text", "press_key", "MouseKeyboardResult",
    #Clipboard
    "get_clipboard_text", "set_clipboard_text", "get_clipboard_image",
    "set_clipboard_image", "clear_clipboard", "ClipboardResult",
    #Terminal
    "execute_command", "execute_script", "get_environment",
    "change_directory", "kill_process", "TerminalResult",
    # Web Browser
    "open_url",
]
