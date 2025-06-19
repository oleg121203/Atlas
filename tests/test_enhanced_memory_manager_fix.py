#!/usr/bin/env python3
"""
Test to verify that the EnhancedMemoryManager initialization issue is fixed.
This test should pass now that the ChatContextManager properly handles dependencies.
"""

import unittest
import sys
import os
import unittest.mock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def mock_gui_modules():
    """Mock GUI modules to prevent import errors during testing."""
    # Mock PyAutoGUI and related modules
    sys.modules['pyautogui'] = unittest.mock.MagicMock()
    sys.modules['mouseinfo'] = unittest.mock.MagicMock()
    sys.modules['Xlib'] = unittest.mock.MagicMock()
    sys.modules['Xlib.display'] = unittest.mock.MagicMock()
    
    # Mock screenshot tool
    mock_capture_screen = unittest.mock.MagicMock()
    mock_capture_screen.return_value = b'fake_screenshot_data'
    
    # Create a mock module for screenshot_tool
    mock_screenshot_module = unittest.mock.MagicMock()
    mock_screenshot_module.capture_screen = mock_capture_screen
    sys.modules['tools.screenshot_tool'] = mock_screenshot_module

# Set up mocks before importing any real modules
mock_gui_modules()

# Now import the modules we want to test
from config_manager import ConfigManager
from agents.llm_manager import LLMManager
from agents.enhanced_memory_manager import EnhancedMemoryManager
from agents.chat_context_manager import ChatContextManager


class TestEnhancedMemoryManagerFix(unittest.TestCase):
    """Test suite for the EnhancedMemoryManager initialization fix."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ConfigManager()
        self.llm_manager = LLMManager(self.config_manager)
    
    def test_enhanced_memory_manager_creation(self):
        """Test that EnhancedMemoryManager can be created with required arguments."""
        memory_manager = EnhancedMemoryManager(
            llm_manager=self.llm_manager, 
            config_manager=self.config_manager
        )
        
        # Verify the memory manager was created successfully
        self.assertIsNotNone(memory_manager)
        self.assertEqual(memory_manager.llm_manager, self.llm_manager)
        self.assertEqual(memory_manager.config_manager, self.config_manager)
    
    def test_chat_context_manager_with_memory_manager(self):
        """Test that ChatContextManager can be created with a memory_manager."""
        memory_manager = EnhancedMemoryManager(
            llm_manager=self.llm_manager, 
            config_manager=self.config_manager
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
        llm_manager = LLMManager(config_manager)
        memory_manager = EnhancedMemoryManager(
            llm_manager=llm_manager, 
            config_manager=config_manager
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


if __name__ == '__main__':
    # Suppress info messages during testing
    import logging
    logging.getLogger().setLevel(logging.ERROR)
    
    unittest.main(verbosity=2)
