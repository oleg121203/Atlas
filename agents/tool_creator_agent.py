"""
Defines the ToolCreatorAgent for dynamically generating new tools.
"""

import os
import re
import ast
from typing import Optional, Dict, Any, TYPE_CHECKING, List

from utils.llm_manager import LLMManager
from utils.logger import get_logger

if TYPE_CHECKING:
    from agents.memory_manager import MemoryManager

class ToolCreatorAgent:
    """An agent that can write new Python tool functions based on a description."""

    def __init__(self, llm_manager: LLMManager, memory_manager: 'MemoryManager', tool_dir: str = "tools/generated"):
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.logger = get_logger()
        self.tool_dir = tool_dir
        os.makedirs(self.tool_dir, exist_ok=True)
        # Ensure the directory is a Python package
        init_path = os.path.join(self.tool_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write("")
        self.logger.info(f"ToolCreatorAgent initialized. Tools will be saved in '{self.tool_dir}'")

    def _get_creation_prompt(self, tool_description: str, examples: Optional[List[Dict[str, Any]]] = None) -> str:
        """Constructs the prompt for the LLM to generate a tool."""
        
        examples_text = ""
        if examples:
            successful_examples = []
            failed_examples = []
            for ex in examples:
                doc = ex.get('document', {})
                if not doc:
                    continue
                
                desc = doc.get('description')
                res = doc.get('result', {})
                status = res.get('status')
                
                if status == 'success':
                    code = res.get('code')
                    if code:
                        successful_examples.append(f"Description: {desc}\n```python\n{code}\n```")
                elif status == 'error':
                    message = res.get('message')
                    failed_examples.append(f"Description: {desc}\nError: {message}")

            if successful_examples:
                examples_text += "\n\n**Here are some examples of successful past attempts for similar requests:**\n"
                examples_text += "\n---\n".join(successful_examples)
            
            if failed_examples:
                examples_text += "\n\n**Here are some examples of FAILED past attempts. Do NOT repeat these mistakes:**\n"
                examples_text += "\n---\n".join(failed_examples)

        return f"""You are an expert Python programmer specializing in creating standalone tool functions for an AI agent system. Your task is to write a single Python function based on a user's request.

**Requirements for the generated code:**
1.  **Single Function:** The output must be a single Python function.
2.  **Imports:** All necessary imports must be included at the top level of the script.
3.  **Type Hinting:** All function arguments and the return value must have clear Python type hints.
4.  **Docstrings:** The function must have a Google-style docstring explaining what it does, its arguments, and what it returns.
5.  **Simplicity:** The function should be as simple as possible to accomplish the task.
6.  **No Classes:** Do not define any classes.
7.  **Error Handling:** Include basic error handling (e.g., try-except blocks) for operations that might fail, like network requests or file I/O.
8.  **Output Format:** Respond ONLY with a single Python code block in markdown format (i.e., ```python ... ```). Do not include any other text, explanations, or conversation.

**Example of a well-formed tool:**

```python
import requests
from typing import Dict, Any

def get_current_weather(city: str) -> Dict[str, Any]:
    '''Gets the current weather for a specified city using an online API.

    Args:
        city: The name of the city.

    Returns:
        A dictionary containing weather data, or an error message.
    '''
    #This is an example and requires a real API key.
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {{"q": city, "appid": "YOUR_API_KEY", "units": "metric"}}
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  #Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return {{"error": "Failed to retrieve weather data: " + str(e)}}
```

**User's Tool Request:**
"{tool_description}"
{examples_text}
"""

    def _extract_python_code(self, response: str) -> Optional[str]:
        """Extracts Python code from a markdown block."""
        match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _validate_code(self, code: str) -> bool:
        """Validates the Python code syntax."""
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            self.logger.error(f"Generated code has a syntax error: {e}")
            return False

    def _get_function_name(self, code: str) -> Optional[str]:
        """Parses the code to find the first function definition's name."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    return node.name
        except SyntaxError:
            return None
        return None

    def create_tool(self, tool_description: str) -> Dict[str, Any]:
        """Generates, validates, and saves a new tool function, learning from past attempts."""
        self.logger.info(f"Attempting to create a new tool for: '{tool_description}'")
        
        past_attempts = self.memory_manager.search(
            collection="tool_creation_history",
            query=tool_description,
            limit=3
        )

        prompt = self._get_creation_prompt(tool_description, past_attempts)
        result: Dict[str, Any] = {}
        code_generated = None
        
        try:
            llm_result = self.llm_manager.chat([{"role": "system", "content": prompt}])
            if not llm_result or not llm_result.response_text:
                result = {"status": "error", "message": "LLM returned no response."}
            else:
                code = self._extract_python_code(llm_result.response_text)
                code_generated = code
                if not code:
                    result = {"status": "error", "message": "Could not extract Python code from LLM response."}
                elif not self._validate_code(code):
                    result = {"status": "error", "message": "Generated code is not valid Python."}
                else:
                    function_name = self._get_function_name(code)
                    if not function_name:
                        result = {"status": "error", "message": "Could not find function definition in generated code"}
                    else:
                        file_name = f"{function_name}.py"
                        file_path = os.path.join(self.tool_dir, file_name)

                        if os.path.exists(file_path):
                            result = {"status": "error", "message": f"Tool file '{file_path}' already exists."}
                        else:
                            with open(file_path, "w") as f:
                                f.write(code)
                            self.logger.info(f"Successfully created new tool: {file_path}")
                            result = {
                                "status": "success", 
                                "message": f"Tool '{function_name}' created at {file_path}",
                                "tool_name": function_name,
                                "file_path": file_path,
                                "code": code
                            }

        except Exception as e:
            self.logger.error(f"An unexpected error occurred in create_tool: {e}", exc_info=True)
            result = {"status": "error", "message": f"An unexpected error occurred: {e}"}

        doc_to_save = {
            "description": tool_description,
            "result": result
        }
        if result.get("status") != "success" and code_generated:
             doc_to_save['result']['code_generated'] = code_generated

        self.memory_manager.add(
            collection="tool_creation_history",
            document=doc_to_save
        )

        return result
