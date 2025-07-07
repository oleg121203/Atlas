"""OpenAI Provider for Atlas LLM Manager.

This module provides the implementation for interacting with OpenAI's API.
It handles API key management, client initialization, and chat functionality.
"""

import logging
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider:
    """Manages interactions with OpenAI API."""

    def __init__(self, config_manager):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_manager = config_manager
        self.client = None
        self.model = "gpt-4-turbo"
        self._initialize_client()

    def _initialize_client(self):
        """Initializes the OpenAI client using the API key from the config."""
        if not OPENAI_AVAILABLE:
            self.logger.warning(
                "OpenAI library not installed. OpenAI client is not available."
            )
            return

        api_key = self.config_manager.get_openai_api_key()
        if not api_key or not api_key.strip() or "placeholder" in api_key.lower():
            self.logger.warning(
                "OpenAI API key not found or invalid. OpenAI client is not available."
            )
            return

        try:
            self.client = OpenAI(api_key=api_key)
            self.logger.info("OpenAI client initialized successfully.")
        except Exception as e:
            self.client = None
            self.logger.error(f"Failed to initialize OpenAI client: {e}")

    def is_available(self):
        """Check if OpenAI provider is available."""
        return self.client is not None

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Handle OpenAI chat requests."""
        if not self.is_available():
            raise ValueError("OpenAI client is not initialized.")

        model_to_use = model or self.model
        try:
            params = {
                "model": model_to_use,
                "messages": messages,
            }
            if tools:
                params["tools"] = tools
            if max_tokens is not None:
                params["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**params)
            message = response.choices[0].message
            return {
                "content": message.content,
                "tool_calls": message.tool_calls,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}", exc_info=True)
            return {
                "content": "",
                "tool_calls": None,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }

    def get_embedding(
        self, text: str, model: str = "text-embedding-ada-002"
    ) -> List[float]:
        """Generates an embedding for the given text using OpenAI API."""
        if not self.is_available():
            self.logger.error("Cannot generate embedding, OpenAI client not available.")
            return []

        try:
            response = self.client.embeddings.create(input=text, model=model)
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}", exc_info=True)
            return []
