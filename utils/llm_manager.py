"""LLM Manager for Atlas.

This module provides a centralized manager for interacting with Large Language Models (LLMs).
It handles API key management, client initialization, and provides a unified interface
for making chat-based and other types of LLM calls. It also integrates with the
TokenTracker to monitor and log token usage for all API calls.
"""

import logging
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Imports for LLM providers are deferred to improve startup performance.

from agents.token_tracker import TokenTracker, TokenUsage
from utils.config_manager import config_manager as utils_config_manager

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

        self.gemini_client: Optional[Any] = None
        self.default_provider = "gemini"
        
        self.gemini_model = "gemini-1.5-flash"
        self.openai_model = "gpt-4-turbo"
        
        self.current_provider = self.config_manager.get_current_provider() or self.default_provider
        self.current_model = self.config_manager.get_current_model() or self.gemini_model

        self._initialize_clients()

    def _initialize_clients(self):
        """Initializes all available LLM clients."""
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Initializes the Gemini client using the API key from the config."""
        import google.generativeai as genai
        api_key = self.config_manager.get_gemini_api_key()
        if not api_key or not api_key.strip():
            self.logger.warning("Gemini API key not found. Gemini client is not available.")
            self.gemini_client = None
            return

        try:
            genai.configure(api_key=api_key)
            self.gemini_client = genai.GenerativeModel(self.gemini_model)
            self.logger.info("Gemini client initialized successfully.")
        except Exception as e:
            self.gemini_client = None
            self.logger.error(f"Failed to initialize Gemini client: {e}")

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        use_model: Optional[str] = None,
    ) -> TokenUsage:
        """Main method to interact with the LLM."""
        if not messages:
            self.logger.error("Chat messages cannot be empty.")
            raise ValueError("Messages cannot be empty.")

        model_to_use = use_model or self.current_model
        
        if "gpt" in model_to_use.lower():
            provider = "openai"
        elif "gemini" in model_to_use.lower():
            provider = "gemini"
        else:
            provider = self.current_provider
            self.logger.warning(f"Unknown model provider for '{model_to_use}'. Using default: {provider}.")

        cache_key = None
        try:
            cache_key_obj = {"messages": messages, "tools": tools, "model": model_to_use, "provider": provider}
            cache_key = json.dumps(cache_key_obj, sort_keys=True)
            if cache_key in self.cache:
                self.logger.info("Returning cached LLM response.")
                return self.cache[cache_key]
        except TypeError as e:
            self.logger.warning(f"Could not create cache key, bypassing cache: {e}")
            cache_key = None

        try:
            if provider == "openai":
                result = self._chat_openai(messages, tools, model_to_use)
            elif provider == "gemini":
                result = self._chat_gemini(messages, tools, model_to_use)
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
            
            if cache_key:
                self.cache[cache_key] = result
            return result
        except Exception as e:
            self.logger.error(f"Error during LLM chat with provider {provider}: {e}", exc_info=True)
            return TokenUsage(
                response_text=f"Error: {e}",
                tool_calls=None,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            )

    def _chat_openai(self, messages: list[dict], tools: Optional[List[Dict[str, Any]]] = None, model: str = "gpt-4-turbo") -> TokenUsage:
        """Handle OpenAI chat requests."""
        from openai import OpenAI
        api_key = self.config_manager.get_openai_api_key()
        if not api_key or "placeholder" in api_key:
            self.logger.warning("OpenAI API key is invalid or placeholder, falling back to Gemini.")
            return self._chat_gemini(messages, tools, self.gemini_model)

        try:
            openai_client = OpenAI(api_key=api_key)
            kwargs = {"model": model, "messages": messages}
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = openai_client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            usage = response.usage
            
            tool_calls = None
            if message.tool_calls:
                tool_calls = [{"id": tc.id, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in message.tool_calls]

            token_usage = TokenUsage(
                response_text=message.content,
                tool_calls=tool_calls,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            )
            self.token_tracker.add_usage(token_usage)
            return token_usage
        except Exception as e:
            self.logger.error(f"An error occurred during the OpenAI call: {e}", exc_info=True)
            self.logger.info("Falling back to Gemini due to OpenAI API error.")
            return self._chat_gemini(messages, tools, self.gemini_model)

    def _chat_gemini(self, messages: list[dict], tools: Optional[List[Dict[str, Any]]] = None, model: str = "gemini-1.5-flash") -> TokenUsage:
        """Handle Gemini chat requests."""
        import google.generativeai as genai

        if not self.gemini_client:
            self.logger.error("Gemini client not initialized.")
            raise ValueError("Gemini client not initialized. Please set your API key.")

        try:
            if not model or not model.startswith("gemini"):
                model = self.gemini_model
                self.logger.info(f"Using default Gemini model: {model}")

            system_instruction = None
            gemini_messages = []
            for msg in messages:
                role, content = msg.get("role"), msg.get("content")
                if role == "system":
                    system_instruction = content
                    continue
                if content:
                    gemini_role = "model" if role == "assistant" else "user"
                    gemini_messages.append({"role": gemini_role, "parts": [content]})

            model_instance = genai.GenerativeModel(model_name=model, system_instruction=system_instruction, tools=tools)
            
            safety_settings = {'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE', 'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE', 'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE', 'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'}
            
            response = model_instance.generate_content(gemini_messages, safety_settings=safety_settings)

            response_text, tool_calls = "", None
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
                    if hasattr(part, 'function_call'):
                        fc = part.function_call
                        tool_calls = [{"id": f"call_{fc.name}", "function": {"name": fc.name, "arguments": json.dumps(dict(fc.args or {}))}}]

            if not response_text and not tool_calls:
                self.logger.warning(f"Gemini response was empty. Raw response: {response}")

            prompt_tokens = model_instance.count_tokens(gemini_messages).total_tokens
            completion_tokens = model_instance.count_tokens(response.candidates[0].content).total_tokens
            
            token_usage = TokenUsage(
                response_text=response_text,
                tool_calls=tool_calls,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            )
            self.token_tracker.add_usage(token_usage)
            return token_usage
        except Exception as e:
            self.logger.error(f"An error occurred during the Gemini call: {e}", exc_info=True)
            raise

    def get_embedding(self, text: str, model: str = "models/embedding-001") -> List[float]:
        """Generates an embedding for the given text."""
        import google.generativeai as genai
        try:
            # Ensure client is configured
            if self.gemini_client is None and self.config_manager.get_gemini_api_key():
                self._initialize_gemini()

            if self.gemini_client is None:
                self.logger.error("Cannot generate embedding, Gemini client not available.")
                return []

            result = genai.embed_content(model=model, content=text)
            return result['embedding']
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}", exc_info=True)
            return []
