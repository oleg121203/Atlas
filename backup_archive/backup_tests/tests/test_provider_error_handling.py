import unittest
from unittest.mock import MagicMock, patch

from modules.agents.token_tracker import TokenTracker

from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager
from utils.providers.gemini_provider import GeminiProvider
from utils.providers.groq_provider import GroqProvider
from utils.providers.ollama_provider import OllamaProvider
from utils.providers.openai_provider import OpenAIProvider


class TestProviderErrorHandling(unittest.TestCase):
    def setUp(self):
        self.token_tracker = TokenTracker()
        self.config_manager = MagicMock(spec=ConfigManager)
        self.config_manager.get_current_provider.return_value = "openai"
        self.config_manager.get_current_model.return_value = "gpt-4-turbo"
        self.config_manager.get_openai_api_key.return_value = "valid_key"
        self.config_manager.get_gemini_api_key.return_value = "valid_key"
        self.config_manager.get_setting.return_value = "valid_key"
        self.llm_manager = LLMManager(self.token_tracker, self.config_manager)

    def test_openai_provider_error_handling(self):
        messages = [{"role": "user", "content": "Test message"}]
        # Mock OpenAI provider to raise an exception
        with (
            patch.object(OpenAIProvider, "is_available", return_value=True),
            patch.object(OpenAIProvider, "chat", side_effect=Exception("API Error")),
        ):
            self.llm_manager.current_provider = "openai"
            result = self.llm_manager.chat(messages)
            self.assertEqual(result.response_text, "")
            self.assertEqual(result.prompt_tokens, 0)
            self.assertEqual(result.completion_tokens, 0)
            self.assertEqual(result.total_tokens, 0)

    def test_gemini_provider_error_handling(self):
        messages = [{"role": "user", "content": "Test message"}]
        # Mock Gemini provider to raise an exception
        with (
            patch.object(GeminiProvider, "is_available", return_value=True),
            patch.object(GeminiProvider, "chat", side_effect=Exception("API Error")),
        ):
            self.llm_manager.current_provider = "gemini"
            result = self.llm_manager.chat(messages)
            self.assertEqual(result.response_text, "")
            self.assertEqual(result.prompt_tokens, 0)
            self.assertEqual(result.completion_tokens, 0)
            self.assertEqual(result.total_tokens, 0)

    def test_groq_provider_error_handling(self):
        messages = [{"role": "user", "content": "Test message"}]
        # Mock Groq provider to raise an exception
        with (
            patch.object(GroqProvider, "is_available", return_value=True),
            patch.object(GroqProvider, "chat", side_effect=Exception("API Error")),
        ):
            self.llm_manager.current_provider = "groq"
            result = self.llm_manager.chat(messages)
            self.assertEqual(result.response_text, "")
            self.assertEqual(result.prompt_tokens, 0)
            self.assertEqual(result.completion_tokens, 0)
            self.assertEqual(result.total_tokens, 0)

    def test_ollama_provider_error_handling(self):
        messages = [{"role": "user", "content": "Test message"}]
        # Mock Ollama provider to raise an exception
        with (
            patch.object(OllamaProvider, "is_available", return_value=True),
            patch.object(OllamaProvider, "chat", side_effect=Exception("API Error")),
        ):
            self.llm_manager.current_provider = "ollama"
            result = self.llm_manager.chat(messages)
            self.assertEqual(result.response_text, "")
            self.assertEqual(result.prompt_tokens, 0)
            self.assertEqual(result.completion_tokens, 0)
            self.assertEqual(result.total_tokens, 0)

    def test_fallback_on_provider_unavailable(self):
        messages = [{"role": "user", "content": "Test message"}]
        # Set an invalid provider to test fallback or error handling
        self.llm_manager.current_provider = "invalid_provider"
        result = self.llm_manager.chat(messages)
        self.assertEqual(result.response_text, "")
        self.assertEqual(result.prompt_tokens, 0)
        self.assertEqual(result.completion_tokens, 0)
        self.assertEqual(result.total_tokens, 0)

    def test_embedding_error_handling(self):
        text = "Test embedding"
        # Mock Gemini provider (default for embeddings) to raise an exception
        with (
            patch.object(GeminiProvider, "is_available", return_value=True),
            patch.object(
                GeminiProvider, "get_embedding", side_effect=Exception("API Error")
            ),
        ):
            result = self.llm_manager.get_embedding(text)
            self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
