"""LLM Manager for Atlas.

This module provides a centralized manager for interacting with Large Language Models (LLMs).
It handles API key management, client initialization, and provides a unified interface
for making chat-based and other types of LLM calls. It also integrates with the
TokenTracker to monitor and log token usage for all API calls.
"""

import logging
import requests
import json
from typing import List, Dict, Any, Optional

from openai import OpenAI, APIError
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from agents.token_tracker import TokenTracker, TokenUsage
from utils.config_manager import config_manager as utils_config_manager
from typing import Optional


class LLMManager:
    """Manages interactions with multiple Language Model providers."""

    def __init__(self, token_tracker: TokenTracker, config_manager=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.token_tracker = token_tracker
        
        # Use provided config manager or fall back to utils config manager
        self.config_manager = config_manager or utils_config_manager
        
        # Initialize clients for different providers
        self.openai_client: Optional[OpenAI] = None
        self.gemini_client: Optional[Any] = None
        self.current_provider = "openai"  # Default provider
        self.current_model = "gpt-3.5-turbo"  # Default model
        
        # Add missing model attributes
        self.gemini_model = "gemini-1.5-flash"
        self.openai_model = "gpt-4-turbo"
        self.anthropic_model = "claude-3-sonnet-20240229"
        self.groq_model = "llama3-8b-8192"
        
        self._initialize_clients()

    def _initialize_clients(self):
        """Initializes all available LLM clients."""
        self._initialize_openai()
        self._initialize_gemini()
        
        # Set current provider from config after initialization
        configured_provider = self.config_manager.get_current_provider()
        if configured_provider:
            self.current_provider = configured_provider.lower()
            self.logger.info(f"Set current provider to: {self.current_provider} (from config)")
        
    def _initialize_openai(self):
        """Initializes the OpenAI client using the API key from the config."""
        api_key = self.config_manager.get_openai_api_key()
        if not api_key or api_key.strip() == "":
            self.logger.warning("OpenAI API key not found in config. OpenAI client is not available.")
            return
        
        # Додаткова перевірка на тестові ключі
        if (api_key.startswith("test_") or 
            api_key.startswith("sk-test") or 
            api_key in ["111", "test", "demo", "example"] or
            len(api_key) < 10):
            self.logger.warning("Test OpenAI API key detected. OpenAI client is not available.")
            return
            
        try:
            self.openai_client = OpenAI(api_key=api_key)
            self.openai_client.models.list()
            self.logger.info("OpenAI API key is valid and client is initialized.")
        except APIError as e:
            self.openai_client = None
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            
    def _initialize_gemini(self):
        """Initializes the Gemini client using the API key from the config."""
        api_key = self.config_manager.get_gemini_api_key()
        if not api_key or api_key.strip() == "":
            self.logger.warning("Gemini API key not found in config. Gemini client is not available.")
            return
            
        # Додаткова перевірка на тестові ключі
        if api_key.startswith("test_") or "test" in api_key.lower():
            self.logger.warning("Test Gemini API key detected. Gemini client is not available.")
            return
            
        try:
            genai.configure(api_key=api_key)
            self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
            self.logger.info("Gemini API key is valid and client is initialized.")
        except Exception as e:
            self.gemini_client = None
            self.logger.error(f"Failed to initialize Gemini client: {e}")

    def set_provider_and_model(self, provider: str, model: str):
        """Set the current provider and model."""
        self.current_provider = provider.lower()
        self.current_model = model
        self.logger.info(f"LLM provider set to {provider} with model {model}")

    def update_settings(self):
        """Re-initializes all LLM clients based on the current configuration."""
        self.logger.info("Updating LLMManager settings by re-initializing clients...")
        self._initialize_clients()

    def get_available_providers(self) -> Dict[str, List[str]]:
        """Returns available providers and their models."""
        providers = {}
        
        # OpenAI models
        if self.openai_client:
            providers["openai"] = [
                "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4",
                "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
            ]
            
        # Gemini models
        if self.gemini_client:
            providers["gemini"] = [
                "gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"
            ]
            
        # Ollama models (local)
        providers["ollama"] = [
            "llama3.2", "llama3.1", "mistral", "codellama", "phi3", "qwen2", "llama2"
        ]
        
        # Groq models (if API key is available)
        if self.config_manager.get_setting('groq_api_key'):
            providers["groq"] = [
                "llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768",
                "gemma-7b-it", "whisper-large-v3"
            ]
        
        # Mistral models (if API key is available)
        if self.config_manager.get_setting('mistral_api_key'):
            providers["mistral"] = [
                "mistral-tiny", "mistral-small", "mistral-medium", "mistral-large-latest",
                "open-mistral-7b", "open-mixtral-8x7b", "open-mixtral-8x22b"
            ]
        
        return providers

    def chat(
        self,
        messages: list[dict],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> TokenUsage:
        """
        Sends a chat request to the specified LLM provider and returns the response.

        Args:
            messages: A list of message dictionaries, e.g., [{"role": "user", "content": "Hello"}].
            tools: Optional list of tools for function calling.
            model: Optional model name to override the current model.
            provider: Optional provider name to override the current provider.

        Returns:
            A TokenUsage object containing the response and token counts, or None on failure.
        """
        # Use provided parameters or fall back to current settings
        use_provider = provider or self.current_provider
        use_model = model or self.current_model
        
        # Route to appropriate provider
        if use_provider == "openai":
            return self._chat_openai(messages, tools, use_model)
        elif use_provider == "gemini":
            return self._chat_gemini(messages, tools, use_model)
        elif use_provider == "ollama":
            return self._chat_ollama(messages, tools, use_model)
        elif use_provider == "groq":
            return self._chat_groq(messages, tools, use_model)
        elif use_provider == "mistral":
            return self._chat_mistral(messages, tools, use_model)
        else:
            self.logger.error(f"Unsupported provider: {use_provider}")
            raise ValueError(f"Unsupported provider: {use_provider}")

    def _chat_openai(self, messages: list[dict], tools: Optional[List[Dict[str, Any]]] = None, model: str = "gpt-3.5-turbo") -> TokenUsage:
        """Handle OpenAI chat requests."""
        if not self.openai_client:
            self.logger.error("OpenAI client not initialized. Cannot make chat request.")
            raise APIError("OpenAI client not initialized. Please set your API key in config.", response=None, body=None)

        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self.openai_client.chat.completions.create(**kwargs)

            message = response.choices[0].message
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            tool_calls = [
                {
                    "id": tool_call.id,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in message.tool_calls
            ] if message.tool_calls else None

            token_usage = TokenUsage(
                response_text=message.content,
                tool_calls=tool_calls,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )

            self.token_tracker.add_usage(token_usage)
            return token_usage

        except Exception as e:
            self.logger.error(f"An error occurred during the OpenAI call: {e}", exc_info=True)
            raise

    def _chat_gemini(self, messages: list[dict], tools: Optional[List[Dict[str, Any]]] = None, model: str = "gemini-1.5-flash") -> TokenUsage:
        """Handle Gemini chat requests."""
        if not self.gemini_client:
            self.logger.error("Gemini client not initialized. Cannot make chat request.")
            raise ValueError("Gemini client not initialized. Please set your API key in config.")

        try:
            # Fix: Ensure we use valid Gemini models only
            if model and model.startswith('gpt'):
                # If someone tries to use GPT model with Gemini, use default Gemini model
                original_model = model
                model = self.gemini_model or 'gemini-1.5-flash'
                self.logger.warning(f"⚠️  Switching from GPT model '{original_model}' to Gemini model: {model}")
            
            # Ensure we have a valid Gemini model
            if not model or not model.startswith('gemini'):
                model = 'gemini-1.5-flash'
                self.logger.info(f"Using default Gemini model: {model}")

            # Convert OpenAI format messages to Gemini format
            if len(messages) == 1 and messages[0]["role"] == "user":
                prompt = messages[0]["content"]
            else:
                # For multi-turn conversations, combine messages
                prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

            # Create generative model with specified model name
            try:
                import google.generativeai as genai
                model_instance = genai.GenerativeModel(model)
                response = model_instance.generate_content(prompt)
            except ImportError:
                self.logger.error("Google Generative AI library not installed. Please install: pip install google-generativeai")
                raise ValueError("Google Generative AI library not installed")

            # Extract response text
            response_text = response.text if hasattr(response, 'text') else str(response)

            # Estimate token usage (Gemini doesn't always provide exact counts)
            prompt_tokens = len(prompt.split()) * 1.3  # Rough estimation
            completion_tokens = len(response_text.split()) * 1.3
            total_tokens = int(prompt_tokens + completion_tokens)

            token_usage = TokenUsage(
                response_text=response_text,
                tool_calls=None,  # Gemini tool calling support would need additional implementation
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=total_tokens,
            )

            self.token_tracker.add_usage(token_usage)
            return token_usage

        except Exception as e:
            self.logger.error(f"An error occurred during the Gemini call: {e}", exc_info=True)
            raise

    def _chat_ollama(self, messages: list[dict], tools: Optional[List[Dict[str, Any]]] = None, model: str = "llama3.2") -> TokenUsage:
        """Handle Ollama local chat requests."""
        try:
            # Prepare the request to Ollama local server
            url = "http://localhost:11434/api/chat"
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code != 200:
                error_msg = response.text
                # Check for specific Ollama errors and provide helpful messages
                if "not found" in error_msg and "try pulling it first" in error_msg:
                    raise Exception(f"Model '{model}' not found in Ollama. Please run: ollama pull {model}")
                else:
                    raise Exception(f"Ollama request failed with status {response.status_code}: {error_msg}")
            
            result = response.json()
            response_text = result.get("message", {}).get("content", "")
            
            # Estimate token usage
            prompt_text = " ".join([msg["content"] for msg in messages])
            prompt_tokens = len(prompt_text.split()) * 1.3
            completion_tokens = len(response_text.split()) * 1.3
            total_tokens = int(prompt_tokens + completion_tokens)

            token_usage = TokenUsage(
                response_text=response_text,
                tool_calls=None,
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=total_tokens,
            )

            self.token_tracker.add_usage(token_usage)
            return token_usage

        except requests.exceptions.ConnectionError:
            self.logger.error("Cannot connect to Ollama. Make sure Ollama is running on localhost:11434")
            raise ValueError("Cannot connect to Ollama. Please start Ollama service.")
        except Exception as e:
            self.logger.error(f"An error occurred during the Ollama call: {e}", exc_info=True)
            raise

    def _chat_groq(self, messages: list[dict], tools: Optional[List[Dict[str, Any]]] = None, model: str = "llama3-8b-8192") -> TokenUsage:
        """Handle Groq chat requests."""
        api_key = self.config_manager.get_setting('groq_api_key')
        if not api_key:
            self.logger.error("Groq API key not found in config.")
            raise ValueError("Groq API key not found. Please set it in config.")

        try:
            # Use OpenAI compatible API
            from openai import OpenAI
            groq_client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
            }
            # Note: Groq has limited tool support
            
            response = groq_client.chat.completions.create(**kwargs)
            
            message = response.choices[0].message
            prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            total_tokens = response.usage.total_tokens if response.usage else 0

            token_usage = TokenUsage(
                response_text=message.content,
                tool_calls=None,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )

            self.token_tracker.add_usage(token_usage)
            return token_usage

        except Exception as e:
            self.logger.error(f"An error occurred during the Groq call: {e}", exc_info=True)
            raise

    def _chat_mistral(self, messages: list[dict], tools: Optional[List[Dict[str, Any]]] = None, model: str = "mistral-tiny") -> TokenUsage:
        """Handle Mistral chat requests."""
        api_key = self.config_manager.get_setting('mistral_api_key')
        if not api_key or api_key.strip() == "":
            self.logger.error("Mistral API key not found in config.")
            raise ValueError("Mistral API key not found. Please set it in config.")
            
        # Додаткова перевірка на тестові ключі
        if api_key.startswith("test_") or "test" in api_key.lower():
            self.logger.error("Test Mistral API key detected.")
            raise ValueError("Test Mistral API key detected. Please set a valid API key.")

        try:
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"Mistral request failed with status {response.status_code}: {response.text}")
            
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            
            token_usage = TokenUsage(
                response_text=message,
                tool_calls=None,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            )

            self.token_tracker.add_usage(token_usage)
            return token_usage

        except Exception as e:
            self.logger.error(f"An error occurred during the Mistral call: {e}", exc_info=True)
            raise

    def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """Generates an embedding for the given text using OpenAI."""
        if not self.openai_client:
            self.logger.error("OpenAI client not initialized. Cannot get embedding.")
            raise APIError("OpenAI client not initialized.", response=None, body=None)
        try:
            text = text.replace("\n", " ")
            response = self.openai_client.embeddings.create(
                input=[text],
                model=model
            )
            embedding = response.data[0].embedding
            self.logger.debug(f"Successfully generated embedding for text: '{text[:50]}...'")
            return embedding
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}", exc_info=True)
            return []

    def is_provider_available(self, provider: str) -> bool:
        """Check if a specific provider is available and configured."""
        provider = provider.lower()
        if provider == "openai":
            return self.openai_client is not None
        elif provider == "gemini":
            return self.gemini_client is not None
        elif provider == "ollama":
            # Check if Ollama is running
            try:
                response = requests.get("http://localhost:11434/api/version", timeout=5)
                return response.status_code == 200
            except:
                return False
        elif provider == "groq":
            return bool(self.config_manager.get_setting('groq_api_key'))
        elif provider == "mistral":
            return bool(self.config_manager.get_setting('mistral_api_key'))
        return False

    def get_current_provider_info(self) -> Dict[str, str]:
        """Get information about the current provider and model."""
        return {
            "provider": self.current_provider,
            "model": self.current_model,
            "available": self.is_provider_available(self.current_provider)
        }

    def stop_all_llm_calls(self):
        """Stops any ongoing LLM calls."""
        pass

    def check_ollama_models(self) -> Dict[str, bool]:
        """Check which Ollama models are available locally."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                installed_models = [model["name"].split(":")[0] for model in data.get("models", [])]
                
                available_models = {}
                suggested_models = ["llama3.2", "llama3.1", "mistral", "codellama", "phi3", "qwen2"]
                
                for model in suggested_models:
                    available_models[model] = model in installed_models
                    
                return available_models
            else:
                return {}
        except:
            return {}
    
    def get_ollama_install_command(self, model: str) -> str:
        """Get the command to install an Ollama model."""
        return f"ollama pull {model}"
