"""Tracks token usage across all LLM calls."""

import threading
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class TokenUsage:
    """Represents the token usage and response from a single LLM call."""

    response_text: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class TokenTracker:
    """
    A thread-safe class to track token usage for different LLM providers.
    This helps in monitoring costs and staying within API limits.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._total_tokens = 0

    def add_usage(self, token_usage: TokenUsage) -> None:
        """Adds token counts from a new LLM call."""
        with self._lock:
            self._prompt_tokens += token_usage.prompt_tokens
            self._completion_tokens += token_usage.completion_tokens
            self._total_tokens += token_usage.total_tokens

    def get_usage(self) -> TokenUsage:
        """Returns the current token usage statistics."""
        with self._lock:
            return TokenUsage(
                prompt_tokens=self._prompt_tokens,
                completion_tokens=self._completion_tokens,
                total_tokens=self._total_tokens,
            )

    def reset(self) -> None:
        """Resets all token counters to zero."""
        with self._lock:
            self._prompt_tokens = 0
            self._completion_tokens = 0
            self._total_tokens = 0
