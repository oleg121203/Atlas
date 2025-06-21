import unittest
import os
import shutil
from unittest.mock import MagicMock

from agents.tool_creator_agent import ToolCreatorAgent
from utils.llm_manager import LLMManager

class TestToolCreatorAgent(unittest.TestCase):

    def setUp(self):
        """Set up a test environment before each test."""
        self.tool_dir = "test_generated_tools"
        os.makedirs(self.tool_dir, exist_ok=True)
        
        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.agent = ToolCreatorAgent(llm_manager=self.mock_llm_manager, tool_dir=self.tool_dir)
        self.agent.logger = MagicMock() #Mock logger to suppress output during tests

    def tearDown(self):
        """Clean up the test environment after each test."""
        if os.path.exists(self.tool_dir):
            shutil.rmtree(self.tool_dir)

    def test_create_tool_success(self):
        """Test successful creation of a new tool."""
        tool_description = "a tool to add two numbers"
        generated_code = '''```python
def add_numbers(a: int, b: int) -> int:
    """Adds two integers together."""
    return a + b
```'''
        mock_result = MagicMock()
        mock_result.response_text = generated_code
        self.mock_llm_manager.chat.return_value = mock_result

        result = self.agent.create_tool(tool_description)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['tool_name'], 'add_numbers')
        expected_file_path = os.path.join(self.tool_dir, 'add_numbers.py')
        self.assertTrue(os.path.exists(expected_file_path))

        with open(expected_file_path, 'r') as f:
            content = f.read()
            self.assertIn('def add_numbers(a: int, b: int) -> int:', content)

    def test_create_tool_invalid_python(self):
        """Test tool creation failure due to invalid Python syntax."""
        tool_description = "a tool with syntax errors"
        generated_code = "```python\ndef invalid_syntax(a, b) return a + b\n```"
        mock_result = MagicMock()
        mock_result.response_text = generated_code
        self.mock_llm_manager.chat.return_value = mock_result

        result = self.agent.create_tool(tool_description)

        self.assertEqual(result['status'], 'error')
        self.assertIn('Generated code is not valid Python', result['message'])
        self.assertEqual(len(os.listdir(self.tool_dir)), 0)

    def test_create_tool_code_extraction_failure(self):
        """Test tool creation failure when code cannot be extracted."""
        tool_description = "a response with no code"
        generated_code = "I am sorry, I cannot create that tool for you."
        mock_result = MagicMock()
        mock_result.response_text = generated_code
        self.mock_llm_manager.chat.return_value = mock_result

        result = self.agent.create_tool(tool_description)

        self.assertEqual(result['status'], 'error')
        self.assertIn('Could not extract Python code', result['message'])

    def test_get_function_name(self):
        """Test the internal method to extract a function name from code."""
        code = "def my_test_function(arg1, arg2):\n    pass\n"
        function_name = self.agent._get_function_name(code)
        self.assertEqual(function_name, 'my_test_function')

    def test_get_function_name_no_function(self):
        """Test _get_function_name with code that has no function definition."""
        code = "import os\nprint('hello')"
        function_name = self.agent._get_function_name(code)
        self.assertIsNone(function_name)

if __name__ == '__main__':
    unittest.main()
