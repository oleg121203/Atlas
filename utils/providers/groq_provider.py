"""Groq Provider for Atlas LLM Manager.

This module provides the implementation for interacting with Groq's API.
It handles API key management, client initialization, and chat functionality.
"""

import logging
from typing import Any, Dict, List, Optional

import requests


class GroqProvider:
    """Manages interactions with Groq API."""

    def __init__(self, config_manager):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_manager = config_manager
        self.api_key = self.config_manager.get_setting("groq_api_key", "")
        self.model = "llama3-8b-8192"

    def is_available(self):
        """Check if Groq provider is available."""
        return self.api_key and self.api_key.startswith("gsk_")

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Handle Groq chat requests via HTTP API."""
        if not self.is_available():
            raise ValueError("Groq API key not found or invalid.")

        model_to_use = model or self.model
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": model_to_use, "messages": messages}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        if tools:
            self.logger.warning("Tools are not supported in Groq API")

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                raise ValueError(
                    f"Groq API error: {response.status_code} {response.text}"
                )
            data = response.json()
            message = data["choices"][0]["message"]
            return {
                "content": message.get("content", ""),
                "tool_calls": message.get("tool_calls"),
                "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
                "total_tokens": data.get("usage", {}).get("total_tokens", 0),
            }
        except Exception as e:
            self.logger.error(f"Groq API error: {e}", exc_info=True)
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
        """Embedding generation is not supported by Groq API."""
        self.logger.warning("Embedding generation is not supported by Groq API")
        return []
