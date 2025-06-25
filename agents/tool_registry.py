"""
Tool Registry for Atlas System

Centralized tool management to avoid incorrect tool assignments.
"""

from typing import Dict, List, Any, Optional
import logging
from enum import Enum
from .email_strategy_manager import email_strategy_manager

class ToolCategory(Enum):
    """Tool categories for proper assignment."""
    EMAIL = "email"
    BROWSER = "browser"
    SCREENSHOT = "screenshot"
    SEARCH = "search"
    CLIPBOARD = "clipboard"
    TERMINAL = "terminal"
    GENERIC = "generic"

class ToolRegistry:
    """Centralized tool registry for proper tool assignment."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[ToolCategory, List[str]] = {
            category: [] for category in ToolCategory
        }
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools with proper categorization."""
        
        # Email tools
        self.register_tool(
            name="EmailFilter",
            category=ToolCategory.EMAIL,
            description="Filter and search emails using Gmail API",
            keywords=["email", "gmail", "mail", "search", "filter"],
            priority=1
        )
        
        self.register_tool(
            name="EmailAnalytics", 
            category=ToolCategory.EMAIL,
            description="Analyze email patterns and statistics",
            keywords=["email", "analytics", "statistics", "patterns"],
            priority=2
        )
        
        self.register_tool(
            name="EmailAutomation",
            category=ToolCategory.EMAIL,
            description="Automate email workflows and templates",
            keywords=["email", "automation", "workflow", "template"],
            priority=3
        )
        
        # Browser tools
        self.register_tool(
            name="BrowserTool",
            category=ToolCategory.BROWSER,
            description="General web browser automation",
            keywords=["browser", "safari", "chrome", "navigate", "web"],
            priority=1
        )
        
        # Screenshot tools
        self.register_tool(
            name="screenshot_tool",
            category=ToolCategory.SCREENSHOT,
            description="Capture and analyze screenshots",
            keywords=["screenshot", "capture", "screen", "image"],
            priority=1
        )
        
        # Search tools
        self.register_tool(
            name="search_tool",
            category=ToolCategory.SEARCH,
            description="General search functionality",
            keywords=["search", "find", "lookup"],
            priority=1
        )
        
        # Clipboard tools
        self.register_tool(
            name="clipboard_tool",
            category=ToolCategory.CLIPBOARD,
            description="Clipboard management",
            keywords=["clipboard", "copy", "paste"],
            priority=1
        )
        
        # Terminal tools
        self.register_tool(
            name="terminal_tool",
            category=ToolCategory.TERMINAL,
            description="Terminal command execution",
            keywords=["terminal", "command", "shell"],
            priority=1
        )
        
        # Generic executor
        self.register_tool(
            name="generic_executor",
            category=ToolCategory.GENERIC,
            description="Generic task executor",
            keywords=["generic", "execute", "task"],
            priority=999  # Lowest priority
        )
        
        # PDF extraction tool
        self.register_tool(
            name="extract_pdf_text",
            category=ToolCategory.GENERIC,
            description="Extract text from a PDF file.",
            keywords=["pdf", "extract", "document", "text"],
            priority=2
        )
        
        # Summarization tool
        self.register_tool(
            name="summarize_text",
            category=ToolCategory.GENERIC,
            description="Summarize input text (first 3 sentences).",
            keywords=["summarize", "summary", "text", "document"],
            priority=2
        )
        
        # Meme caption tool
        self.register_tool(
            name="add_meme_caption",
            category=ToolCategory.GENERIC,
            description="Overlay a caption on an image to create a meme.",
            keywords=["meme", "caption", "image", "fun"],
            priority=2
        )
        
        # Save image tool
        self.register_tool(
            name="save_image",
            category=ToolCategory.GENERIC,
            description="Save a PIL image object to a file.",
            keywords=["save", "image", "file", "picture"],
            priority=2
        )
        
        # Macro suggestion tool
        self.register_tool(
            name="macro_suggestion",
            category=ToolCategory.GENERIC,
            description="Suggest a macro (sequence of steps) based on recent user actions.",
            keywords=["macro", "automation", "pattern", "suggestion"],
            priority=2
        )
        
        # AppleScript tool
        self.register_tool(
            name="run_applescript",
            category=ToolCategory.GENERIC,
            description="Run an AppleScript command for macOS app/system control.",
            keywords=["applescript", "macos", "automation", "system", "app"],
            priority=1
        )
        
        # Automator/Shortcuts tool
        self.register_tool(
            name="run_automator_or_shortcut",
            category=ToolCategory.GENERIC,
            description="Trigger an Automator workflow or macOS Shortcut by name/path.",
            keywords=["automator", "shortcut", "macos", "workflow", "automation"],
            priority=1
        )
        
        # Accessibility tool
        self.register_tool(
            name="accessibility_action",
            category=ToolCategory.GENERIC,
            description="Simulate a mouse click or keystroke using AppleScript (System Events).",
            keywords=["accessibility", "click", "keystroke", "macos", "automation"],
            priority=1
        )
        
        # System events tool
        self.register_tool(
            name="system_event",
            category=ToolCategory.GENERIC,
            description="Query or trigger common macOS system events (sleep, mute, open app, etc).",
            keywords=["system", "event", "macos", "sleep", "volume", "app", "automation"],
            priority=1
        )
    
    def register_tool(self, name: str, category: ToolCategory, description: str, 
                     keywords: List[str], priority: int = 1):
        """Register a new tool."""
        self.tools[name] = {
            "name": name,
            "category": category,
            "description": description,
            "keywords": keywords,
            "priority": priority
        }
        
        if name not in self.categories[category]:
            self.categories[category].append(name)
    
    def get_tool_for_task(self, task_description: str) -> str:
        """
        Get the most appropriate tool for a given task description.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Tool name that best matches the task
        """
        task_lower = task_description.lower()
        
        # Special handling for email tasks - use Email Strategy Manager
        if any(keyword in task_lower for keyword in ["email", "gmail", "mail"]):
            method = email_strategy_manager.select_access_method(task_description)
            if method:
                tool_name = email_strategy_manager.get_tool_for_method(method)
                self.logger.info(f"Email Strategy Manager selected {method.value} -> {tool_name}")
                return tool_name
        
        # Regular tool scoring for non-email tasks
        scores: Dict[str, float] = {}
        
        # Score each tool based on keyword matches
        for tool_name, tool_info in self.tools.items():
            score = 0.0
            
            # Check keyword matches
            for keyword in tool_info["keywords"]:
                if keyword in task_lower:
                    score += 1.0
            
            # Bonus for exact matches
            if tool_info["name"].lower() in task_lower:
                score += 2.0
            
            # Apply priority (lower priority number = higher score)
            score += (10 - tool_info["priority"]) * 0.1
            
            scores[tool_name] = score
        
        # Find the tool with highest score
        if scores:
            best_tool = max(scores.items(), key=lambda x: x[1])[0]
            if scores[best_tool] > 0:
                self.logger.info(f"Selected tool '{best_tool}' for task: {task_description}")
                return best_tool
        
        # Fallback to generic executor
        self.logger.warning(f"No specific tool found for task: {task_description}, using generic_executor")
        return "generic_executor"
    
    def get_tools_by_category(self, category: ToolCategory) -> List[str]:
        """Get all tools in a specific category."""
        return self.categories.get(category, [])
    
    def validate_tool_exists(self, tool_name: str) -> bool:
        """Check if a tool exists in the registry."""
        return tool_name in self.tools
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        return self.tools.get(tool_name)
    
    def list_all_tools(self) -> Dict[str, List[str]]:
        """List all tools organized by category."""
        return {category.value: tools for category, tools in self.categories.items()}

# Global tool registry instance
tool_registry = ToolRegistry() 