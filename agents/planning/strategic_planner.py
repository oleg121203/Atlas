"""
Defines the Strategic Planner for decomposing high-level goals into strategic objectives.
"""
import re
from typing import List

from agents.enhanced_memory_manager import EnhancedMemoryManager
from utils.llm_manager import LLMManager
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
        """Constructs the system prompt for the strategic planning LLM, incorporating Chain-of-Thought."""
        return """
You are the Strategic Planner for an autonomous agent named Atlas.
Your role is to decompose a high-level, abstract user goal into a concise list of concrete, actionable strategic objectives.

**Process:**
1.  **Think Step-by-Step:** First, reason about the user's goal inside `<thinking>` XML tags. Analyze the request, consider potential ambiguities, identify key components, and outline a logical flow. This is your scratchpad.
2.  **Generate the Plan:** After your reasoning, provide the final plan. The plan should be a concise, numbered list of strategic objectives.

**Mandate for the Final Plan:**
- The plan must be a sequence of 3-5 strategic objectives.
- Each objective must be a clear, high-level step that moves towards completing the overall goal.
- Output ONLY the `<thinking>` block followed by the numbered list. Do not add any other preamble or commentary.

**Example:**
User Goal: "Refactor the authentication system to improve security."

Your Output:
<thinking>
The user wants to refactor the auth system for better security. This is a common but critical task.
1.  **Assess:** I need to understand the current system first. What are its weaknesses? An audit is the logical first step.
2.  **Research:** I shouldn't just patch the old system. A modern, well-vetted library is probably better. I need to find one that fits the current tech stack.
3.  **Implement:** This is the core development work. I'll need to replace the old code with the new library.
4.  **Verify:** Security-related changes must be thoroughly tested. This includes unit, integration, and maybe even some penetration testing.
5.  **Deploy & Monitor:** After deployment, I need to watch for any issues, like login failures or performance problems.
This sequence covers the full lifecycle of a secure refactoring project.
</thinking>
1. Audit the existing authentication system for vulnerabilities.
2. Research and select a modern, secure authentication library that fits the project's tech stack.
3. Implement the new authentication library, replacing the old system.
4. Write comprehensive tests for the new authentication flow, including security checks.
5. Deploy the new system and monitor for issues.
"""

    def generate_strategic_plan(self, high_level_goal: str) -> List[str]:
        """
        Takes a high-level goal and breaks it down into a list of strategic objectives
        using Chain-of-Thought reasoning.
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

            # Extract and log the Chain-of-Thought reasoning
            thinking_match = re.search(r"<thinking>(.*?)</thinking>", response_text, re.DOTALL)
            if thinking_match:
                thinking_process = thinking_match.group(1).strip()
                self.logger.info(f"LLM Chain-of-Thought reasoning:\n---\n{thinking_process}\n---")
            else:
                self.logger.warning("LLM response did not contain a <thinking> block as per the prompt.")

            # Parse the numbered list from the response. This is robust to the thinking block's presence.
            objectives = re.findall(r"^\d+\.\s*(.*)", response_text, re.MULTILINE)

            if not objectives:
                self.logger.warning("Could not parse numbered list from LLM response. Falling back to manual parsing.")
                lines = [line.strip() for line in response_text.strip().split("\n") if line.strip()]
                if lines and lines[0].endswith(":"):
                    objectives = lines[1:]
                else:
                    objectives = lines
                # Filter out any empty strings that might result
                objectives = [obj for obj in objectives if obj]

            if objectives:
                self.logger.info(f"Generated {len(objectives)} strategic objectives.")
            else:
                self.logger.error("Failed to extract any strategic objectives from the LLM response.")

            return objectives

        except Exception as e:
            self.logger.error(f"Strategic plan generation failed: {e}", exc_info=True)
            return []
