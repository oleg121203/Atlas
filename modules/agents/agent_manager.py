import importlib.util
import inspect
import os
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from modules.agents.tool_creator_agent import ToolCreatorAgent
from utils.llm_manager import LLMManager
from utils.logger import get_logger

if TYPE_CHECKING:
    from modules.agents.memory_manager import MemoryManager
    from modules.agents.enhanced_memory_manager import EnhancedMemoryManager

class ToolNotFoundError(Exception):
    """Raised when a specified tool cannot be found."""

class InvalidToolArgumentsError(Exception):
    """Raised when the arguments provided to a tool are invalid."""


class AgentManager:
    """Manages the registration, retrieval, and execution of agents and tools.

    Attributes:
        _agents (Dict[str, Any]): Registered agents
        _tools (Dict[str, Dict[str, Any]]): Registered tools with their metadata
        llm_manager (LLMManager): Language model manager
        memory_manager (Union[MemoryManager, EnhancedMemoryManager]): Memory management system
        master_agent_update_callback (Optional[Callable]): Callback for master agent updates
        _generated_tools (List[str]): List of dynamically generated tools
    """

    def __init__(self, 
                 llm_manager: LLMManager, 
                 memory_manager: Union["MemoryManager", "EnhancedMemoryManager"], 
                 master_agent_update_callback: Optional[Callable] = None):
        """Initialize the AgentManager.

        Args:
            llm_manager (LLMManager): Language model manager
            memory_manager (Union[MemoryManager, EnhancedMemoryManager]): Memory management system
            master_agent_update_callback (Optional[Callable]): Callback for master agent updates
        """
        self._agents: Dict[str, Any] = {}
        self._tools: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger()
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.master_agent_update_callback = master_agent_update_callback
        self.plugin_manager: Optional[Any] = None  # Will be set later to avoid circular dependency

        # Keep track of which tools are dynamically loaded
        self._generated_tools: List[str] = []

        # Initialize and register the ToolCreatorAgent's create_tool method
        self.tool_creator = ToolCreatorAgent(
            llm_manager=self.llm_manager, 
            memory_manager=self.memory_manager
        )
        self.add_tool(
            "create_tool", 
            self.tool_creator.create_tool, 
            "Creates a new Python tool function from a description, saves it to a file, and makes it available for use."
        )

        # Load tools from the generated directory
        self.reload_generated_tools()

        # Load built-in tools
        self.load_builtin_tools()

    @property
    def has_agents(self) -> bool:
        """Returns True if there are any registered agents."""
        return bool(self._agents)

    def clear_tools(self):
        """Clears all registered tools except the essential ones."""
        #Preserve essential tools if needed, or clear completely
        #For now, let's assume we clear and re-add the most basic tool
        self.tools = {}
        self.tool_descriptions = {}
        self.logger.info("All tools have been cleared from the AgentManager.")

        #Re-register the essential 'create_tool'
        from modules.agents.tool_creator_agent import ToolCreatorAgent
        tool_creator = ToolCreatorAgent(self.llm_manager, self.memory_manager)
        self.add_tool(
            "create_tool",
            tool_creator.create_tool,
            tool_creator.create_tool.__doc__,
        )

        #Reload generated tools after clearing
        self.reload_generated_tools()

        #Reload built-in tools after clearing
        self.load_builtin_tools()

    def reload_generated_tools(self, directory: str = "tools/generated"):
        """Clears and reloads all tool functions from a specified directory."""
        self.logger.info(f"Reloading generated tools from '{directory}'...")
        start_time = time.perf_counter()

        #Unregister all previously loaded generated tools
        for tool_name in self._generated_tools:
            if tool_name in self._tools:
                del self._tools[tool_name]
        self._generated_tools.clear()

        if not os.path.exists(directory):
            self.logger.warning(f"Generated tools directory not found: {directory}")
            return

        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                file_path = os.path.join(directory, filename)
                module_name = f"tools.generated.{filename[:-3]}"

                try:
                    tool_load_start_time = time.perf_counter()
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        for name, func in inspect.getmembers(module, inspect.isfunction):
                            if not name.startswith("_"):
                                self.add_tool(name, func)
                                self._generated_tools.append(name)
                                tool_load_end_time = time.perf_counter()
                                duration = tool_load_end_time - tool_load_start_time
                                if 'metrics_manager_instance' in globals():
                                    metrics_manager_instance.record_tool_load_time(name, duration)
                                self.logger.info(f"Dynamically loaded and registered tool: '{name}' from {filename} in {duration:.4f}s")
                                break
                except (SyntaxError, ImportError, AttributeError, Exception) as e:
                    self.logger.error(f"Failed to load tool from {file_path} due to an error: {e}. Skipping this file.", exc_info=True)

        #Notify the master agent that the tool list has been updated
        end_time = time.perf_counter()
        self.logger.info(f"Finished reloading tools in {end_time - start_time:.4f} seconds.")

        #Notify the master agent that the tool list has been updated
        if self.master_agent_update_callback:
            self.logger.info("Notifying MasterAgent of tool updates.")
            self.master_agent_update_callback()

    def add_agent(self, name: str, agent_instance: Any) -> None:
        """Registers a new agent."""
        self._agents[name] = agent_instance
        self.logger.info(f"Registered agent: {name}")

    def get_agent(self, name: str):
        """Return a registered agent by name or *None* if not present (legacy helper)."""
        return self._agents.get(name)

    def add_tool(self, 
                 name: str, 
                 tool_function: Callable, 
                 description: Optional[str] = None, 
                 silent_overwrite: bool = False) -> None:
        """Registers a new tool function.

        Args:
            name (str): Tool name
            tool_function (Callable): Tool implementation function
            description (Optional[str]): Tool description
            silent_overwrite (bool): Whether to silently overwrite existing tool
        """
        if name in self._tools:
            if not silent_overwrite:
                self.logger.warning(f"Tool '{name}' is already registered. It will be overwritten.")

        # Store the function and its description (or docstring)
        doc = description or inspect.getdoc(tool_function) or "No description available"

        self._tools[name] = {
            "function": tool_function,
            "doc": doc,
            "name": name
        }
        self.logger.info(f"Registered tool: {name}")

        # Notify master agent if callback is set
        if self.master_agent_update_callback:
            self.master_agent_update_callback()

    def get_tool_list_string(self) -> str:
        """Returns a formatted string of available tools and their docstrings for the LLM prompt."""
        tool_docs = []
        for name, tool_data in self._tools.items():
            docstring = tool_data.get("doc")
            if docstring:
                #Clean up the docstring
                clean_doc = " ".join(docstring.split())
                tool_docs.append(f"- {name}: {clean_doc}")
            else:
                tool_docs.append(f"- {name}: No description available.")
        return "\n".join(tool_docs)

    def execute_tool(self, 
                 tool_name: str, 
                 args: Dict[str, Any]) -> Any:
        """Executes a specified tool with the given arguments.

        Args:
            tool_name (str): Name of the tool to execute
            args (Dict[str, Any]): Arguments for the tool

        Returns:
            Any: Result of the tool execution

        Raises:
            ToolNotFoundError: If the tool is not found
            InvalidToolArgumentsError: If arguments are invalid
        """
        self.logger.info(f"Executing tool: {tool_name} with args: {args}")
        if tool_name not in self._tools:
            self.logger.error(f"Tool '{tool_name}' not found.")
            raise ToolNotFoundError(f"Tool '{tool_name}' not found. You can try to create it using 'create_tool'.")

        tool_info = self._tools[tool_name]
        func = tool_info["function"]
        func_spec = inspect.getfullargspec(func)

        try:
            # Validate arguments against function signature
            if func_spec.args and not func_spec.varargs:
                for arg_name in args:
                    if arg_name not in func_spec.args:
                        self.logger.warning(f"Argument '{arg_name}' is not a valid argument for tool '{tool_name}'.")
                        raise InvalidToolArgumentsError(
                            f"Argument '{arg_name}' is not a valid argument for tool '{tool_name}'"
                        )
            
            result = func(**args)
            return result
        except TypeError as e:
            self.logger.error(f"Invalid arguments for tool {tool_name}: {e}", exc_info=True)
            tool_doc = tool_info.get("doc", "No documentation available.")
            raise InvalidToolArgumentsError(
                f"Invalid arguments for tool '{tool_name}'. Error: {e}.\n"
                f"Tool documentation: '{tool_doc}'.\n"
                f"Please check the arguments and try again.",
            )
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            raise

    def get_all_agents(self) -> Dict[str, Any]:
        """Returns a dictionary of all registered agents."""
        return self._agents

    def get_tool_names(self) -> List[str]:
        """Returns a list of the names of all registered tools."""
        return list(self._tools.keys())

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Generates a list of schemas for all available tools."""
        schemas = []
        for tool_name, tool_info in self._tools.items():
            func = tool_info['function']
            try:
                sig = inspect.signature(func)
                params = []
                for param in sig.parameters.values():
                    param_info = {
                        "name": param.name,
                        "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any',
                        "required": param.default == inspect.Parameter.empty
                    }
                    params.append(param_info)
                
                schema = {
                    "name": tool_name,
                    "description": tool_info['doc'],
                    "arguments": params
                }
                schemas.append(schema)
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Could not generate schema for tool '{tool_name}': {e}")
        return schemas

    def get_generated_tools_details(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionaries with details about each generated tool."""
        details = []
        for tool_name in self._generated_tools:
            if tool_name in self._tools:
                tool_data = self._tools[tool_name]
                file_path = os.path.join("tools", "generated", f"{tool_name}.py")
                details.append({
                    "name": tool_name,
                    "doc": tool_data.get("doc", "No description available."),
                    "file_path": file_path,
                })
        return details

    def delete_tool(self, tool_name: str, file_path: str):
        """Deletes a tool's file and unregisters it."""
        self.logger.info(f"Attempting to delete tool '{tool_name}' from {file_path}")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Successfully deleted tool file: {file_path}")
            else:
                self.logger.warning(f"Tool file not found at {file_path}, cannot delete.")

            if tool_name in self._tools:
                del self._tools[tool_name]

            if tool_name in self._generated_tools:
                self._generated_tools.remove(tool_name)

            #Notify the master agent of the change
            if self.master_agent_update_callback:
                self.logger.info("Notifying MasterAgent of tool updates.")
                self.master_agent_update_callback()

        except Exception as e:
            self.logger.error(f"Error deleting tool '{tool_name}': {e}", exc_info=True)

    def load_builtin_tools(self):
        """Load built-in tools from the tools directory."""
        self.logger.info("Loading built-in tools...")

        #Import and register built-in tools
        try:
            #Screenshot tool
            from tools.screenshot_tool import capture_screen
            self.add_tool("capture_screen", capture_screen, "Capture a screenshot of the screen and save it to a file")

            #Clipboard tool
            from tools.clipboard_tool import (
                clear_clipboard,
                get_clipboard_image,
                get_clipboard_text,
                set_clipboard_image,
                set_clipboard_text,
            )
            self.add_tool("get_clipboard_text", get_clipboard_text, "Get text content from clipboard")
            self.add_tool("set_clipboard_text", set_clipboard_text, "Set text content to clipboard")
            self.add_tool("get_clipboard_image", get_clipboard_image, "Get image content from clipboard")
            self.add_tool("set_clipboard_image", set_clipboard_image, "Set image content to clipboard")
            self.add_tool("clear_clipboard", clear_clipboard, "Clear clipboard content")

            #Mouse and keyboard tool
            from tools.mouse_keyboard_tool import (
                click_at,
                move_mouse,
                press_key,
                type_text,
            )
            self.add_tool("click_at", click_at, "Click mouse at specified coordinates")
            self.add_tool("move_mouse", move_mouse, "Move mouse to specified coordinates")
            self.add_tool("type_text", type_text, "Type text using keyboard")
            self.add_tool("press_key", press_key, "Press a specific key")

            #OCR tool
            from tools.ocr_tool import ocr_file, ocr_image
            self.add_tool("ocr_image", ocr_image, "Extract text from an image using OCR")
            self.add_tool("ocr_file", ocr_file, "Extract text from an image file using OCR")

            #Image recognition tool
            from tools.image_recognition_tool import (
                find_object_in_image,
                find_template_in_image,
            )
            self.add_tool("find_template_in_image", find_template_in_image, "Find a template image within a larger image")
            self.add_tool("find_object_in_image", find_object_in_image, "Find objects in an image using cascade classifier")

            #Terminal tool
            from tools.terminal_tool import (
                change_directory,
                execute_command,
                execute_script,
                get_environment,
                kill_process,
            )
            self.add_tool("execute_command", execute_command, "Execute a shell command")
            self.add_tool("execute_script", execute_script, "Execute a script file")
            self.add_tool("get_environment", get_environment, "Get environment variables")
            self.add_tool("change_directory", change_directory, "Change working directory")
            self.add_tool("kill_process", kill_process, "Kill a process by PID")

            #Notification tool
            from tools.notification_tool import NotificationManager
            notif_manager = NotificationManager()
            self.add_tool("send_email", notif_manager.send_email, "Send an email notification")
            self.add_tool("send_telegram", notif_manager.send_telegram, "Send a Telegram notification")
            self.add_tool("send_sms", notif_manager.send_sms, "Send an SMS notification")



            #Translation tool (for internal use, not exposed to user directly)
            from tools.translation_tool import create_translation_tool
            translation_tool = create_translation_tool(self.llm_manager)
            self.add_tool("translate_text", translation_tool.translate_with_llm, "Translate text between languages")
            self.add_tool("detect_language", translation_tool.detect_language, "Detect the language of input text")

            #Count only the actual built-in tools
            builtin_tool_count = len([name for name in self._tools.keys() if name in [
                "capture_screen", "get_clipboard_text", "set_clipboard_text", "get_clipboard_image",
                "set_clipboard_image", "clear_clipboard", "click_at", "move_mouse", "type_text",
                "press_key", "ocr_image", "ocr_file", "find_template_in_image", "find_object_in_image",
                "execute_command", "execute_script", "get_environment", "change_directory",
                "kill_process", "send_email", "send_telegram", "send_sms", "translate_text", "detect_language",
                "open_url",
            ]])

            self.logger.info(f"Successfully loaded {builtin_tool_count} built-in tools")

        except Exception as e:
            self.logger.error(f"Error loading built-in tools: {e}", exc_info=True)

    def get_all_tools_details(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionaries with details about all tools (built-in, generated, plugin, and superhuman)."""
        details = []

        #Add generated tools
        for tool_name in self._generated_tools:
            if tool_name in self._tools:
                tool_func = self._tools[tool_name]
                file_path = os.path.join("tools", "generated", f"{tool_name}.py")
                details.append({
                    "name": tool_name,
                    "doc": getattr(tool_func, "__doc__", "Generated tool - no description available."),
                    "file_path": file_path,
                    "type": "generated",
                    "source": "User generated",
                })

        #Add built-in tools
        builtin_tools = {
            "capture_screen": "Screenshot Tool",
            "get_clipboard_text": "Clipboard Tool",
            "set_clipboard_text": "Clipboard Tool",
            "get_clipboard_image": "Clipboard Tool",
            "set_clipboard_image": "Clipboard Tool",
            "clear_clipboard": "Clipboard Tool",
            "click_at": "Mouse & Keyboard Tool",
            "move_mouse": "Mouse & Keyboard Tool",
            "type_text": "Mouse & Keyboard Tool",
            "press_key": "Mouse & Keyboard Tool",
            "ocr_image": "OCR Tool",
            "ocr_file": "OCR Tool",
            "find_template_in_image": "Image Recognition Tool",
            "find_object_in_image": "Image Recognition Tool",
            "execute_command": "Terminal Tool",
            "execute_script": "Terminal Tool",
            "get_environment": "Terminal Tool",
            "change_directory": "Terminal Tool",
            "kill_process": "Terminal Tool",
            "send_email": "Notification Tool",
            "send_telegram": "Notification Tool",
            "send_sms": "Notification Tool",
            "translate_text": "Translation Tool",
            "detect_language": "Translation Tool",
            "open_url": "Web Browser Tool",
        }

        for tool_name, tool_category in builtin_tools.items():
            if tool_name in self._tools:
                tool_func = self._tools[tool_name]
                details.append({
                    "name": tool_name,
                    "doc": getattr(tool_func, "__doc__", f"Built-in {tool_category} - no description available."),
                    "file_path": f"tools/{tool_name.split('_')[0]}_tool.py",
                    "type": "built-in",
                    "source": tool_category,
                })

        #Add essential tools
        essential_tools = ["create_tool"]
        for tool_name in essential_tools:
            if tool_name in self._tools and tool_name not in [t["name"] for t in details]:
                tool_func = self._tools[tool_name]
                details.append({
                    "name": tool_name,
                    "doc": getattr(tool_func, "__doc__", "Essential tool for creating new tools."),
                    "file_path": "agents/tool_creator_agent.py",
                    "type": "essential",
                    "source": "Tool Creator Agent",
                })

        #Add plugin tools
        if self.plugin_manager:
            try:
                for plugin_name, plugin_data in self.plugin_manager.get_all_plugins().items():
                    plugin_tools = plugin_data.get("tools", [])
                    for tool_func in plugin_tools:
                        #Now tools should be functions with __name__ attribute
                        if hasattr(tool_func, "__name__"):
                            tool_name = tool_func.__name__
                            if tool_name not in self._tools or tool_name not in [t["name"] for t in details if t["type"] != "essential"]:
                                details.append({
                                    "name": tool_name,
                                    "doc": getattr(tool_func, "__doc__", f"Plugin tool from {plugin_name}"),
                                    "file_path": f"plugins/{plugin_name}",
                                    "type": "plugin",
                                    "source": "Plugin Manager",
                                })
            except Exception as e:
                self.logger.warning(f"Error processing plugin tools for UI display: {e}")

        # Add superhuman tools (creative, proactive, playful)
        try:
            from tools.creative_tool import CreativeTool
            from tools.proactive_tool import ProactiveTool
            from tools.playful_tool import PlayfulTool
            superhuman_tools = [CreativeTool(), ProactiveTool(), PlayfulTool()]
            for tool in superhuman_tools:
                details.append({
                    "name": tool.name,
                    "doc": tool.__doc__ or tool.description,
                    "file_path": f"tools/{tool.name}.py",
                    "type": "superhuman",
                    "source": "Atlas Superhuman Module",
                    "capabilities": getattr(tool, "capabilities", []),
                })
        except Exception as e:
            self.logger.warning(f"Could not load superhuman tools: {e}")

        #Debug: Print tool counts for troubleshooting
        generated_count = len([d for d in details if d["type"] == "generated"])
        builtin_count = len([d for d in details if d["type"] == "built-in"])
        essential_count = len([d for d in details if d["type"] == "essential"])
        plugin_count = len([d for d in details if d["type"] == "plugin"])

        self.logger.info(f"Tool UI details: {builtin_count} built-in, {generated_count} generated, {essential_count} essential, {plugin_count} plugin tools")

        return details

    def set_plugin_manager(self, plugin_manager):
        """Set the plugin manager after initialization to avoid circular dependency."""
        self.plugin_manager = plugin_manager

    def parse_and_execute_request(self, request: str) -> Any:
        """
        Parse a user request and execute the appropriate tool chain for system/app control.
        Uses simple rules/keywords for now.
        Args:
            request: User request as a string.
        Returns:
            Results of tool chain execution.
        """
        request_lower = request.lower()
        tool_chain = []
        # Simple rules for demo
        if "mute" in request_lower:
            tool_chain.append({"tool": "system_event", "args": {"event": "mute"}})
        if "unmute" in request_lower:
            tool_chain.append({"tool": "system_event", "args": {"event": "unmute"}})
        if "sleep" in request_lower:
            tool_chain.append({"tool": "system_event", "args": {"event": "sleep"}})
        if "open" in request_lower:
            # Try to extract app name
            words = request_lower.split()
            idx = words.index("open") if "open" in words else -1
            if idx != -1 and idx+1 < len(words):
                app = words[idx+1].capitalize()
                tool_chain.append({"tool": "system_event", "args": {"event": "open_app", "app_name": app}})
        if "set volume to" in request_lower:
            try:
                vol = int(request_lower.split("set volume to")[-1].split()[0])
                tool_chain.append({"tool": "system_event", "args": {"event": "set_volume", "value": vol}})
            except Exception:
                pass
        if not tool_chain:
            return {"status": "error", "error": "Could not parse request or no matching tools."}
        # Execute tool chain
        results = []
        for step in tool_chain:
            tool_name = step["tool"]
            args = step["args"]
            result = self.execute_tool(tool_name, args)
            results.append({"tool": tool_name, "args": args, "result": result})
        return {"status": "success", "results": results}
