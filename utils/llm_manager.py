"""LLM Manager for Atlas.

This module provides a centralized manager for interacting with Large Language Models (LLMs).
It handles API key management, client initialization, and provides a unified interface
for making chat-based and other types of LLM calls. It also integrates with the
TokenTracker to monitor and log token usage for all API calls.
"""

import logging
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Union

# Imports for LLM providers are deferred to improve startup performance.

from modules.agents.token_tracker import TokenTracker, TokenUsage
from utils.config_manager import config_manager as utils_config_manager

# Import provider-specific modules
from utils.providers.openai_provider import OpenAIProvider
from utils.providers.gemini_provider import GeminiProvider
from utils.providers.groq_provider import GroqProvider
from utils.providers.ollama_provider import OllamaProvider

# Define a protocol for provider classes to ensure type safety
class LLMProvider(Protocol):
    def is_available(self) -> bool:
        ...
    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, model: Optional[str] = None, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        ...
    def get_embedding(self, text: str, model: str = "models/embedding-001") -> List[float]:
        ...

# ---------------------------------------------------------------------------
# Legacy compatibility shim
# ---------------------------------------------------------------------------
# Some older tests expect a dataclass named `LLMResponse` to be available from
# `utils.llm_manager`.  The production code has migrated to using the
# `TokenUsage` dataclass defined in `agents.token_tracker`.  To avoid touching
# numerous test files, we provide a thin wrapper that mirrors the original
# interface (plus a `model` field) while having no runtime impact.

@dataclass
class LLMResponse:  # noqa: D101
    response_text: Optional[str] = None
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0



