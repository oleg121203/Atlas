#!/usr/bin/env python3
"""
Test to verify that the EnhancedMemoryManager initialization issue is fixed.
This test should pass now that the ChatContextManager properly handles dependencies.
"""

import sys
import unittest
import unittest.mock

# Mock GUI modules to prevent import errors during testing.
# This must be done BEFORE importing the application modules.
sys.modules["pyautogui"] = unittest.mock.MagicMock()
sys.modules["mouseinfo"] = unittest.mock.MagicMock()
sys.modules["Xlib"] = unittest.mock.MagicMock()
sys.modules["Xlib.display"] = unittest.mock.MagicMock()

# Mock screenshot tool
mock_capture_screen = unittest.mock.MagicMock()
mock_capture_screen.return_value = b"fake_screenshot_data"
mock_screenshot_module = unittest.mock.MagicMock()
mock_screenshot_module.capture_screen = mock_capture_screen
sys.modules["tools.screenshot_tool"] = mock_screenshot_module

# Now that mocks are in place, we can import our modules.
from modules.agents.chat_context_manager import ChatContextManager
from modules.agents.enhanced_memory_manager import EnhancedMemoryManager
from modules.agents.token_tracker import TokenTracker

from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


class TestEnhancedMemoryManagerFix(unittest.TestCase):
    """Test suite for the EnhancedMemoryManager initialization fix."""

    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ConfigManager()
        self.token_tracker = TokenTracker()
        self.llm_manager = LLMManager(self.token_tracker, self.config_manager)

    def test_enhanced_memory_manager_creation(self):
        """Test that EnhancedMemoryManager can be created with required arguments."""
        memory_manager = EnhancedMemoryManager(
            llm_manager=self.llm_manager,
            config_manager=self.config_manager,
        )

        # Verify the memory manager was created successfully
        self.assertIsNotNone(memory_manager)
        self.assertEqual(memory_manager.llm_manager, self.llm_manager)
        self.assertEqual(memory_manager.config_manager, self.config_manager)

    def test_chat_context_manager_with_memory_manager(self):
        """Test that ChatContextManager can be created with a memory_manager."""
        memory_manager = EnhancedMemoryManager(
            llm_manager=self.llm_manager,
            config_manager=self.config_manager,
        )

        chat_context_manager = ChatContextManager(memory_manager=memory_manager)

        # Verify the chat context manager was created successfully
        self.assertIsNotNone(chat_context_manager)
        self.assertEqual(chat_context_manager.memory_manager, memory_manager)

    def test_chat_context_manager_without_memory_manager(self):
        """Test that ChatContextManager can be created without a memory_manager."""
        chat_context_manager = ChatContextManager()

        # Verify the chat context manager was created successfully
        self.assertIsNotNone(chat_context_manager)
        # memory_manager should be None when not provided
        self.assertIsNone(chat_context_manager.memory_manager)

    def test_atlas_app_simulation(self):
        """Test simulating the AtlasApp initialization sequence."""
        # This simulates the exact sequence that happens in AtlasApp.__init__
        config_manager = ConfigManager()
        token_tracker = TokenTracker()
        llm_manager = LLMManager(token_tracker, config_manager)
        memory_manager = EnhancedMemoryManager(
            llm_manager=llm_manager,
            config_manager=config_manager,
        )
        chat_context_manager = ChatContextManager(memory_manager=memory_manager)

        # Verify all components were created successfully
        self.assertIsNotNone(config_manager)
        self.assertIsNotNone(llm_manager)
        self.assertIsNotNone(memory_manager)
        self.assertIsNotNone(chat_context_manager)

        # Verify the dependencies are correctly set
        self.assertEqual(memory_manager.llm_manager, llm_manager)
        self.assertEqual(memory_manager.config_manager, config_manager)
        self.assertEqual(chat_context_manager.memory_manager, memory_manager)


if __name__ == "__main__":
    # Suppress info messages during testing
    import logging

    logging.getLogger().setLevel(logging.ERROR)

    unittest.main(verbosity=2)
