"""Ollama backend wrapper using the REST API."""
from __future__ import annotations

from typing import List

import requests

from utils.llm_manager import LLMResponse
from utils.logger import get_logger

logger = get_logger(__name__)

class OllamaBackend:
    """Calls the local Ollama server via its REST API."""

    def __init__(self, model: str, host: str = "http://localhost:11434"):
        self.model = model
        self.api_url = f"{host}/api/chat"

    def chat(self, messages: List[dict[str, str]], **kwargs) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,  #Required to get full response with stats
        }
        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            prompt_tokens = data.get("prompt_eval_count", 0)
            completion_tokens = data.get("eval_count", 0)

            return LLMResponse(
                response_text=data.get("message", {}).get("content", ""),
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            )
        except requests.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            raise RuntimeError(f"Failed to connect to Ollama API: {e}") from e
