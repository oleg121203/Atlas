import os
import subprocess
from typing import Any, Dict, Optional


def run_automator_or_shortcut(
    workflow_path: Optional[str] = None, shortcut_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Trigger an Automator workflow (.workflow file) or a macOS Shortcut by name.

    Args:
        workflow_path: Path to the Automator .workflow file.
        shortcut_name: Name of the macOS Shortcut to run.
    Returns:
        A dict with 'status', 'output', and 'error' (if any).
    """
    try:
        if workflow_path:
            if not os.path.exists(workflow_path):
                return {
                    "status": "error",
                    "error": f"Workflow not found: {workflow_path}",
                }
            result = subprocess.run(
                ["open", workflow_path], capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return {"status": "success", "output": result.stdout.strip()}
            else:
                return {
                    "status": "error",
                    "error": result.stderr.strip() or result.stdout.strip(),
                }
        elif shortcut_name:
            result = subprocess.run(
                ["shortcuts", "run", shortcut_name],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return {"status": "success", "output": result.stdout.strip()}
            else:
                return {
                    "status": "error",
                    "error": result.stderr.strip() or result.stdout.strip(),
                }
        else:
            return {
                "status": "error",
                "error": "No workflow_path or shortcut_name provided.",
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}
