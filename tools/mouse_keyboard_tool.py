"""Mouse and keyboard automation tool for Atlas (macOS).

Provides secure mouse movement, clicking, and keyboard input using PyAutoGUI 
and native macOS Quartz APIs.
"""
from __future__ import annotations

import time
import os
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

#Try to import pyautogui safely for headless environments
try:
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'  #Fallback display
    import pyautogui  #type: ignore
    _PYAUTOGUI_AVAILABLE = True
except Exception as e:
    _PYAUTOGUI_AVAILABLE = False
    print(f"Warning: PyAutoGUI not available for mouse/keyboard: {e}")

try:
    from Quartz import (
        CGEventCreateMouseEvent,
        CGEventPost,
        kCGEventLeftMouseDown,
        kCGEventLeftMouseUp,
        kCGEventRightMouseDown,
        kCGEventRightMouseUp,
        kCGEventMouseMoved,
        kCGHIDEventTap,
    )
    _QUARTZ_AVAILABLE = True
except ImportError:
    _QUARTZ_AVAILABLE = False

from utils.logger import get_logger

logger = get_logger(__name__)

__all__ = ["MouseButton", "click_at", "move_mouse", "type_text", "press_key", "MouseKeyboardResult"]


class MouseButton(Enum):
    """Mouse button enumeration."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


@dataclass
class MouseKeyboardResult:
    """Result object for mouse/keyboard operations."""
    success: bool
    action: str
    coordinates: Optional[Tuple[int, int]] = None
    text_typed: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0


def click_at(x: int, y: int, button: MouseButton = MouseButton.LEFT, 
             duration: float = 0.1) -> MouseKeyboardResult:
    """Click at specific coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate  
        button: Mouse button to click
        duration: Duration between mouse down and up events
        
    Returns:
        MouseKeyboardResult with operation details
    """
    start_time = time.time()
    
    try:
        if _QUARTZ_AVAILABLE:
            #Use native macOS Quartz for better performance
            if button == MouseButton.LEFT:
                down_event = kCGEventLeftMouseDown
                up_event = kCGEventLeftMouseUp
            elif button == MouseButton.RIGHT:
                down_event = kCGEventRightMouseDown
                up_event = kCGEventRightMouseUp
            else:
                #Fallback to PyAutoGUI for middle click
                pyautogui.click(x, y, button=button.value, duration=duration)
                execution_time = time.time() - start_time
                return MouseKeyboardResult(
                    success=True,
                    action=f"click_{button.value}",
                    coordinates=(x, y),
                    execution_time=execution_time
                )
            
            #Create and post mouse events
            mouse_down = CGEventCreateMouseEvent(None, down_event, (x, y), 0)
            mouse_up = CGEventCreateMouseEvent(None, up_event, (x, y), 0)
            
            CGEventPost(kCGHIDEventTap, mouse_down)
            time.sleep(duration)
            CGEventPost(kCGHIDEventTap, mouse_up)
        else:
            #Fallback to PyAutoGUI
            pyautogui.click(x, y, button=button.value, duration=duration)
        
        execution_time = time.time() - start_time
        
        logger.info(f"Clicked {button.value} button at ({x}, {y}) in {execution_time:.3f}s")
        
        return MouseKeyboardResult(
            success=True,
            action=f"click_{button.value}",
            coordinates=(x, y),
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to click at ({x}, {y}): {str(e)}"
        logger.error(error_msg)
        
        return MouseKeyboardResult(
            success=False,
            action=f"click_{button.value}",
            coordinates=(x, y),
            error=error_msg,
            execution_time=execution_time
        )


def move_mouse(x: int, y: int, duration: float = 0.5) -> MouseKeyboardResult:
    """Move mouse to specific coordinates.
    
    Args:
        x: Target X coordinate
        y: Target Y coordinate
        duration: Time to take for the movement
        
    Returns:
        MouseKeyboardResult with operation details
    """
    start_time = time.time()
    
    try:
        if _QUARTZ_AVAILABLE:
            #Use native macOS for smooth movement
            move_event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (x, y), 0)
            CGEventPost(kCGHIDEventTap, move_event)
        else:
            #Fallback to PyAutoGUI
            pyautogui.moveTo(x, y, duration=duration)
        
        execution_time = time.time() - start_time
        
        logger.info(f"Moved mouse to ({x}, {y}) in {execution_time:.3f}s")
        
        return MouseKeyboardResult(
            success=True,
            action="move_mouse",
            coordinates=(x, y),
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to move mouse to ({x}, {y}): {str(e)}"
        logger.error(error_msg)
        
        return MouseKeyboardResult(
            success=False,
            action="move_mouse",
            coordinates=(x, y),
            error=error_msg,
            execution_time=execution_time
        )


def type_text(text: str, interval: float = 0.01) -> MouseKeyboardResult:
    """Type text with specified interval between characters.
    
    Args:
        text: Text to type
        interval: Delay between each character
        
    Returns:
        MouseKeyboardResult with operation details
    """
    start_time = time.time()
    
    try:
        pyautogui.write(text, interval=interval)
        
        execution_time = time.time() - start_time
        
        logger.info(f"Typed text '{text[:50]}...' in {execution_time:.3f}s")
        
        return MouseKeyboardResult(
            success=True,
            action="type_text",
            text_typed=text,
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to type text: {str(e)}"
        logger.error(error_msg)
        
        return MouseKeyboardResult(
            success=False,
            action="type_text",
            text_typed=text,
            error=error_msg,
            execution_time=execution_time
        )


def press_key(key: str, duration: float = 0.1) -> MouseKeyboardResult:
    """Press a specific key.
    
    Args:
        key: Key to press (e.g., 'enter', 'space', 'cmd', 'tab')
        duration: Duration to hold the key
        
    Returns:
        MouseKeyboardResult with operation details
    """
    start_time = time.time()
    
    try:
        pyautogui.press(key)
        
        execution_time = time.time() - start_time
        
        logger.info(f"Pressed key '{key}' in {execution_time:.3f}s")
        
        return MouseKeyboardResult(
            success=True,
            action=f"press_key_{key}",
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to press key '{key}': {str(e)}"
        logger.error(error_msg)
        
        return MouseKeyboardResult(
            success=False,
            action=f"press_key_{key}",
            error=error_msg,
            execution_time=execution_time
        )
