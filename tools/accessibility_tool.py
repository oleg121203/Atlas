import subprocess
from typing import Dict, Any, Optional

def accessibility_action(action: str, x: Optional[int] = None, y: Optional[int] = None, key: Optional[str] = None) -> Dict[str, Any]:
    """
    Simulate a mouse click or keystroke on macOS using AppleScript (osascript).

    Args:
        action: 'click' or 'keystroke'.
        x, y: Coordinates for click (if action is 'click').
        key: Key to press (if action is 'keystroke').
    Returns:
        A dict with 'status', 'output', and 'error' (if any).
    """
    try:
        if action == 'click' and x is not None and y is not None:
            script = f'tell application "System Events" to click at {{{x}, {y}}}'
        elif action == 'keystroke' and key:
            script = f'tell application "System Events" to keystroke "{key}"'
        else:
            return {"status": "error", "error": "Invalid arguments for accessibility action."}
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout.strip()}
        else:
            return {"status": "error", "error": result.stderr.strip() or result.stdout.strip()}
    except Exception as e:
        return {"status": "error", "error": str(e)} 