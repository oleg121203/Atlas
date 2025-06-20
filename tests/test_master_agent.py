import sys
import os
import unittest

#Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import MagicMock, create_autospec

from agents.agent_manager import AgentManager
from agents.llm_manager import LLMManager
from agents.master_agent import MasterAgent
from agents.memory_manager import MemoryManager


class TestMasterAgent(unittest.TestCase):
    """Tests for the MasterAgent class."""

    def setUp(self):
        """Set up mocks for dependencies using autospec for accuracy."""
        self.mock_llm_manager = create_autospec(LLMManager, instance=True)
        self.mock_agent_manager = create_autospec(AgentManager, instance=True)
        self.mock_memory_manager = create_autospec(MemoryManager, instance=True)

        self.mock_agent_manager.get_tool_list_string.return_value = "[mock_tool_description]"
        self.mock_agent_manager._agents = {'some_agent': MagicMock()}
        self.mock_memory_manager.search_memories.return_value = []

        self.master_agent = MasterAgent(
            llm_manager=self.mock_llm_manager,
            agent_manager=self.mock_agent_manager,
            memory_manager=self.mock_memory_manager,
        )

    def test_init_registers_callback(self):
        """Test that MasterAgent registers its update callback with AgentManager on init."""
        self.assertEqual(
            self.master_agent._on_tools_updated,
            self.mock_agent_manager.master_agent_update_callback
        )

    def test_prompt_caching_and_invalidation(self):
        """Test that the planning prompt is cached and invalidated correctly."""
        #Check initial state
        self.assertTrue(self.master_agent._tools_changed)
        self.assertIsNone(self.master_agent.system_prompt_template)

        #1. First call, prompt should be generated
        self.master_agent._get_planning_prompt("test goal", [], [])
        self.assertEqual(self.mock_agent_manager.get_tool_list_string.call_count, 1)

        #Check state after first call
        self.assertFalse(self.master_agent._tools_changed, "Flag _tools_changed should be False after prompt generation")
        self.assertIsNotNone(self.master_agent.system_prompt_template, "system_prompt_template should be set after generation")
    
        #2. Second call, prompt should be cached
        self.master_agent._get_planning_prompt("another goal", [], [])
        self.assertEqual(self.mock_agent_manager.get_tool_list_string.call_count, 1, "get_tool_list_string should not be called again")

        #3. Invalidate cache by calling the callback
        self.master_agent._on_tools_updated()
        self.assertTrue(self.master_agent._tools_changed, "Flag _tools_changed should be True after invalidation")
        
        #4. Third call, prompt should be regenerated
        self.master_agent._get_planning_prompt("third goal", [], [])
        self.assertEqual(self.mock_agent_manager.get_tool_list_string.call_count, 2, "get_tool_list_string should be called again after invalidation")


if __name__ == "__main__":
    unittest.main()
