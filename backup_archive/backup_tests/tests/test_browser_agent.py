import unittest
from unittest.mock import MagicMock, patch

# Import the class to test
from modules.agents.browser_agent import BrowserAgent


class TestBrowserAgent(unittest.TestCase):
    def setUp(self):
        # Create a mock logger
        self.mock_logger = MagicMock()
        # Instantiate the agent with the mock logger
        self.agent = BrowserAgent(logger=self.mock_logger)
        # Do not reset mock here to capture initialization logs

    def test_init(self):
        """Test initialization of BrowserAgent."""
        self.assertIsNotNone(self.agent)
        self.mock_logger.info.assert_called_with("Browser Control Agent initialized.")

    def test_execute_task_open(self):
        """Test executing a task to open a browser."""
        prompt = "open Safari"
        with patch.object(self.agent, "_handle_browser_open") as mock_handler:
            mock_handler.return_value = "Opening browser"
            result = self.agent.execute_task(prompt, {})
            mock_handler.assert_called_once_with(prompt)
            self.assertEqual(result, "Opening browser")
            self.mock_logger.info.assert_called_with(
                f"Executing browser task: {prompt}"
            )

    def test_execute_task_search(self):
        """Test executing a task to search in a browser."""
        prompt = "search for AI news"
        with patch.object(self.agent, "_handle_browser_search") as mock_handler:
            mock_handler.return_value = "Searching for AI news"
            result = self.agent.execute_task(prompt, {})
            mock_handler.assert_called_once_with(prompt)
            self.assertEqual(result, "Searching for AI news")
            self.mock_logger.info.assert_called_with(
                f"Executing browser task: {prompt}"
            )

    def test_execute_task_close(self):
        """Test executing a task to close a browser."""
        prompt = "close browser"
        with patch.object(self.agent, "_handle_browser_close") as mock_handler:
            mock_handler.return_value = "Closing browser"
            result = self.agent.execute_task(prompt, {})
            mock_handler.assert_called_once_with(prompt)
            self.assertEqual(result, "Closing browser")
            self.mock_logger.info.assert_called_with(
                f"Executing browser task: {prompt}"
            )

    def test_execute_task_click(self):
        """Test executing a task to click an element."""
        prompt = "click on login button"
        with patch.object(self.agent, "_handle_click") as mock_handler:
            mock_handler.return_value = "Clicking login button"
            result = self.agent.execute_task(prompt, {})
            mock_handler.assert_called_once_with(prompt)
            self.assertEqual(result, "Clicking login button")
            self.mock_logger.info.assert_called_with(
                f"Executing browser task: {prompt}"
            )

    def test_execute_task_input(self):
        """Test executing a task to input text."""
        prompt = "enter username JohnDoe"
        with patch.object(self.agent, "_handle_input") as mock_handler:
            mock_handler.return_value = "Entering username"
            result = self.agent.execute_task(prompt, {})
            mock_handler.assert_called_once_with(prompt)
            self.assertEqual(result, "Entering username")
            self.mock_logger.info.assert_called_with(
                f"Executing browser task: {prompt}"
            )

    def test_execute_task_default(self):
        """Test executing a default task."""
        prompt = "some other task"
        with patch.object(self.agent, "_handle_default") as mock_handler:
            mock_handler.return_value = "Handling default task"
            result = self.agent.execute_task(prompt, {})
            mock_handler.assert_called_once_with(prompt)
            self.assertEqual(result, "Handling default task")
            self.mock_logger.info.assert_called_with(
                f"Executing browser task: {prompt}"
            )

    def test_execute_task_error_handling(self):
        """Test error handling during task execution."""
        prompt = "open browser"
        with patch.object(self.agent, "_handle_browser_open") as mock_handler:
            mock_handler.side_effect = Exception("Test error")
            with patch.object(self.agent, "_handle_error") as mock_error_handler:
                mock_error_handler.return_value = "Error handled"
                result = self.agent.execute_task(prompt, {})
                mock_error_handler.assert_called_once_with(prompt, "Test error")
                self.assertEqual(result, "Error handled")
                self.mock_logger.info.assert_called_with(
                    f"Executing browser task: {prompt}"
                )
                self.mock_logger.error.assert_called_with(
                    f"Error executing browser task '{prompt}': Test error"
                )

    def test_get_status(self):
        """Test getting the agent's status."""
        result = self.agent.get_status()
        self.assertEqual(result, "Browser Control Agent is operational")

    def test_initialize(self):
        """Test initializing the agent."""
        with patch.object(self.agent, "_check_tools") as mock_check:
            self.agent.initialize()
            mock_check.assert_called_once()
            self.mock_logger.info.assert_called_with(
                "Initializing Browser Control Agent"
            )

    def test_shutdown(self):
        """Test shutting down the agent."""
        self.agent.shutdown()
        self.mock_logger.info.assert_called_with("Shutting down Browser Control Agent")

    def test_handle_error(self):
        """Test error handling method."""
        error = "Test error message"
        prompt = "test prompt"
        result = self.agent._handle_error(prompt, error)
        self.assertEqual(result, f"Failed to execute browser task: {error}")


if __name__ == "__main__":
    unittest.main()
