import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.events import NEW_TOOL_REGISTERED, TOOL_ERROR, TOOL_EXECUTED
from ui.module_communication import EVENT_BUS


class SelfRegenerationManager:
    """Manages self-regeneration processes to detect and fix issues in the Atlas system."""

    def __init__(self, project_root: str):
        self.logger = logging.getLogger(__name__)
        self.project_root = Path(project_root)
        self.fixes_applied: List[Dict[str, Any]] = []
        self.issue_types = [
            "missing_module",  # Missing module
            "missing_class",  # Missing class
            "missing_method",  # Missing method
            "missing_tool_file",  # Missing tool file
            "missing_plugin",  # Missing plugin
            "missing_config",  # Missing configuration file
            "class_not_found",  # Class not found
        ]
        self.logger.info(
            "SelfRegenerationManager initialized with project root: %s", project_root
        )

    def detect_and_fix_issues(self) -> Dict[str, Any]:
        """Detect issues in the system and attempt to fix them."""
        self.logger.info("Starting system self-diagnosis and regeneration...")
        issues = self._detect_issues()
        fixes = self._apply_fixes(issues)
        result = {
            "issues_detected": len(issues),
            "fixes_applied": len(fixes),
            "system_health": "repaired"
            if fixes
            else "healthy"
            if not issues
            else "needs_attention",
            "issues": issues,
            "fixes": fixes,
        }
        self.logger.info("Self-regeneration completed: %d fixes applied", len(fixes))
        return result

    def _detect_issues(self) -> List[Dict[str, Any]]:
        """Detect various types of issues in the system."""
        issues = []

        # Check for missing imports
        import_issues = self._detect_import_issues()
        issues.extend(import_issues)

        # Check for missing methods
        method_issues = self._detect_missing_methods()
        issues.extend(method_issues)

        # Check for broken tools
        tool_issues = self._detect_broken_tools()
        issues.extend(tool_issues)

        # Check for missing plugins
        plugin_issues = self._detect_missing_plugins()
        issues.extend(plugin_issues)

        # Check for configuration issues
        config_issues = self._detect_config_issues()
        issues.extend(config_issues)

        return issues

    def _apply_fixes(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply fixes for detected issues."""
        fixes = []

        for issue in issues:
            fix = self._fix_issue(issue)
            if fix:
                fixes.append(fix)
                self.fixes_applied.append(fix)

        return fixes

    def _detect_import_issues(self) -> List[Dict[str, Any]]:
        """Detect issues with missing imports."""
        # Placeholder for import issue detection logic
        return []

    def _detect_missing_methods(self) -> List[Dict[str, Any]]:
        """Detect missing methods in classes."""
        # Placeholder for missing method detection logic
        return []

    def _detect_broken_tools(self) -> List[Dict[str, Any]]:
        """Detect issues with broken or missing tools."""
        # Placeholder for broken tool detection logic
        return []

    def _detect_missing_plugins(self) -> List[Dict[str, Any]]:
        """Detect missing plugins."""
        # Placeholder for missing plugin detection logic
        return []

    def _detect_config_issues(self) -> List[Dict[str, Any]]:
        """Detect issues with configuration files."""
        # Placeholder for configuration issue detection logic
        return []

    def _fix_issue(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt to fix a specific issue based on its type."""
        issue_type = issue.get("type")
        if issue_type == "missing_plugin":
            return self._fix_missing_plugin(issue)
        elif issue_type == "missing_config":
            return self._fix_missing_config(issue)
        elif issue_type == "missing_method":
            return self._fix_missing_method(issue)
        elif issue_type == "missing_tool_file":
            return self._fix_missing_tool_file(issue)
        else:
            self.logger.warning("No fix available for issue type: %s", issue_type)
            return None

    def _fix_missing_plugin(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fix a missing plugin by creating necessary directories and files."""
        plugin_path = self.project_root / issue.get("plugin", "")

        # Create plugin directory
        plugin_path.mkdir(parents=True, exist_ok=True)

        # Create basic plugin files
        (plugin_path / "__init__.py").touch()

        plugin_json = {
            "name": issue.get("plugin", "").split("/")[-1],
            "version": "1.0.0",
            "description": "Auto-generated plugin",
            "author": "Atlas Self-Regeneration",
            "enabled": True,
        }

        with open(plugin_path / "plugin.json", "w") as f:
            import json

            json.dump(plugin_json, f, indent=2)

        return {
            "issue": issue,
            "fix_type": "plugin_created",
            "plugin": str(plugin_path),
            "success": True,
        }

    def _fix_missing_config(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fix a missing configuration file by generating a basic one."""
        config_path = self.project_root / issue.get("file", "")

        # Create configuration directory
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate basic configuration
        config_content = """[DEFAULT]
# Auto-generated configuration file
# Generated by Atlas Self-Regeneration Manager

[providers]
default = groq

[models]
groq = llama3-8b-8192

[api_keys]
# Add your API keys here
"""

        with open(config_path, "w") as f:
            f.write(config_content)

        return {
            "issue": issue,
            "fix_type": "config_created",
            "file": str(config_path),
            "success": True,
        }

    def _fix_missing_method(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fix a missing method by dynamically adding it to the class."""
        class_path = issue.get("class", "")
        method_name = issue.get("method", "")

        try:
            module_name, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            class_obj = getattr(module, class_name)

            # Generate method code based on class and method name
            method_code = self._generate_method_code(class_name, method_name)

            # Add method to class
            exec(method_code, {class_name: class_obj})

            return {
                "issue": issue,
                "fix_type": "method_added",
                "method": method_name,
                "class": class_path,
                "success": True,
            }
        except Exception as e:
            return {
                "issue": issue,
                "fix_type": "method_added",
                "method": method_name,
                "class": class_path,
                "success": False,
                "error": str(e),
            }

    def _fix_missing_tool_file(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fix a missing tool file by creating it with basic content."""
        file_path = self.project_root / issue.get("file", "")

        # Create tool directory
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate tool content
        content = self._generate_tool_file_content(str(file_path))

        with open(file_path, "w") as f:
            f.write(content)

        return {
            "issue": issue,
            "fix_type": "tool_file_created",
            "file": str(file_path),
            "success": True,
        }

    def _generate_method_code(self, class_name: str, method_name: str) -> str:
        """
        Generate code for a missing method.

        Args:
            class_name (str): Name of the class.
            method_name (str): Name of the method to generate.

        Returns:
            str: Generated method code.
        """
        return f"""
def {method_name}(self, *args, **kwargs):
    \"\"\"Auto-generated method.\"\"\"
    self.logger.info(\"Executing auto-generated method {method_name}\")
    return {{"status": "auto-generated", "method": "{method_name}"}}"""

    def _generate_browser_tool_content(self, tool_name: str) -> str:
        """Generate content for a browser-related tool."""
        return f"""import logging\nfrom typing import Any, Dict\n\n\nclass BrowserTool:\n    \"\"Browser automation tool.\"\"\n    def __init__(self):\n        self.logger = logging.getLogger(__name__)\n    def open_url(self, url: str) -> Dict[str, Any]:\n        \"\"Open URL in browser.\"\"\n        self.logger.info(f\"Opening URL: {{url}}\")\n        return {{"status": "success", "url": url}}\n\n\n# Instantiate the tool\ntool = BrowserTool()\n"""

    def _generate_generic_tool_content(self, tool_name: str) -> str:
        """Generate content for a generic tool."""
        return f"""import logging\nfrom typing import Any, Dict\n\n\nclass GenericTool:\n    \"\"Generic tool placeholder.\"\"\n    def __init__(self):\n        self.logger = logging.getLogger(__name__)\n    def execute(self, *args, **kwargs) -> Dict[str, Any]:\n        \"\"Execute the tool with given parameters.\"\"\n        self.logger.info(f\"Executing tool {tool_name}\")\n        return {{"status": "success", "tool": \"{tool_name}\"}}\n\n\n# Instantiate the tool\ntool = GenericTool()\n"""

    def _generate_tool_file_content(self, file_path: str) -> str:
        """Generate content for a missing tool file."""
        if "browser" in file_path:
            return self._generate_browser_tool_content(file_path)
        return self._generate_generic_tool_content(file_path)

    def execute_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool with the given parameters."""
        self.logger.info(f"Executing tool {tool_name} with parameters {parameters}")
        if tool_name == "create_module":
            return self.create_module_tool(parameters)
        elif tool_name == "create_class":
            return self.create_class_tool(parameters)
        elif tool_name == "create_method":
            return self.create_method_tool(parameters)
        elif tool_name == "create_tool":
            return self.create_tool_tool(parameters)
        elif tool_name == "create_plugin":
            return self.create_plugin_tool(parameters)
        elif tool_name == "create_config":
            return self.create_config_tool(parameters)
        else:
            self.logger.error(f"Unknown tool: {tool_name}")
            return {"success": False, "message": f"Unknown tool: {tool_name}"}

    def create_module_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a tool for generating a missing module.

        Args:
            parameters (Dict[str, Any]): Dictionary containing 'module_name'.

        Returns:
            Dict[str, Any]: Result of the tool creation process.
        """
        module_name = parameters.get("module_name", "")
        self.logger.info(f"Creating tool for missing module: {module_name}")
        try:
            tool_code = f"""
# Auto-generated tool for creating module: {module_name}
def create_module_{module_name}():
    import os
    module_path = os.path.join('modules', '{module_name}.py')
    with open(module_path, 'w') as f:
        f.write('# Auto-generated module')
    return f"Module {module_name} created at {{module_path}}"
"""
            self._run_tool_code(tool_code, f"create_module_{module_name}")
            return {
                "success": True,
                "message": f"Tool for module {module_name} created",
            }
        except Exception as e:
            self.logger.error(
                f"Error creating module tool for {module_name}: {e}", exc_info=True
            )
            return {
                "success": False,
                "message": f"Error creating tool for module {module_name}: {str(e)}",
            }

    def create_class_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a tool for generating a missing class in a module.

        Args:
            parameters (Dict[str, Any]): Dictionary containing 'class_name' and 'module_name'.

        Returns:
            Dict[str, Any]: Result of the tool creation process.
        """
        class_name = parameters.get("class_name", "")
        module_name = parameters.get("module_name", "")
        self.logger.info(
            f"Creating tool for missing class: {class_name} in module: {module_name}"
        )
        try:
            tool_code = f"""
# Auto-generated tool for creating class: {class_name} in module: {module_name}
def create_class_{class_name}():
    import os
    module_path = os.path.join('modules', '{module_name}.py')
    with open(module_path, 'a') as f:
        f.write('\n\nclass {class_name}:\n    pass\n')
    return f"Class {class_name} added to module {module_name} at {{module_path}}"
"""
            self._run_tool_code(tool_code, f"create_class_{class_name}")
            return {"success": True, "message": f"Tool for class {class_name} created"}
        except Exception as e:
            self.logger.error(
                f"Error creating class tool for {class_name}: {e}", exc_info=True
            )
            return {
                "success": False,
                "message": f"Error creating tool for class {class_name}: {str(e)}",
            }

    def create_method_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a tool for generating a missing method in a class.

        Args:
            parameters (Dict[str, Any]): Dictionary containing 'method_name', 'class_name', and 'module_name'.

        Returns:
            Dict[str, Any]: Result of the tool creation process.
        """
        method_name = parameters.get("method_name", "")
        class_name = parameters.get("class_name", "")
        module_name = parameters.get("module_name", "")
        self.logger.info(
            f"Creating tool for missing method: {method_name} in class: {class_name}, module: {module_name}"
        )
        try:
            tool_code = f"""
# Auto-generated tool for creating method: {method_name} in class: {class_name}
def create_method_{method_name}():
    import os
    module_path = os.path.join('modules', '{module_name}.py')
    with open(module_path, 'a') as f:
        f.write('\n    def {method_name}(self):\n        pass\n')
    return f"Method {method_name} added to class {class_name} in module {module_name} at {{module_path}}"
"""
            self._run_tool_code(tool_code, f"create_method_{method_name}")
            return {
                "success": True,
                "message": f"Tool for method {method_name} created",
            }
        except Exception as e:
            self.logger.error(
                f"Error creating method tool for {method_name}: {e}", exc_info=True
            )
            return {
                "success": False,
                "message": f"Error creating tool for method {method_name}: {str(e)}",
            }

    def create_tool_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a tool for generating a missing tool.

        Args:
            parameters (Dict[str, Any]): Dictionary containing 'tool_name'.

        Returns:
            Dict[str, Any]: Result of the tool creation process.
        """
        tool_name = parameters.get("tool_name", "")
        self.logger.info(f"Creating tool for missing tool: {tool_name}")
        try:
            tool_code = f"""
# Auto-generated tool for creating tool: {tool_name}
def create_tool_{tool_name}():
    import os
    tool_path = os.path.join('tools', '{tool_name}.py')
    with open(tool_path, 'w') as f:
        f.write('# Auto-generated tool')
    return f"Tool {tool_name} created at {{tool_path}}"
"""
            self._run_tool_code(tool_code, f"create_tool_{tool_name}")
            self.add_tool(tool_name)
            return {"success": True, "message": f"Tool for tool {tool_name} created"}
        except Exception as e:
            self.logger.error(
                f"Error creating tool tool for {tool_name}: {e}", exc_info=True
            )
            return {
                "success": False,
                "message": f"Error creating tool for tool {tool_name}: {str(e)}",
            }

    def create_plugin_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a tool for generating a missing plugin.

        Args:
            parameters (Dict[str, Any]): Dictionary containing 'plugin_name'.

        Returns:
            Dict[str, Any]: Result of the tool creation process.
        """
        plugin_name = parameters.get("plugin_name", "")
        self.logger.info(f"Creating tool for missing plugin: {plugin_name}")
        try:
            tool_code = f"""
# Auto-generated tool for creating plugin: {plugin_name}
def create_plugin_{plugin_name}():
    import os
    plugin_path = os.path.join('plugins', '{plugin_name}.py')
    with open(plugin_path, 'w') as f:
        f.write('# Auto-generated plugin')
    return f"Plugin {plugin_name} created at {{plugin_path}}"
"""
            self._run_tool_code(tool_code, f"create_plugin_{plugin_name}")
            return {
                "success": True,
                "message": f"Tool for plugin {plugin_name} created",
            }
        except Exception as e:
            self.logger.error(
                f"Error creating plugin tool for {plugin_name}: {e}", exc_info=True
            )
            return {
                "success": False,
                "message": f"Error creating tool for plugin {plugin_name}: {str(e)}",
            }

    def create_config_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a tool for generating a missing configuration file.

        Args:
            parameters (Dict[str, Any]): Dictionary containing 'config_name'.

        Returns:
            Dict[str, Any]: Result of the tool creation process.
        """
        config_name = parameters.get("config_name", "")
        self.logger.info(f"Creating tool for missing config: {config_name}")
        try:
            tool_code = f"""
# Auto-generated tool for creating config: {config_name}
def create_config_{config_name}():
    import os
    config_path = os.path.join('configs', '{config_name}.yaml')
    with open(config_path, 'w') as f:
        f.write('# Auto-generated config')
    return f"Config {config_name} created at {{config_path}}"
"""
            self._run_tool_code(tool_code, f"create_config_{config_name}")
            return {
                "success": True,
                "message": f"Tool for config {config_name} created",
            }
        except Exception as e:
            self.logger.error(
                f"Error creating config tool for {config_name}: {e}", exc_info=True
            )
            return {
                "success": False,
                "message": f"Error creating tool for config {config_name}: {str(e)}",
            }

    def notify_user(self, message: str) -> None:
        """Notify the user about important repair events."""
        self.logger.info("Notifying user: %s", message)

    def _run_tool_code(self, tool_code: str, tool_name: str) -> None:
        """Run the tool code in a separate context."""
        # Create a new context for the tool code
        tool_context = {}

        # Execute the tool code in the new context
        exec(tool_code, tool_context)

        # Get the tool function from the context
        tool_function = tool_context.get(tool_name)

        # Run the tool function only if it exists
        if tool_function is not None:
            tool_function()
        else:
            self.logger.error(
                f"Tool function {tool_name} not found in the generated code."
            )

    def handle_tool_activation(self, tool_name: str) -> Dict[str, Any]:
        """Handle tool activation from UI signals.

        Args:
            tool_name (str): Name of the tool to activate.

        Returns:
            Dict[str, Any]: Result of the tool activation.
        """
        self.logger.info(f"Tool activated from UI: {tool_name}")
        result = self.execute_tool(tool_name, parameters={})
        # Публікуємо подію про результат виконання
        if result.get("success", False):
            EVENT_BUS.publish(TOOL_EXECUTED, result)
        else:
            EVENT_BUS.publish(TOOL_ERROR, result)
        return result

    def add_tool(self, tool_name: str) -> None:
        """Register a new tool and publish event."""
        self.logger.info(f"Registering new tool: {tool_name}")
        EVENT_BUS.publish(NEW_TOOL_REGISTERED, {"tool_name": tool_name})

    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool and publish event."""
        self.logger.info(f"Removing tool: {tool_name}")
        EVENT_BUS.publish("ToolRemoved", {"tool_name": tool_name})

    def get_available_tools(self) -> List[str]:
        """Return a list of available tool names (Python files in tools/)."""
        tools_dir = self.project_root.parent / "tools"
        tool_files = [
            f.stem
            for f in tools_dir.glob("*.py")
            if f.is_file() and not f.name.startswith("__") and f.name != "base_tool.py"
        ]
        # Додаємо також згенеровані інструменти, якщо потрібно
        return sorted(tool_files)


# Singleton instance
self_regeneration_manager = SelfRegenerationManager(
    project_root=str(Path(__file__).parent.parent)
)
