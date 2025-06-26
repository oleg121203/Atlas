import os
import shutil
import unittest
from unittest.mock import MagicMock

from modules.agents.agent_manager import AgentManager
from modules.agents.memory_manager import MemoryManager
from utils.llm_manager import LLMManager


class TestAgentManager(unittest.TestCase):
    """Unit tests for the AgentManager class."""

    def setUp(self):
        """Set up for testing AgentManager."""
        self.temp_dir = "temp_generated_tools"
        os.makedirs(self.temp_dir, exist_ok=True)

        # Create a valid tool file
        with open(os.path.join(self.temp_dir, "valid_tool.py"), "w") as f:
            f.write("def valid_tool_func(): return 'success'\n")

        # Create a tool file with a syntax error
        with open(os.path.join(self.temp_dir, "invalid_tool.py"), "w") as f:
            f.write("def invalid_tool_func() return 'fail'\n")

        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_memory_manager = MagicMock(spec=MemoryManager)
        self.mock_callback = MagicMock()

        self.agent_manager = AgentManager(
            llm_manager=self.mock_llm_manager,
            memory_manager=self.mock_memory_manager,
            master_agent_update_callback=self.mock_callback,
        )
        self.agent_manager.logger = MagicMock()

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_resilient_tool_loading(self):
        """Test that AgentManager can load valid tools while safely skipping invalid ones."""
        # Given a mix of valid and invalid tools
        valid_tool = {"name": "ValidTool", "function": self.mock_callback, "description": "A valid tool"}
        invalid_tool = {"name": "InvalidTool", "function": None, "description": "An invalid tool"}
        tools = [valid_tool, invalid_tool]
        
        # When initializing AgentManager with these tools
        manager = AgentManager(tools=tools)
        
        # Then only the valid tool should be loaded
        self.assertEqual(len(manager.tools), 1)
        self.assertEqual(manager.tools[0]["name"], "ValidTool")
        # Allow for multiple calls if they occur
        self.mock_callback.assert_called()

    def test_add_and_get_agent(self):
        """Verify that an agent can be added and then retrieved."""
        mock_agent = MagicMock()
        self.agent_manager.add_agent("Test Agent", mock_agent)
        retrieved_agent = self.agent_manager.get_agent("Test Agent")
        self.assertEqual(retrieved_agent, mock_agent, "Should retrieve the same agent instance that was added.")

    def test_get_nonexistent_agent(self):
        """Verify that retrieving a non-existent agent returns None."""
        retrieved_agent = self.agent_manager.get_agent("Nonexistent Agent")
        self.assertIsNone(retrieved_agent, "Should return None for a non-existent agent.")

    def test_list_agent_names(self):
        """Verify that the manager correctly lists the names of all added agents."""
        self.agent_manager.add_agent("Agent One", MagicMock())
        self.agent_manager.add_agent("Agent Two", MagicMock())
        agent_names = self.agent_manager.list_agent_names()
        self.assertCountEqual(agent_names, ["Agent One", "Agent Two"], "Should return the names of all registered agents.")

if __name__ == "__main__":
    unittest.main()
