"""
Specialized agent for web browsing tasks.
"""

from typing import Any, Dict

import webbrowser
import re

from agents.base_agent import BaseAgent


class BrowserAgent(BaseAgent):
    """Handles tasks related to web browsing and information gathering."""

    def __init__(self):
        super().__init__("Browser Agent")

    def execute_task(self, prompt: str, context: Dict[str, Any]) -> str:
        self.logger.info(f"Executing browser task: '{prompt}'")

        # Simple URL extraction using regex
        url_pattern = re.compile(r'https?://[\S]+')
        match = url_pattern.search(prompt)

        if match:
            url = match.group(0)
            try:
                webbrowser.open(url)
                self.logger.info(f"Successfully opened URL: {url}")
                return f"Successfully opened URL: {url}"
            except Exception as e:
                self.logger.error(f"Failed to open URL {url}: {e}")
                return f"Error opening URL {url}: {e}"

        # Simple web search capability
        search_prefix = "search for "
        if prompt.lower().startswith(search_prefix):
            query = prompt[len(search_prefix):].strip()
            # A real implementation would use a proper search API/tool
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            try:
                webbrowser.open(search_url)
                self.logger.info(f"Successfully searched for: '{query}'")
                return f"Successfully performed web search for: '{query}'"
            except Exception as e:
                self.logger.error(f"Failed to perform web search for '{query}': {e}")
                return f"Error performing web search for '{query}': {e}"

        return f"Unknown browser task: '{prompt}'. Please provide a URL to open or use 'search for <query>'."
