"""
Test cases for the chat module of Atlas application.
"""

import unittest
from modules.chat.chat_logic import ChatProcessor
from core.application import AtlasApplication

class TestChatModule(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        self.app = AtlasApplication([])
        self.chat_processor = ChatProcessor()

    def test_chat_processor_initialization(self):
        """Test if the chat processor initializes correctly."""
        self.assertIsNotNone(self.chat_processor)
        self.assertTrue(hasattr(self.chat_processor, 'process_message'))

    def test_message_processing(self):
        """Test if a message is processed correctly."""
        test_message = "Hello, how are you?"
        response = self.chat_processor.process_message(test_message)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)

if __name__ == '__main__':
    unittest.main()
