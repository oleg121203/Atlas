"""
Defines the Strategic Planner for decomposing high-level goals into strategic objectives.
"""
import re
from typing import List

from utils.llm_manager import LLMManager
from agents.enhanced_memory_manager import EnhancedMemoryManager
from utils.logger import get_logger


class StrategicPlanner:
    """
    Decomposes a high-level, abstract goal into a sequence of strategic objectives.
    """

    def __init__(self, llm_manager: LLMManager, memory_manager: EnhancedMemoryManager):
        """
        Initializes the StrategicPlanner.

        Args:
            llm_manager: The language model manager for API calls.
            memory_manager: The memory manager for context retrieval (currently unused but planned).
        """
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.logger = get_logger(self.__class__.__name__)

    def _get_system_prompt(self) -> str:
        """Constructs the system prompt for the strategic planning LLM."""
        return """
You are the Strategic Planner for an autonomous agent named Atlas.
Your role is to decompose a high-level, abstract user goal into a concise list of concrete, actionable strategic objectives.
Each objective should be a clear, high-level step that moves towards completing the overall goal.

**Mandate:**
- Analyze the user's goal.
- Break it down into a sequence of 3-5 strategic objectives.
- The objectives should be logical and sequential.
- Output ONLY the objectives as a numbered list. Do not add any preamble, commentary, or other text.

**Example:**
User Goal: "Refactor the authentication system to improve security."

Your Output:
1. Audit the existing authentication system for vulnerabilities.
2. Research and select a modern, secure authentication library.
3. Implement the new authentication library, replacing the old system.
4. Write comprehensive tests for the new authentication flow.
5. Deploy the new system and monitor for issues.
"""

    def generate_strategic_plan(self, high_level_goal: str) -> List[str]:
        """
        Takes a high-level goal and breaks it down into a list of strategic objectives.

        Args:
            high_level_goal: The abstract goal from the user.

        Returns:
            A list of strings, where each string is a strategic objective.
        """
        self.logger.info(f"Generating strategic plan for high-level goal: '{high_level_goal}'")
        system_prompt = self._get_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": high_level_goal},
        ]

        try:
            llm_result = self.llm_manager.chat(messages)
            if not llm_result or not llm_result.response_text:
                self.logger.error("LLM returned no content for strategic plan generation.")
                return []

            response_text = llm_result.response_text
            self.logger.debug(f"LLM raw response for strategic plan: {response_text}")

            # Parse the numbered list from the response
            objectives = re.findall(r"^\d+\.\s*(.*)", response_text, re.MULTILINE)

            if not objectives:
                self.logger.warning("Could not parse objectives from LLM response. Falling back to newline splitting.")
                objectives = [line.strip() for line in response_text.split('\n') if line.strip() and not line.lower().startswith("your output")]

            self.logger.info(f"Generated {len(objectives)} strategic objectives.")
            return objectives

        except Exception as e:
            self.logger.error(f"Strategic plan generation failed: {e}", exc_info=True)
            return []
