# Atlas Plugin Development Guide

This guide explains how to create custom plugins for Atlas to extend its capabilities with new tools and specialized agents.

## Plugin Structure

A plugin is a Python package located in the `plugins/` directory. A typical plugin has the following structure:

```
plugins/
└── my_awesome_plugin/
    ├── __init__.py
    ├── tools.py
    └── agent.py
```

- `__init__.py`: The entry point for your plugin. It must contain a `register()` function.
- `tools.py`: (Recommended) Contains the functions that your plugin provides as tools.
- `agent.py`: (Optional) Contains the definition of your custom agent, if you are providing one.

## The `register()` Function

The `__init__.py` file must contain a `register(llm_manager)` function. The `PluginManager` calls this function during startup to discover what your plugin offers.

The function receives an instance of the `LLMManager`, which you can pass to any custom agents you create.

It must return a dictionary with two keys:
- `"agents"`: A dictionary mapping agent names to agent instances.
- `"tools"`: A list of callable tool functions.

**Example `__init__.py`:**
```python
from typing import TYPE_CHECKING
from .tools import my_tool
from .agent import MyAwesomeAgent

if TYPE_CHECKING:
    from utils.llm_manager import LLMManager

def register(llm_manager: "LLMManager"):
    """Registers the plugin's components."""
    return {
        "agents": {
            "MyAwesomeAgent": MyAwesomeAgent(llm_manager)
        },
        "tools": [
            my_tool
        ]
    }
```

## Creating Tools

A tool is a simple Python function. The function's name and docstring are used by the `MasterAgent` to determine when and how to use the tool. Therefore, it is crucial to have a clear, descriptive name and a detailed docstring.

**Example `tools.py`:**
```python
def my_tool(argument_1: str, argument_2: int) -> str:
    """
    This is a description of what my_tool does.

    Args:
        argument_1: Describes the first argument.
        argument_2: Describes the second argument.

    Returns:
        A string describing the outcome.
    """
    # ... tool logic here ...
    return f"Tool executed with {argument_1} and {argument_2}"
```

## Creating Agents

You can also create specialized agents that inherit from `DeputyAgent`. These agents can be assigned complex tasks by the `MasterAgent`.

**Example `agent.py`:**
```python
import logging
from agents.deputy_agent import DeputyAgent
from utils.llm_manager import LLMManager

class MyAwesomeAgent(DeputyAgent):
    """An agent that does awesome things."""

    def __init__(self, llm_manager: LLMManager):
        super().__init__(llm_manager)
        self.system_prompt = "You are an awesome agent. Your purpose is to be awesome."

    def execute(self, query: str, history=None) -> str:
        """Executes the awesome task."""
        # ... agent logic here ...
        return f"Awesomeness complete for query: {query}"
```
