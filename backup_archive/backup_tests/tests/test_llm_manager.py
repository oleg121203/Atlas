import json
import unittest
from unittest.mock import MagicMock

from modules.agents.token_tracker import TokenTracker

from core.token_usage import TokenUsage
from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


class TestLLMManager(unittest.TestCase):
    def setUp(self):
        self.token_tracker = TokenTracker()
        self.config_manager = MagicMock(spec=ConfigManager)
        self.config_manager.get_current_provider.return_value = "mock_provider"
        self.config_manager.get_current_model.return_value = "mock_model"
        self.llm_manager = LLMManager(self.token_tracker, self.config_manager)
        # Mock provider for testing
        self.mock_provider = MagicMock()
        self.llm_manager.providers = {"mock_provider": self.mock_provider}

    def test_initialization(self):
        self.assertEqual(self.llm_manager.current_provider, "mock_provider")
        self.assertEqual(self.llm_manager.current_model, "mock_model")
        self.assertTrue("mock_provider" in self.llm_manager.providers)

    def test_chat_with_cache_hit(self):
        # Setup cache with a response
        messages = [{"role": "user", "content": "Hello"}]
        cached_response = TokenUsage(
            response_text="Cached response",
            tool_calls=None,
            prompt_tokens=5,
            completion_tokens=10,
            total_tokens=15,
        )
        cache_key = json.dumps(messages[0])
        self.llm_manager.cache[cache_key] = cached_response

        # Test cache hit
        result = self.llm_manager.chat(messages)
        self.assertEqual(result.response_text, "Cached response")
        self.mock_provider.chat.assert_not_called()

    def test_chat_without_cache(self):
        messages = [{"role": "user", "content": "New message"}]
        mock_response = {
            "content": "New response",
            "tool_calls": None,
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        }
        self.mock_provider.is_available.return_value = True
        self.mock_provider.chat.return_value = mock_response

        result = self.llm_manager.chat(messages)
        self.assertEqual(result.response_text, "New response")
        self.mock_provider.chat.assert_called_once_with(
            messages, None, "mock_model", None
        )
        self.assertEqual(result.prompt_tokens, 10)
        self.assertEqual(result.completion_tokens, 20)
        self.assertEqual(result.total_tokens, 30)

    def test_chat_provider_not_available(self):
        messages = [{"role": "user", "content": "Test message"}]
        self.mock_provider.is_available.return_value = False

        result = self.llm_manager.chat(messages)
        self.assertEqual(result.response_text, "Provider is not available")
        self.mock_provider.chat.assert_not_called()

    def test_get_embedding(self):
        text = "Test embedding"
        model = "embedding-model"
        embedding_result = [0.1, 0.2, 0.3]
        self.mock_provider.is_available.return_value = True
        self.mock_provider.get_embedding.return_value = embedding_result
        # Override the default provider for embeddings to use mock_provider
        original_provider = self.llm_manager.providers.get("gemini")
        self.llm_manager.providers["gemini"] = self.mock_provider

        result = self.llm_manager.get_embedding(text, model)
        self.assertEqual(result, embedding_result)
        self.mock_provider.get_embedding.assert_called_once_with(text, model)

        # Restore original provider
        if original_provider:
            self.llm_manager.providers["gemini"] = original_provider
        else:
            del self.llm_manager.providers["gemini"]

    def test_update_settings(self):
        self.config_manager.get_current_provider.return_value = "new_provider"
        self.config_manager.get_current_model.return_value = "new_model"
        # Add new provider to dictionary for testing
        new_provider_mock = MagicMock()
        new_provider_mock.is_available.return_value = True
        self.llm_manager.providers["new_provider"] = new_provider_mock

        self.assertTrue(self.llm_manager.update_settings())
        self.assertEqual(self.llm_manager.current_provider, "new_provider")
        self.assertEqual(self.llm_manager.current_model, "new_model")

    def test_is_provider_available(self):
        self.mock_provider.is_available.return_value = True
        self.assertTrue(self.llm_manager.is_provider_available("mock_provider"))
        self.assertFalse(self.llm_manager.is_provider_available("unknown_provider"))


if __name__ == "__main__":
    unittest.main()
