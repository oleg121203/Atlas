"""Ollama Provider for Atlas LLM Manager.

This module provides the implementation for interacting with Ollama's local API.
It handles client initialization and chat functionality.
"""

import logging
import requests
from typing import Any, Dict, List, Optional

class OllamaProvider:
    """Manages interactions with Ollama local API."""

    def __init__(self, config_manager):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_manager = config_manager
        self.model = "llama3"

    def is_available(self):
        """Check if Ollama provider is available."""
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=3)
            return response.status_code == 200
        except Exception:
            return False

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, model: Optional[str] = None, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Handle Ollama chat requests via local HTTP API."""
        if not self.is_available():
            raise ValueError("Ollama server is not running or not accessible.")

        model_to_use = model or self.model
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": model_to_use,
            "messages": messages,
            "stream": False
        }
        if max_tokens is not None:
            payload["options"] = {"num_predict": max_tokens}

        if tools:
            self.logger.warning("Tools are not supported in Ollama API")

        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code != 200:
                raise ValueError(f"Ollama API error: {response.status_code} {response.text}")
            data = response.json()
            message = data.get("message", {}).get("content", "")
            return {
                "content": message,
                "tool_calls": None,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        except Exception as e:
            self.logger.error(f"Ollama API error: {e}", exc_info=True)
            return {"content": "", "tool_calls": None, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def get_embedding(self, text: str, model: str = "models/embedding-001") -> List[float]:
        """Embedding generation is not supported by Ollama API by default."""
        self.logger.warning("Embedding generation is not supported by Ollama API")
        return []
