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
        """
        Test that AgentManager can load valid tools while safely skipping invalid ones.
        """
        # Act
        self.agent_manager.reload_generated_tools(directory=self.temp_dir)

        # Assert
        # Check that the valid tool was loaded
        self.assertIn("valid_tool_func", self.agent_manager._tools)
        self.assertEqual(self.agent_manager._tools["valid_tool_func"]["function"](), "success")

        # Check that the invalid tool was not loaded
        self.assertNotIn("invalid_tool_func", self.agent_manager._tools)

        # Check that an error was logged for the invalid file
        self.agent_manager.logger.error.assert_called_once()
        log_message = self.agent_manager.logger.error.call_args[0][0]
        self.assertIn("Failed to load tool from", log_message)
        self.assertIn("invalid_tool.py", log_message)

        # Check that the callback was called to notify of the update
        self.mock_callback.assert_called_once()

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
