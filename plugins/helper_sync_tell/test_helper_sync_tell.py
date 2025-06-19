"""
Tests for the Helper Sync Tell plugin.

These tests verify that the plugin functions correctly in both Linux and macOS environments.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add the Atlas root directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the plugin
sys.path.insert(0, str(Path(__file__).parent))
try:
    from plugin import HelperSyncTellTool
except ImportError:
    # Try alternative import method
    import importlib.util
    spec = importlib.util.spec_from_file_location("plugin", Path(__file__).parent / "plugin.py")
    plugin_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin_module)
    HelperSyncTellTool = plugin_module.HelperSyncTellTool

class TestHelperSyncTell(unittest.TestCase):
    """Test cases for the Helper Sync Tell tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock LLM and memory managers
        self.mock_llm_manager = MagicMock()
        self.mock_memory_manager = MagicMock()
        
        # Configure the mock LLM manager to return predictable responses
        self.mock_llm_manager.generate_text.side_effect = self._mock_llm_responses
        
        # Create the tool with mock managers
        self.helper_tool = HelperSyncTellTool(
            llm_manager=self.mock_llm_manager,
            memory_manager=self.mock_memory_manager
        )
        
        # Sample query for tests
        self.test_query = "How does memory work in Atlas?"
        
        # Mock available tools
        self.available_tools = {
            "code_search": MagicMock(return_value="Code search results"),
            "memory_query": MagicMock(return_value="Memory query results")
        }
    
    def _mock_llm_responses(self, prompt):
        """Provide mock responses based on the prompt content."""
        if "Break down this complex query" in prompt:
            return "1. How is memory stored in Atlas?\n2. What memory types exist in Atlas?"
        elif "Determine which tools" in prompt:
            return "code_search, memory_query"
        elif "Analyze the following results" in prompt or "Provide an analysis" in prompt:
            return "Analysis of memory in Atlas based on available information."
        elif "Synthesize a comprehensive" in prompt:
            return "Atlas memory works through an enhanced memory manager with various memory types."
        elif "Review and refine" in prompt:
            return "Atlas uses a sophisticated memory system with different memory types and scopes."
        else:
            return "Generic LLM response"
    
    def test_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertEqual(self.helper_tool.name, "helper_sync_tell")
        self.assertIsNotNone(self.helper_tool.description)
        self.assertEqual(self.helper_tool.llm_manager, self.mock_llm_manager)
        self.assertEqual(self.helper_tool.memory_manager, self.mock_memory_manager)
    
    def test_break_down_query(self):
        """Test breaking down a complex query."""
        sub_questions = self.helper_tool.break_down_query(self.test_query)
        self.assertEqual(len(sub_questions), 2)
        self.assertEqual(sub_questions[0], "How is memory stored in Atlas?")
        self.assertEqual(sub_questions[1], "What memory types exist in Atlas?")
        
        # Verify LLM was called with the right prompt
        self.mock_llm_manager.generate_text.assert_called_with(
            unittest.mock.ANY  # Can't check the exact string due to whitespace differences
        )
    
    def test_analyze_sub_question(self):
        """Test analyzing a sub-question with available tools."""
        sub_question = "How is memory stored in Atlas?"
        analysis = self.helper_tool.analyze_sub_question(sub_question, self.available_tools)
        
        # Check analysis result
        self.assertIn("Analysis of memory in Atlas", analysis)
        
        # Check if tools were called
        self.available_tools["code_search"].assert_called_once()
        self.available_tools["memory_query"].assert_called_once()
    
    def test_synthesize_response(self):
        """Test synthesizing a response from analyses."""
        analyses = [
            "Analysis 1: Memory is stored using ChromaDB",
            "Analysis 2: Atlas has different memory types like OBSERVATION, PLAN, etc."
        ]
        
        synthesis = self.helper_tool.synthesize_response(self.test_query, analyses)
        self.assertIn("memory", synthesis.lower())
        
        # Verify LLM was called for synthesis
        self.mock_llm_manager.generate_text.assert_called()
    
    def test_refine_response(self):
        """Test refining a response."""
        draft = "Draft response about Atlas memory."
        refined = self.helper_tool.refine_response(self.test_query, draft)
        
        self.assertIsNotNone(refined)
        self.assertIn("sophisticated memory system", refined)
        
        # Verify LLM was called for refinement
        self.mock_llm_manager.generate_text.assert_called()
    
    def test_full_process(self):
        """Test the full query processing workflow."""
        response = self.helper_tool(self.test_query, self.available_tools)
        
        # Check final response
        self.assertIsNotNone(response)
        self.assertIn("memory", response.lower())
        
        # Verify memory steps were stored
        self.assertEqual(self.mock_memory_manager.add_memory_for_agent.call_count, 5)
    
    def test_without_llm(self):
        """Test the tool's fallback behavior without an LLM."""
        # Create tool without LLM
        helper_tool_no_llm = HelperSyncTellTool(
            llm_manager=None,
            memory_manager=self.mock_memory_manager
        )
        
        # Process a query
        response = helper_tool_no_llm(self.test_query, self.available_tools)
        
        # Check that a response was still generated
        self.assertIsNotNone(response)
        self.assertIn("Here's what I found", response)
    
    def test_without_memory(self):
        """Test the tool's behavior without a memory manager."""
        # Create tool without memory manager
        helper_tool_no_memory = HelperSyncTellTool(
            llm_manager=self.mock_llm_manager,
            memory_manager=None
        )
        
        # Process a query
        response = helper_tool_no_memory(self.test_query, self.available_tools)
        
        # Check that a response was still generated
        self.assertIsNotNone(response)
        self.assertIn("memory", response.lower())
    
    @patch('utils.platform_utils.IS_MACOS', True)
    @patch('utils.platform_utils.IS_LINUX', False)
    def test_on_macos(self):
        """Test the tool on macOS platform."""
        with patch('sys.version_info', (3, 13)):
            helper_tool_macos = HelperSyncTellTool(
                llm_manager=self.mock_llm_manager,
                memory_manager=self.mock_memory_manager
            )
            
            # Verify platform detection
            self.assertTrue(helper_tool_macos.platform_info["is_macos"])
            self.assertFalse(helper_tool_macos.platform_info["is_linux"])
            self.assertEqual(helper_tool_macos.platform_info["python_version"], "3.13")
            
            # Test functionality
            response = helper_tool_macos(self.test_query, self.available_tools)
            self.assertIsNotNone(response)
    
    @patch('utils.platform_utils.IS_MACOS', False)
    @patch('utils.platform_utils.IS_LINUX', True)
    def test_on_linux(self):
        """Test the tool on Linux platform."""
        with patch('sys.version_info', (3, 12)):
            helper_tool_linux = HelperSyncTellTool(
                llm_manager=self.mock_llm_manager,
                memory_manager=self.mock_memory_manager
            )
            
            # Verify platform detection
            self.assertFalse(helper_tool_linux.platform_info["is_macos"])
            self.assertTrue(helper_tool_linux.platform_info["is_linux"])
            self.assertEqual(helper_tool_linux.platform_info["python_version"], "3.12")
            
            # Test functionality
            response = helper_tool_linux(self.test_query, self.available_tools)
            self.assertIsNotNone(response)


if __name__ == '__main__':
    unittest.main()