class LLMManager:
    """Manages interactions with multiple Language Model providers."""

    def __init__(self, token_tracker: TokenTracker, config_manager=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.token_tracker = token_tracker
        self.cache: Dict[str, TokenUsage] = {}

        self.config_manager = config_manager or utils_config_manager

        self.default_provider = "gemini"
        
        self.gemini_model = "gemini-1.5-flash"
        self.openai_model = "gpt-4-turbo"
        
        self.current_provider = self.config_manager.get_current_provider() or self.default_provider
        self.current_model = self.config_manager.get_current_model() or self.gemini_model

        # Initialize provider-specific clients
        self.providers: Dict[str, Union[OpenAIProvider, GeminiProvider, GroqProvider, OllamaProvider]] = {
            "openai": OpenAIProvider(self.config_manager),
            "gemini": GeminiProvider(self.config_manager),
            "groq": GroqProvider(self.config_manager),
            "ollama": OllamaProvider(self.config_manager)
        }

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        use_model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> TokenUsage:
        """
        Send a chat request to the LLM provider.
        
        Args:
            messages: List of message dictionaries
            tools: Optional list of tool definitions
            use_model: Optional model to use (overrides current model)
            max_tokens: Optional maximum tokens for response
            
        Returns:
            TokenUsage object with response and token counts
        """
        provider = self.current_provider
        model_to_use = use_model or self.current_model

        if not model_to_use:
            self.logger.warning(f"Unknown model provider for '{model_to_use}'. Using default: {provider}.")

        cache_key = None
        try:
            # Check cache first for non-conversational queries
            if len(messages) == 1 and messages[0].get("role") == "user":
                cache_key = json.dumps(messages[0])
                if cache_key in self.cache:
                    self.logger.info(f"Cache hit for request: {cache_key[:50]}...")
                    return self.cache[cache_key]

            # Route the request to the appropriate provider
            if provider not in self.providers:
                self.logger.error(f"Unsupported provider: {provider}")
                return self._fallback_to_available_provider(messages, tools, model_to_use, max_tokens)

            if not self.providers[provider].is_available():
                self.logger.error(f"Provider {provider} is not available. Attempting fallback.")
                return self._fallback_to_available_provider(messages, tools, model_to_use, max_tokens)

            response_data = self.providers[provider].chat(messages, tools, model_to_use, max_tokens)
            token_usage = TokenUsage(
                response_text=response_data.get("content", ""),
                tool_calls=response_data.get("tool_calls"),
                prompt_tokens=response_data.get("prompt_tokens", 0),
                completion_tokens=response_data.get("completion_tokens", 0),
                total_tokens=response_data.get("total_tokens", 0),
            )
            self.token_tracker.add_usage(token_usage)

            if cache_key:
                self.cache[cache_key] = token_usage
                self.logger.info(f"Cached response for request: {cache_key[:50]}...")

            return token_usage
        except Exception as e:
            self.logger.error(f"LLM API error with {provider}: {e}", exc_info=True)
            return self._fallback_to_available_provider(messages, tools, model_to_use, max_tokens)

    def _fallback_to_available_provider(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> TokenUsage:
        """Attempt to fallback to another available provider if the current one fails."""
        self.logger.info("Attempting to fallback to another available provider.")
        fallback_providers = [p for p in self.providers.keys() if p != self.current_provider]
        for provider in fallback_providers:
            if provider in self.providers and self.providers[provider].is_available():
                self.logger.info(f"Falling back to provider: {provider}")
                try:
                    response_data = self.providers[provider].chat(messages, tools, model, max_tokens)
                    token_usage = TokenUsage(
                        response_text=response_data.get("content", ""),
                        tool_calls=response_data.get("tool_calls"),
                        prompt_tokens=response_data.get("prompt_tokens", 0),
                        completion_tokens=response_data.get("completion_tokens", 0),
                        total_tokens=response_data.get("total_tokens", 0),
                    )
                    self.token_tracker.add_usage(token_usage)
                    # Update current provider to the one that worked
                    self.current_provider = provider
                    self.logger.info(f"Successfully fell back to provider: {provider}")
                    return token_usage
                except Exception as e:
                    self.logger.error(f"Fallback to {provider} failed: {e}", exc_info=True)
                    continue
        self.logger.error("No providers available after fallback attempts.")
        return TokenUsage()

    def get_embedding(self, text: str, model: str = "models/embedding-001") -> List[float]:
        """Generates an embedding for the given text."""
        provider = "gemini"  # Default to Gemini for embeddings
        if provider not in self.providers:
            self.logger.error(f"Provider {provider} not found for embedding generation.")
            return []

        provider_instance = self.providers[provider]
        if not hasattr(provider_instance, 'get_embedding'):
            self.logger.error(f"Provider {provider} does not support embedding generation.")
            return []

        if not provider_instance.is_available():
            self.logger.error(f"Cannot generate embedding, {provider} client not available.")
            return []

        return provider_instance.get_embedding(text, model)

    def update_settings(self):
        """Update LLM manager settings from config."""
        try:
            # Update current model and provider based on configuration
            new_model = self.config_manager.get_current_model()
            new_provider = self.config_manager.get_current_provider()
            
            # Check if settings actually changed
            settings_changed = False
            
            if new_model != self.current_model:
                self.current_model = new_model
                self.logger.info(f"Updated current model to: {new_model}")
                settings_changed = True
            
            if new_provider != self.current_provider:
                self.current_provider = new_provider
                self.logger.info(f"Updated current provider to: {new_provider}")
                settings_changed = True
            
            # Re-initialize providers if settings changed
            if settings_changed:
                self.providers = {
                    "openai": OpenAIProvider(self.config_manager),
                    "gemini": GeminiProvider(self.config_manager),
                    "groq": GroqProvider(self.config_manager),
                    "ollama": OllamaProvider(self.config_manager)
                }
                self.logger.info("Re-initialized LLM providers with new settings")
                
            self.logger.debug("LLM settings updated successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update LLM settings: {e}", exc_info=True)
            return False

    def is_provider_available(self, provider: str) -> bool:
        """Check if a specific LLM provider is available."""
        if provider in self.providers:
            return self.providers[provider].is_available()
        return False
