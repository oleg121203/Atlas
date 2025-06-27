import unittest
from unittest.mock import MagicMock

from modules.agents.master_agent import MasterAgent


class TestFullWorkflow(unittest.TestCase):
    """Tests a full, multi-agent workflow from goal to completion."""

    def setUp(self):
        """Set up the test environment."""
        self.mock_llm_manager = MagicMock()
        self.master_agent = MasterAgent(
            llm_manager=self.mock_llm_manager, prompt="Full Workflow Test"
        )

    def test_multi_agent_workflow(self):
        """Simulate a workflow: open a website, capture text, and save it."""
        goal = "Open 'https://example.com', find the main headline, and save it to 'headline.txt'."

        # 1. Mock the generated plan from the LLM
        mock_plan = [
            {"agent": "Browser Agent", "prompt": "Open the URL 'https://example.com'"},
            {
                "agent": "Screen Agent",
                "prompt": "Capture the main headline text from the current screen",
            },
            {
                "agent": "System Interaction Agent",
                "prompt": "Save the following text to a file named 'headline.txt': [LAST_RESULT]",
            },
        ]
        self.master_agent._generate_plan = MagicMock(return_value=mock_plan)

        # 2. Mock the results from each specialized agent's execution
        mock_browser_agent = self.master_agent.agents.get_agent("Browser Agent")
        mock_browser_agent.execute_task = MagicMock(
            return_value={"status": "success", "message": "URL opened"}
        )

        mock_screen_agent = self.master_agent.agents.get_agent("Screen Agent")
        mock_screen_agent.execute_task = MagicMock(
            return_value={"status": "success", "data": "Example Domain Headline"}
        )

        mock_system_agent = self.master_agent.agents.get_agent(
            "System Interaction Agent"
        )
        mock_system_agent.execute_task = MagicMock(
            return_value={"status": "success", "message": "File saved"}
        )

        # 3. Run the agent and wait for completion
        self.master_agent.run(
            goal, master_prompt="Full Workflow Test", options={"is_cyclic": False}
        )
        if self.master_agent.thread:
            self.master_agent.thread.join(timeout=5)

        # 4. Assertions
        # Verify the plan was generated once
        self.master_agent._generate_plan.assert_called_once_with(
            goal, error_context=None
        )

        # Verify each agent was called in the correct order with the correct prompt

        mock_browser_agent.execute_task.assert_called_once_with(
            prompt="Open the URL 'https://example.com'", context={}
        )
        mock_screen_agent.execute_task.assert_called_once_with(
            prompt="Capture the main headline text from the current screen",
            context={"last_result": {"status": "success", "message": "URL opened"}},
        )
        mock_system_agent.execute_task.assert_called_once_with(
            prompt="Save the following text to a file named 'headline.txt': [LAST_RESULT]",
            context={
                "last_result": {"status": "success", "data": "Example Domain Headline"}
            },
        )


if __name__ == "__main__":
    unittest.main()
