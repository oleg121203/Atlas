"""Gemini Provider for Atlas LLM Manager.

This module provides the implementation for interacting with Google's Gemini API.
It handles API key management, client initialization, and chat functionality.
"""

import logging
from typing import Any, Dict, List, Optional

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiProvider:
    """Manages interactions with Gemini API."""

    def __init__(self, config_manager):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_manager = config_manager
        self.client = None
        self.model = "gemini-1.5-flash"
        self._initialize_client()

    def _initialize_client(self):
        """Initializes the Gemini client using the API key from the config."""
        if not GEMINI_AVAILABLE:
            self.logger.warning(
                "Gemini library not installed. Gemini client is not available."
            )
            return

        api_key = self.config_manager.get_gemini_api_key()
        if not api_key or not api_key.strip():
            self.logger.warning(
                "Gemini API key not found. Gemini client is not available."
            )
            return

        try:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
            self.logger.info("Gemini client initialized successfully.")
        except Exception as e:
            self.client = None
            self.logger.error(f"Failed to initialize Gemini client: {e}")

    def is_available(self):
        """Check if Gemini provider is available."""
        return self.client is not None

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Handle Gemini chat requests."""
        if not self.is_available():
            raise ValueError("Gemini client is not initialized.")

        model_to_use = model or self.model
        try:
            chat_model = genai.GenerativeModel(model_to_use)
            chat_session = chat_model.start_chat(history=[])

            system_message = next(
                (m for m in messages if m.get("role") == "system"), None
            )
            if system_message:
                chat_session.send_message(system_message.get("content", ""))
                messages = [m for m in messages if m.get("role") != "system"]

            for message in messages:
                message["role"]
                content = message.get("content", "")
                if isinstance(content, str):
                    chat_session.send_message(content)
                elif isinstance(content, list):
                    text_content = next(
                        (c.get("text", "") for c in content if c.get("type") == "text"),
                        "",
                    )
                    chat_session.send_message(text_content)

            if tools:
                self.logger.warning("Tools are not yet supported in Gemini API")

            if max_tokens is not None:
                self.logger.warning(
                    "max_tokens parameter is not supported in Gemini API"
                )

            response = (
                chat_session.history[-1].parts[0].text if chat_session.history else ""
            )
            return {
                "content": response,
                "tool_calls": None,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}", exc_info=True)
            return {
                "content": "",
                "tool_calls": None,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }

    def get_embedding(
        self, text: str, model: str = "models/embedding-001"
    ) -> List[float]:
        """Generates an embedding for the given text."""
        if not self.is_available():
            self.logger.error("Cannot generate embedding, Gemini client not available.")
            return []

        try:
            result = genai.embed_content(model=model, content=text)
            return result["embedding"]
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}", exc_info=True)
            return []
