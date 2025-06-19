import unittest
import os
import shutil
from unittest.mock import MagicMock

from agents.agent_manager import AgentManager
from agents.llm_manager import LLMManager

class TestAgentManagerReloading(unittest.TestCase):

    def setUp(self):
        """Set up a test environment before each test."""
        self.generated_tools_dir = "test_temp_generated_tools"
        os.makedirs(self.generated_tools_dir, exist_ok=True)

        self.tool_name = "dummy_reload_tool"
        self.tool_code = f"""
def {self.tool_name}(arg1: str):
    \"\"\"A dummy tool for testing reloading.\"\"\"
    return f\"Processed: {{arg1}}\"
"""
        with open(os.path.join(self.generated_tools_dir, f"{self.tool_name}.py"), "w") as f:
            f.write(self.tool_code)

        self.mock_update_callback = MagicMock()
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.agent_manager = AgentManager(llm_manager=self.mock_llm_manager)
        self.agent_manager.master_agent_update_callback = self.mock_update_callback
        self.agent_manager.logger = MagicMock()

    def tearDown(self):
        """Clean up the test environment after each test."""
        if os.path.exists(self.generated_tools_dir):
            shutil.rmtree(self.generated_tools_dir)

    def test_reload_generated_tools_and_callback(self):
        """Test that reloading tools loads new functions and triggers the callback."""
        self.assertNotIn(self.tool_name, self.agent_manager._tools.keys())

        self.agent_manager.reload_generated_tools(directory=self.generated_tools_dir)

        self.assertIn(self.tool_name, self.agent_manager._tools.keys())
        self.mock_update_callback.assert_called_once()

        result = self.agent_manager.execute_tool(self.tool_name, {"arg1": "test"})
        self.assertEqual(result, "Processed: test")

if __name__ == '__main__':
    unittest.main()
