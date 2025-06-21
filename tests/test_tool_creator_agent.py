import os
import shutil
import unittest
from unittest.mock import MagicMock

from agents.tool_creator_agent import ToolCreatorAgent
from utils.llm_manager import LLMManager


class TestToolCreatorAgent(unittest.TestCase):

    def setUp(self):
        """Set up a test environment before each test."""
        self.tool_dir = "test_generated_tools"
        os.makedirs(self.tool_dir, exist_ok=True)

        self.mock_llm_manager = MagicMock(spec=LLMManager)
        self.mock_memory_manager = MagicMock()
        self.agent = ToolCreatorAgent(
            llm_manager=self.mock_llm_manager,
            memory_manager=self.mock_memory_manager,
            tool_dir=self.tool_dir,
        )
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
        self.mock_memory_manager.search.return_value = []

        result = self.agent.create_tool(tool_description)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tool_name"], "add_numbers")
        expected_file_path = os.path.join(self.tool_dir, "add_numbers.py")
        self.assertTrue(os.path.exists(expected_file_path))

        with open(expected_file_path) as f:
            content = f.read()
            self.assertIn("def add_numbers(a: int, b: int) -> int:", content)

    def test_create_tool_invalid_python(self):
        """Test tool creation failure due to invalid Python syntax."""
        tool_description = "a tool with syntax errors"
        generated_code = "```python\ndef invalid_syntax(a, b) return a + b\n```"
        mock_result = MagicMock()
        mock_result.response_text = generated_code
        self.mock_llm_manager.chat.return_value = mock_result
        self.mock_memory_manager.search.return_value = []

        result = self.agent.create_tool(tool_description)

        self.assertEqual(result["status"], "error")
        self.assertIn("Generated code is not valid Python", result["message"])
        # The __init__.py file is created, so there is 1 file
        self.assertEqual(len(os.listdir(self.tool_dir)), 1)

    def test_create_tool_code_extraction_failure(self):
        """Test tool creation failure when code cannot be extracted."""
        tool_description = "a response with no code"
        generated_code = "I am sorry, I cannot create that tool for you."
        mock_result = MagicMock()
        mock_result.response_text = generated_code
        self.mock_llm_manager.chat.return_value = mock_result
        self.mock_memory_manager.search.return_value = []

        result = self.agent.create_tool(tool_description)

        self.assertEqual(result["status"], "error")
        self.assertIn("Could not extract Python code", result["message"])

    def test_get_function_name(self):
        """Test the internal method to extract a function name from code."""
        code = "def my_test_function(arg1, arg2):\n    pass\n"
        function_name = self.agent._get_function_name(code)
        self.assertEqual(function_name, "my_test_function")

    def test_get_function_name_no_function(self):
        """Test _get_function_name with code that has no function definition."""
        code = "import os\nprint('hello')"
        function_name = self.agent._get_function_name(code)
        self.assertIsNone(function_name)

    def test_create_tool_no_function_definition(self):
        """Test tool creation failure when the code has no function definition."""
        tool_description = "a script that just prints hello"
        generated_code = "```python\nprint('hello world')\n```"
        mock_result = MagicMock()
        mock_result.response_text = generated_code
        self.mock_llm_manager.chat.return_value = mock_result
        self.mock_memory_manager.search.return_value = []

        result = self.agent.create_tool(tool_description)

        self.assertEqual(result["status"], "error")
        self.assertIn("Could not find function definition in generated code", result["message"])

    def test_create_tool_with_imports(self):
        """Test successful creation of a tool that requires imports."""
        tool_description = "a tool to get the current date"
        generated_code = '''```python
import datetime

def get_current_date():
    """Returns the current date as a string."""
    return str(datetime.date.today())
```'''
        mock_result = MagicMock()
        mock_result.response_text = generated_code
        self.mock_llm_manager.chat.return_value = mock_result
        self.mock_memory_manager.search.return_value = []

        result = self.agent.create_tool(tool_description)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tool_name"], "get_current_date")
        expected_file_path = os.path.join(self.tool_dir, "get_current_date.py")
        self.assertTrue(os.path.exists(expected_file_path))

        with open(expected_file_path) as f:
            content = f.read()
            self.assertIn("import datetime", content)
            self.assertIn("def get_current_date():", content)

    def test_create_tool_with_complex_logic(self):
        """Test successful creation of a tool with more complex logic."""
        tool_description = "a tool to check if a number is prime"
        generated_code = '''```python
def is_prime(n: int) -> bool:
    """Checks if a number is prime."""
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```'''
        mock_result = MagicMock()
        mock_result.response_text = generated_code
        self.mock_llm_manager.chat.return_value = mock_result
        self.mock_memory_manager.search.return_value = []

        result = self.agent.create_tool(tool_description)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tool_name"], "is_prime")
        expected_file_path = os.path.join(self.tool_dir, "is_prime.py")
        self.assertTrue(os.path.exists(expected_file_path))
        with open(expected_file_path) as f:
            content = f.read()
            self.assertIn("for i in range(2, int(n**0.5) + 1):", content)

    def test_create_tool_does_not_overwrite_existing(self):
        """Test that creating a tool does not overwrite an existing file."""
        tool_description = "a tool to add two numbers"
        generated_code = '''```python
def add_numbers(a: int, b: int) -> int:
    """Adds two integers together."""
    return a + b
```'''
        mock_result = MagicMock()
        mock_result.response_text = generated_code
        self.mock_llm_manager.chat.return_value = mock_result
        self.mock_memory_manager.search.return_value = []

        # Create the tool once
        result1 = self.agent.create_tool(tool_description)
        self.assertEqual(result1["status"], "success")
        expected_file_path = os.path.join(self.tool_dir, "add_numbers.py")
        self.assertTrue(os.path.exists(expected_file_path))

        # Attempt to create the tool again
        result2 = self.agent.create_tool(tool_description)

        # The agent should detect the file exists and return an error
        self.assertEqual(result2["status"], "error")
        self.assertIn("already exists", result2["message"])

        # Verify the original file was not overwritten
        with open(expected_file_path) as f:
            content = f.read()
            self.assertNotIn("A different implementation", content)

if __name__ == "__main__":
    unittest.main()
