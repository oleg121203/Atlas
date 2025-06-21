"""
Specialized agent for screen analysis and interaction.
"""

from typing import Any, Dict

from agents.base_agent import BaseAgent
from agents.enhanced_memory_manager import MemoryScope, MemoryType
from tools.screenshot_tool import capture_screen


class ScreenAgent(BaseAgent):
    """Handles tasks related to screen capture, OCR, and image recognition."""

    def __init__(self, memory_manager=None):
        super().__init__("Screen Agent")
        self.memory_manager = memory_manager

    def execute_task(self, prompt: str, context: Dict[str, Any]) -> str:
        self.logger.info(f"Executing screen task: '{prompt}'")

        #Simple parsing for now. A real implementation would use LLM-based intent recognition.
        if "capture" in prompt.lower() or "screenshot" in prompt.lower():
            try:
                image = capture_screen()
                #In a real scenario, this image would be passed to another tool or agent.
                #For now, we just confirm it was taken.
                self.logger.info(f"Screen captured successfully. Image size: {image.size}")

                #Store observation in memory if available
                if self.memory_manager:
                    self.memory_manager.add_memory_for_agent(
                        agent_type=MemoryScope.SCREEN_AGENT,
                        memory_type=MemoryType.OBSERVATION,
                        content=f"Screen captured: {image.width}x{image.height} pixels",
                        metadata={"prompt": prompt, "success": True, "dimensions": f"{image.width}x{image.height}"},
                    )

                return f"Screen captured successfully. Image dimensions: {image.width}x{image.height}."
            except Exception as e:
                self.logger.error(f"Failed to capture screen: {e}")

                #Store error in memory if available
                if self.memory_manager:
                    self.memory_manager.add_memory_for_agent(
                        agent_type=MemoryScope.SCREEN_AGENT,
                        memory_type=MemoryType.ERROR,
                        content=f"Screen capture failed: {e!s}",
                        metadata={"prompt": prompt, "success": False, "error": str(e)},
                    )

                return f"Error capturing screen: {e}"

        return f"Unknown screen task: '{prompt}'. Please specify 'capture' or 'screenshot'."
