"""
Defines the Tactical Planner for breaking down strategic objectives into concrete plans.
"""
import json
import re
from typing import List, Dict, Any, Optional

from utils.llm_manager import LLMManager
from agents.enhanced_memory_manager import EnhancedMemoryManager
from utils.logger import get_logger

class TacticalPlanner:
    """
    Breaks down a strategic objective into a concrete, multi-step tactical plan.
    """

    def __init__(self, llm_manager: LLMManager, memory_manager: EnhancedMemoryManager):
        """
        Initializes the TacticalPlanner.

        Args:
            llm_manager: The language model manager for API calls.
            memory_manager: The memory manager for context retrieval.
        """
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.logger = get_logger(self.__class__.__name__)

    def _get_system_prompt(self) -> str:
        """Constructs the system prompt for the tactical planning LLM."""
        return """
You are the Tactical Planner for an autonomous agent named Atlas.
Your role is to take a single strategic objective and break it down into a detailed, multi-step tactical plan.
This tactical plan will be passed to an operational planner that will convert each step into executable tool commands.

**Mandate:**
- Analyze the strategic objective.
- Create a JSON object describing the tactical plan.
- The JSON object must have a "steps" key, which is a list of step objects.
- Each step object in the list must have two keys:
    1. "sub_goal": A concise, imperative command for the operational planner (e.g., "Analyze the project's dependencies.").
    2. "description": A user-friendly sentence describing the purpose of the step (e.g., "I will analyze the project's dependencies to identify potential conflicts.").
- The plan should be logical, efficient, and cover all necessary actions to achieve the objective.
- Output ONLY the raw JSON object. Do not add any preamble, commentary, or markdown code fences.

**Example:**
Strategic Objective: "Audit the existing authentication system for vulnerabilities."

Your Output:
{
    "steps": [
        {
            "sub_goal": "List all files related to the authentication system.",
            "description": "I will list all files related to the authentication system to understand its architecture."
        },
        {
            "sub_goal": "Read the contents of each authentication file.",
            "description": "I will read the contents of each file to identify potential security flaws."
        },
        {
            "sub_goal": "Summarize the identified vulnerabilities.",
            "description": "I will summarize the findings and report on potential vulnerabilities."
        }
    ]
}
"""

    def _extract_json_from_response(self, response_str: str) -> Optional[str]:
        """Extracts a JSON object from the LLM's raw response string."""
        match = re.search(r'\{.*\}', response_str, re.DOTALL)
        if match:
            return match.group(0)
        self.logger.warning("Could not find a JSON object in the LLM response.")
        return None

    def generate_tactical_plan(self, strategic_objective: str) -> Dict[str, Any]:
        """
        Takes a strategic objective and creates a JSON tactical plan.

        Args:
            strategic_objective: A clear, high-level objective.

        Returns:
            A dictionary representing the JSON tactical plan, or an empty dictionary on failure.
        """
        self.logger.info(f"Generating tactical plan for strategic objective: '{strategic_objective}'")
        system_prompt = self._get_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": strategic_objective},
        ]

        try:
            llm_result = self.llm_manager.chat(messages)
            if not llm_result or not llm_result.response_text:
                self.logger.error("LLM returned no content for tactical plan generation.")
                return {}

            response_text = llm_result.response_text
            self.logger.debug(f"LLM raw response for tactical plan: {response_text}")

            json_str = self._extract_json_from_response(response_text)
            if not json_str:
                self.logger.error(f"Could not extract JSON from LLM response: {response_text}")
                return {}

            plan = json.loads(json_str)
            return plan

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON from LLM response: {e}", exc_info=True)
            return {}
        except Exception as e:
            self.logger.error(f"Tactical plan generation failed: {e}", exc_info=True)
            return {}
