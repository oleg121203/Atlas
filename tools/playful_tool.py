import asyncio
from typing import Any, Dict

from tools.base_tool import BaseTool


class PlayfulTool(BaseTool):
    """
    A tool that gamifies routine tasks or adds creative, playful outputs.
    Example: 'Inbox Zero Challenge' for email cleanup.
    """

    name = "playful_tool"
    description = "Gamifies routine tasks or adds creative, playful outputs."
    capabilities = ["gamify_tasks", "creative_outputs"]
    version = "1.0"

    def __init__(self):
        super().__init__()

    async def run(self, task_type: str = "inbox_cleanup", **kwargs) -> Dict[str, Any]:
        """
        Gamify a routine task. Example: 'Inbox Zero Challenge'.
        Args:
            task_type: The type of task to gamify (default: 'inbox_cleanup')
        Returns:
            Game result or creative output
        """
        self.log_usage("gamify", {"task_type": task_type})
        await asyncio.sleep(1)  # Simulate game logic
        if task_type == "inbox_cleanup":
            return {
                "status": "success",
                "game": "Inbox Zero Challenge",
                "message": "You cleaned your inbox! 🎉",
            }
        else:
            return {"status": "success", "game": "Unknown", "message": "Task gamified!"}
