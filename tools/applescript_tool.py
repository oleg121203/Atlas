import subprocess
from typing import Any, Dict


def run_applescript(script: str) -> Dict[str, Any]:
    """
    Run an AppleScript command on macOS using osascript.

    Args:
        script: The AppleScript code to execute.
    Returns:
        A dict with 'status', 'output', and 'error' (if any).
    """
    try:
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout.strip()}
        else:
            return {
                "status": "error",
                "error": result.stderr.strip() or result.stdout.strip(),
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}
