import unittest
import os
import shutil
from unittest.mock import MagicMock

from agents.agent_manager import AgentManager
from agents.llm_manager import LLMManager
from agents.memory_manager import MemoryManager


class TestAgentManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for generated tools."""
        self.temp_dir = "temp_generated_tools"
        os.makedirs(self.temp_dir, exist_ok=True)

        # Create a valid tool file
        with open(os.path.join(self.temp_dir, "valid_tool.py"), "w") as f:
            f.write("def valid_tool_func(): return 'success'\n")

        # Create a tool file with a syntax error
        with open(os.path.join(self.temp_dir, "invalid_tool.py"), "w") as f:
            f.write("def invalid_tool_func() return 'fail'\n") # Missing colon

        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_memory_manager = MagicMock(spec=MemoryManager)
        self.mock_callback = MagicMock()

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_resilient_tool_loading(self):
        """
        Test that AgentManager can load valid tools while safely skipping invalid ones.
        """
        # Arrange
        agent_manager = AgentManager(
            llm_manager=self.mock_llm_manager,
            memory_manager=self.mock_memory_manager,
            master_agent_update_callback=self.mock_callback
        )
        agent_manager.logger = MagicMock()

        # Act
        agent_manager.reload_generated_tools(directory=self.temp_dir)

        # Assert
        # Check that the valid tool was loaded
        self.assertIn("valid_tool_func", agent_manager._tools)
        self.assertEqual(agent_manager._tools["valid_tool_func"]['function'](), 'success')

        # Check that the invalid tool was not loaded
        self.assertNotIn("invalid_tool_func", agent_manager._tools)

        # Check that an error was logged for the invalid file
        agent_manager.logger.error.assert_called_once()
        log_message = agent_manager.logger.error.call_args[0][0]
        self.assertIn("Failed to load tool from", log_message)
        self.assertIn("invalid_tool.py", log_message)

        # Check that the callback was called to notify of the update
        self.mock_callback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
from unittest.mock import MagicMock
import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from agents.agent_manager import AgentManager

class TestAgentManager(unittest.TestCase):
    """Unit tests for the AgentManager class."""

    def setUp(self):
        """Set up a new AgentManager for each test."""
        self.agent_manager = AgentManager()

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

if __name__ == '__main__':
    unittest.main()
