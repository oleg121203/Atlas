import subprocess
from typing import Dict, Any, Optional

def system_event(event: str, value: Optional[Any] = None, app_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Query or trigger common macOS system events using AppleScript or system commands.

    Args:
        event: The event to query or trigger ('sleep', 'wake', 'mute', 'unmute', 'get_volume', 'set_volume', 'open_app', 'get_running_apps').
        value: Value for set_volume (0-100).
        app_name: Name of app to open (for 'open_app').
    Returns:
        A dict with 'status', 'output', and 'error' (if any).
    """
    try:
        if event == 'sleep':
            script = 'tell application "System Events" to sleep'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
        elif event == 'mute':
            script = 'set volume output muted true'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
        elif event == 'unmute':
            script = 'set volume output muted false'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
        elif event == 'get_volume':
            script = 'output volume of (get volume settings)'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
        elif event == 'set_volume' and value is not None:
            script = f'set volume output volume {int(value)}'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
        elif event == 'open_app' and app_name:
            result = subprocess.run(["open", "-a", app_name], capture_output=True, text=True, check=False)
        elif event == 'get_running_apps':
            script = 'tell application "System Events" to get name of (processes where background only is false)'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
        else:
            return {"status": "error", "error": "Invalid event or missing arguments."}
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout.strip()}
        else:
            return {"status": "error", "error": result.stderr.strip() or result.stdout.strip()}
    except Exception as e:
        return {"status": "error", "error": str(e)} 