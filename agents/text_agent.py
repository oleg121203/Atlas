"""
Specialized agent for text processing and generation.
"""

from typing import Any, Dict

from agents.base_agent import BaseAgent
from agents.llm_manager import LLMManager


class TextAgent(BaseAgent):
    """Agent for text processing tasks."""

    def __init__(self, llm_manager: LLMManager):
        super().__init__("Text Agent")
        self.llm_manager = llm_manager

    def execute_task(self, prompt: str, context: Dict[str, Any]) -> str:
        self.logger.info(f"Executing text task: Summarizing text of length {len(prompt)}")

        summarization_prompt = f"Please summarize the following text concisely:\n\n---\n{prompt}\n---" 

        try:
            #For now, we use the default provider configured in LLMManager.
            #A more advanced implementation could specify a provider/model.
            summary = self.llm_manager.chat(summarization_prompt)
            self.logger.info("Text summarization successful.")
            return summary
        except Exception as e:
            self.logger.error(f"Failed to summarize text: {e}")
            return f"Error during text summarization: {e}"
