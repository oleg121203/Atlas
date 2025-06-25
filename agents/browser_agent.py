"""
Enhanced Browser Agent with plugin integration.
Uses the Advanced Web Browsing Plugin for comprehensive automation.
"""

import re
import webbrowser
from typing import Any, Dict, Optional, Tuple
import logging
import os
import subprocess

from agents.base_agent import BaseAgent


class BrowserAgent(BaseAgent):
    """Enhanced browser agent that integrates with the Advanced Web Browsing Plugin."""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        super().__init__("Browser Control Agent")
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("Browser Control Agent initialized.")
        self.browser_process: Optional[str] = None
        self.web_plugin_available = False
        self.web_plugin = None
        self.preferred_browser = None  # To store user's browser preference
        # Delay plugin check to avoid heavy initialization
        if not hasattr(self, '_plugin_checked'):
            self._check_web_plugin()
            self._plugin_checked = True

    def _check_web_plugin(self) -> None:
        """Check if advanced web browsing plugin is available."""
        try:
            from plugins.unified_browser.plugin import UnifiedBrowserPlugin  # type: ignore
            self.web_plugin = WebBrowsingPlugin()
            self.web_plugin_available = True
            self.logger.info("Advanced web browsing plugin loaded successfully")
        except ImportError:
            self.web_plugin_available = False
            self.web_plugin = None
            self.logger.warning("Advanced web browsing plugin not available")

    def execute_task(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute browser task with enhanced capabilities"""
        context = context or {}
        self.logger.info(f"Executing browser task: {prompt}")
        try:
            if self.web_plugin_available and self.web_plugin:
                # Check if the task can be handled by the advanced plugin
                if any(term in prompt.lower() for term in ["close", "exit", "quit"]):
                    return str(self.web_plugin.close_browser())
                elif any(term in prompt.lower() for term in ["open", "browse", "navigate", "visit", "go to"]):
                    url = self._extract_url(prompt)
                    if url:
                        return str(self.web_plugin.navigate_to_url(url))
                elif any(term in prompt.lower() for term in ["search", "google", "find", "look up"]):
                    query = self._extract_search_query(prompt)
                    if query:
                        return str(self.web_plugin.navigate_to_url(f"https://www.google.com/search?q={query}"))
                elif any(term in prompt.lower() for term in ["click", "select", "press", "tap"]):
                    element = self._extract_element(prompt)
                    if element:
                        return str(self.web_plugin.click_element(element))
                    else:
                        return str(self.web_plugin.click_element(prompt))  # Pass prompt as fallback description
                elif any(term in prompt.lower() for term in ["type", "enter", "input", "write", "fill"]):
                    input_info = self._extract_input_info(prompt)
                    if input_info:
                        field, text = input_info
                        return str(self.web_plugin.fill_form_field(field, text))
                    else:
                        return "I couldn't determine the input field or text to enter. Please provide more details."
                else:
                    # Default to navigating to a URL or complex task execution if plugin supports it
                    try:
                        return str(self.web_plugin.navigate_to_url(prompt))
                    except:
                        return str(getattr(self.web_plugin, 'execute_complex_task', lambda x: "Complex task execution not supported")(prompt))
            else:
                # Fallback to basic browser control without plugin
                if "close" in prompt.lower() or "exit" in prompt.lower() or "quit" in prompt.lower():
                    return self._handle_browser_close(prompt)
                elif any(term in prompt.lower() for term in ["open", "browse", "navigate", "visit", "go to"]):
                    return self._handle_browser_open(prompt)
                elif any(term in prompt.lower() for term in ["search", "google", "find", "look up"]):
                    return self._handle_browser_search(prompt)
                elif any(term in prompt.lower() for term in ["click", "select", "press", "tap"]):
                    return self._handle_click(prompt)
                elif any(term in prompt.lower() for term in ["type", "enter", "input", "write", "fill"]):
                    return self._handle_input(prompt)
                else:
                    return self._handle_default(prompt)
        except Exception as e:
            self.logger.error(f"Error executing browser task '{prompt}': {e}")
            return self._handle_error(prompt, str(e))

    def _handle_browser_open(self, prompt: str) -> str:
        """Handle opening browser with a URL or site."""
        self.logger.info(f"Handling browser open: {prompt}")
        url = self._extract_url(prompt)
        if not url:
            site_name = self._infer_url_from_site_name(prompt)
            if site_name:
                url = site_name
            else:
                url = "https://www.google.com"  # Default if no URL or site inferred
        try:
            browser = self._determine_browser(prompt)
            if os.name == "posix":
                # macOS
                script = f"""
                tell application "{browser}"
                    activate
                    open location "{url}"
                end tell
                """
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
                if result.returncode == 0:
                    self.browser_process = browser
                    return f"Opened {url} in {browser}"
                else:
                    return self._handle_error(prompt, f"Failed to open {browser}: {result.stderr}")
            else:
                # Windows
                webbrowser.get().open(url)
                self.browser_process = browser
                return f"Opened {url} in browser"
        except Exception as e:
            return self._handle_error(prompt, str(e))

    def _handle_browser_search(self, prompt: str) -> str:
        """Handle search in browser."""
        self.logger.info(f"Handling browser search: {prompt}")
        query = self._extract_search_query(prompt)
        url = f"https://www.google.com/search?q={query}"
        try:
            browser = self._determine_browser(prompt)
            if os.name == "posix":
                # macOS
                script = f"""
                tell application "{browser}"
                    activate
                    open location "{url}"
                end tell
                """
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
                if result.returncode == 0:
                    return f"Searched for '{query}' in {browser}"
                else:
                    return self._handle_error(prompt, f"Failed to search in {browser}: {result.stderr}")
            else:
                # Windows
                webbrowser.get().open(url)
                return f"Searched for '{query}' in browser"
        except Exception as e:
            return self._handle_error(prompt, str(e))

    def _handle_browser_close(self, prompt: str) -> str:
        """Handle closing browser."""
        self.logger.info(f"Handling browser close: {prompt}")
        browser = self._determine_browser(prompt)
        try:
            if os.name == "posix":
                # macOS
                script = f"""
                tell application "{browser}"
                    quit
                end tell
                """
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
                if result.returncode == 0:
                    self.browser_process = None
                    return f"Closed {browser}"
                else:
                    return self._handle_error(prompt, f"Failed to close {browser}: {result.stderr}")
            else:
                # Windows - using PowerShell to close browser
                script = f"Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{browser}*' }} | ForEach-Object {{ $_.CloseMainWindow() }}"
                subprocess.run(["powershell", "-Command", script])
                self.browser_process = None
                return f"Closed {browser}"
        except Exception as e:
            return self._handle_error(prompt, str(e))

    def _infer_url_from_site_name(self, prompt: str) -> Optional[str]:
        """Infer URL from site name mentioned in prompt"""
        prompt_lower = prompt.lower()
        
        site_mappings = {
            "github": "https://github.com",
            "google": "https://google.com", 
            "facebook": "https://facebook.com",
            "youtube": "https://youtube.com",
            "twitter": "https://twitter.com",
            "instagram": "https://instagram.com",
            "linkedin": "https://linkedin.com",
            "amazon": "https://amazon.com",
            "netflix": "https://netflix.com",
            "spotify": "https://spotify.com"
        }
        
        for site_name, url in site_mappings.items():
            if site_name in prompt_lower:
                return url
                
        return None

    def _extract_url(self, prompt: str) -> Optional[str]:
        """Extract URL from prompt"""
        url_pattern = re.compile(r"https?://[\w\-.]+(:[\d]+)?(/[\w\-./?%&=]*)?", re.IGNORECASE)
        match = url_pattern.search(prompt)
        if match:
            return match.group(0)
        # Check for common site names and convert to URL
        common_sites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "amazon": "https://www.amazon.com",
            "wikipedia": "https://www.wikipedia.org"
        }
        for site, url in common_sites.items():
            if site in prompt.lower():
                return url
        return None

    def _extract_search_query(self, prompt: str) -> str:
        """Extract search query from the prompt."""
        search_phrases = ["search for", "search", "google", "look up", "find"]
        for phrase in search_phrases:
            if phrase in prompt.lower():
                start_idx = prompt.lower().find(phrase) + len(phrase)
                query = prompt[start_idx:].strip()
                return query
        return prompt

    def _extract_element(self, prompt: str) -> str:
        """Extract element to click from the prompt."""
        click_phrases = ["click on", "click", "select", "press", "tap"]
        for phrase in click_phrases:
            if phrase in prompt.lower():
                start_idx = prompt.lower().find(phrase) + len(phrase)
                element = prompt[start_idx:].strip()
                return element
        return prompt

    def _extract_input_info(self, prompt: str) -> Optional[Tuple[str, str]]:
        """Extract input field and text from prompt"""
        if "into" in prompt.lower() and "type" in prompt.lower():
            parts = prompt.split("into")
            if len(parts) > 1:
                field = parts[1].strip()
                text_part = parts[0].replace("type", "").strip()
                return (field, text_part)
        return None

    def _determine_browser(self, prompt: str) -> str:
        """Determine which browser to use based on prompt or default to platform preference."""
        browser_map = {
            "safari": "Safari",
            "chrome": "Google Chrome",
            "firefox": "Firefox",
            "edge": "Microsoft Edge",
            "opera": "Opera"
        }
        prompt_lower = prompt.lower()
        for key, value in browser_map.items():
            if key in prompt_lower:
                return value
        return "Safari" if os.name == "posix" else "Google Chrome"

    def _handle_click(self, prompt: str) -> str:
        """Handle clicking elements in browser."""
        self.logger.info(f"Handling browser click: {prompt}")
        try:
            element = self._extract_element(prompt)
            if os.name == "posix":
                # macOS - AppleScript approach (limited support for clicking specific elements without plugin)
                return "Clicking elements is not fully supported without the advanced plugin on macOS."
            else:
                # Windows - Limited support without plugin
                return "Clicking elements is not fully supported without the advanced plugin on Windows."
        except Exception as e:
            return self._handle_error(prompt, str(e))

    def _handle_input(self, prompt: str) -> str:
        """Handle inputting text into fields in browser."""
        self.logger.info(f"Handling browser input: {prompt}")
        try:
            input_info = self._extract_input_info(prompt)
            if input_info:
                field, text = input_info
                if os.name == "posix":
                    # macOS - AppleScript approach (limited support for input without plugin)
                    return "Inputting text is not fully supported without the advanced plugin on macOS."
                else:
                    # Windows - Limited support without plugin
                    return "Inputting text is not fully supported without the advanced plugin on Windows."
            else:
                return "I couldn't determine the input field or text to enter. Please provide more details."
        except Exception as e:
            return self._handle_error(prompt, str(e))

    def _handle_default(self, prompt: str) -> str:
        """Handle default or unrecognized browser tasks."""
        self.logger.info(f"Handling default browser task: {prompt}")
        try:
            return "I couldn't understand the browser task. Please specify if you want to open, search, click, input, or close the browser."
        except Exception as e:
            return self._handle_error(prompt, str(e))

    def _handle_error(self, prompt: str, error: str) -> str:
        """Handle errors during browser task execution."""
        self.logger.error(f"Browser task error for '{prompt}': {error}")
        return f"Failed to execute browser task: {error}"

    def initialize(self) -> None:
        """Initialize the agent, checking for required tools."""
        self.logger.info("Initializing Browser Control Agent")
        if not self._plugin_checked:
            self._check_web_plugin()
            self._plugin_checked = True
        self._check_tools()

    def shutdown(self) -> None:
        """Shut down the agent, releasing any resources."""
        self.logger.info("Shutting down Browser Control Agent")
        self.browser_process = None
        if self.web_plugin:
            try:
                self.web_plugin.close_browser()
            except:
                pass
        self.web_plugin = None

    def get_status(self) -> str:
        """Get the current status of the agent."""
        return "Browser Control Agent is operational"

    def _check_tools(self) -> None:
        """Check available tools and configurations for browser control."""
        # Placeholder for actual tool checking logic
        self.logger.info("Checking tools for browser control")
        # For now, just log that we're using AppleScript on macOS or PowerShell on Windows
        if os.name == 'posix':
            self.logger.info("Using AppleScript for browser control on macOS")
        elif os.name == 'nt':
            self.logger.info("Using PowerShell for browser control on Windows")
