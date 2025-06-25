"""
Defines the Operational Planner for translating tactical steps into executable commands.
"""

import json
import re
from typing import Any, Dict, Optional

from agents.agent_manager import AgentManager
from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryScope, MemoryType
from utils.llm_manager import LLMManager
from utils.logger import get_logger


class OperationalPlanner:
    """
    Translates a single tactical step into a detailed, executable JSON plan.
    This class now encapsulates the core planning logic from the MasterAgent.
    """
    def __init__(self, llm_manager: LLMManager, memory_manager: EnhancedMemoryManager, agent_manager: AgentManager):
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.agent_manager = agent_manager
        self.logger = get_logger()

    def generate_operational_plan(self, goal: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Takes a tactical goal and generates a JSON plan of tool commands using Chain-of-Thought.
        If 'preferred_tool' is present in context and valid, instruct the LLM to use it as the first step.
        """
        preferred_tool = context.get('preferred_tool')
        preferred_tool_instruction = ""
        if preferred_tool and self.agent_manager:
            if preferred_tool in self.agent_manager.get_tool_names():
                preferred_tool_instruction = (
                    f"\n**MANDATE:** The first step of your plan MUST use the tool '{preferred_tool}' if at all possible. "
                    f"If it is not possible, explain why in your <thinking> block."
                )
                self.logger.info(f"[OperationalPlanner] Injected preferred_tool '{preferred_tool}' into planning prompt.")
        
        # Feedback memories (from MASTER_AGENT, FEEDBACK)
        feedback_memories = self.memory_manager.search_memories_for_agent(
            agent_type=MemoryScope.MASTER_AGENT,
            memory_type=MemoryType.FEEDBACK,
            query=f"feedback related to goal: {goal}",
            n_results=5
        )
        # Knowledge memories (from SYSTEM_KNOWLEDGE)
        knowledge_memories = self.memory_manager.search_memories(
            query=f"general knowledge for: {goal}",
            collection_names=[MemoryScope.SYSTEM_KNOWLEDGE.value],
            n_results=5
        )

        system_prompt = self._get_planning_prompt(goal, feedback_memories, knowledge_memories, context)
        if preferred_tool_instruction:
            system_prompt += preferred_tool_instruction
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": goal}]

        try:
            llm_result = self.llm_manager.chat(messages)
            if not llm_result or not llm_result.response_text:
                self.logger.error("LLM returned no content for plan generation.")
                return None

            response_str = llm_result.response_text
            self.logger.debug(f"LLM raw response for plan: {response_str}")

            # Extract and log the Chain-of-Thought reasoning
            thinking_match = re.search(r"<thinking>(.*?)</thinking>", response_str, re.DOTALL)
            if thinking_match:
                thinking_process = thinking_match.group(1).strip()
                self.logger.info(f"LLM Chain-of-Thought reasoning:\n---\n{thinking_process}\n---")
            else:
                self.logger.warning("LLM response did not contain a <thinking> block as per the prompt.")

            json_str = self._extract_json_from_response(response_str)
            if not json_str:
                self.logger.error(f"Could not extract JSON from LLM response: {response_str}")
                return None

            plan = json.loads(json_str)
            return plan
        except Exception as e:
            self.logger.error(f"Plan generation failed: {e}", exc_info=True)
            return None

    def _get_planning_prompt(self, goal: str, feedback: list, knowledge: list, context: Dict[str, Any]) -> str:
        """Constructs the system prompt for the planning LLM, incorporating Chain-of-Thought."""
        tools_string = self.agent_manager.get_tool_list_string() if self.agent_manager else ""

        feedback_context = "No feedback from past attempts."
        if feedback:
            feedback_items = [f"- {mem.get('content', 'N/A')}" for mem in feedback]
            if feedback_items:
                feedback_context = "\n".join(feedback_items)

        general_context = "No relevant general knowledge found."
        if knowledge:
            knowledge_items = [f"- (From collection: {mem.get('collection', 'general')}) {mem.get('content', 'N/A')}" for mem in knowledge]
            if knowledge_items:
                general_context = "\n".join(knowledge_items)

        context_str = json.dumps(context, indent=2)
        prompt = f"""
        You are the planning module for an autonomous agent named Atlas.
        Your task is to create a detailed, step-by-step JSON plan to achieve a given goal.

        **Process:**
        1.  **Think Step-by-Step:** First, reason about the goal inside `<thinking>` XML tags. Analyze the goal, available tools, context, and past feedback. Formulate a robust sequence of tool calls.
        2.  **Generate the Plan:** After your reasoning, provide the final plan as a single JSON object.

        Available Tools:
        {tools_string}

        **Current Context:**
        {context_str}

        **Critique of Past Attempts (Learn from these!):**
        {feedback_context}

        **Relevant General Knowledge:**
        {general_context}

        **Mandate for the Final JSON Plan:**
        - The plan must be a JSON object with two keys: "description" and "steps".
        - "description" should be a brief, user-friendly summary of the plan.
        - "steps" must be a list of JSON objects, where each object represents a single step.
        - Each step object must have "tool_name" and "arguments".
        - "tool_name" must be one of the available tools.
        - "arguments" must be a JSON object of key-value pairs for the tool's parameters.
        - Use the special syntax `{{{{step_N.output}}}}` to reference the output of a previous step (e.g., `{{{{step_1.output}}}}`).
        - If past attempts FAILED, your new plan MUST propose a different sequence of actions or use different arguments to avoid repeating the same mistakes.

        Output ONLY the `<thinking>` block followed by the raw JSON object. Do not add any other preamble or markdown code fences.
        """
        return prompt

    def _extract_json_from_response(self, text: str) -> Optional[str]:
        """Extracts a JSON object or array from a string, even if it's in a markdown block."""
        # Regex to find JSON in markdown ```json ... ``` blocks or as a raw object
        match = re.search(r"```json\n(.*?)\n```|({.*})|(\[.*\])", text, re.DOTALL)
        if match:
            # Prioritize the markdown block, then raw object, then raw array
            return match.group(1) or match.group(2) or match.group(3)
        return None
