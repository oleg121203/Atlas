#!/usr/bin/env python3
"""
Delay Tool for adding pauses between actions
"""

import asyncio
import logging
from typing import Dict, Any
from .base_tool import BaseTool

class DelayTool(BaseTool):
    """
    Tool for adding controlled delays between actions (async, metadata, chaining).
    """
    name = "delay_tool"
    description = "Adds controlled delays between actions for better execution."
    capabilities = ["wait", "smart_wait", "progressive_wait"]
    version = "2.0"

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def run(self, duration: float = 1.0, **kwargs) -> Dict[str, Any]:
        """
        Async wait for specified duration.
        """
        self.log_usage("wait", {"duration": duration})
        try:
            await asyncio.sleep(duration)
            return {
                "status": "success",
                "message": f"Waited for {duration} seconds",
                "duration": duration,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Delay failed: {str(e)}",
                "duration": duration,
            }

    async def smart_wait(self, action_type: str = "general", **kwargs) -> Dict[str, Any]:
        """
        Smart async wait with duration based on action type.
        """
        delays = {
            "browser": 2.0,
            "search": 1.5,
            "click": 0.5,
            "screenshot": 1.0,
            "general": 1.0
        }
        duration = delays.get(action_type, delays["general"])
        self.log_usage("smart_wait", {"action_type": action_type, "duration": duration})
        return await self.run(duration)

    async def progressive_wait(self, step_number: int = 1, **kwargs) -> Dict[str, Any]:
        """
        Progressive async wait that increases with step number.
        """
        duration = min(1.0 + (step_number - 1) * 0.5, 3.0)
        self.log_usage("progressive_wait", {"step_number": step_number, "duration": duration})
        return await self.run(duration) 