"""
Enhanced Browser Agent with plugin integration.
Uses the Advanced Web Browsing Plugin for comprehensive automation.
"""

import json
import re
import webbrowser
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


class BrowserAgent(BaseAgent):
    """Enhanced browser agent that integrates with the Advanced Web Browsing Plugin."""

    def __init__(self):
        super().__init__("Enhanced Browser Agent")
        self.web_plugin_available = False
        self._check_web_plugin()

    def _check_web_plugin(self):
        """Check if the Advanced Web Browsing Plugin is available"""
        try:
            #Try to import the web browsing plugin
            import os
            import sys

            #Add plugins directory to path
            plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins", "web_browsing")
            if plugins_dir not in sys.path:
                sys.path.append(plugins_dir)

            import plugin as web_plugin
            self.web_plugin = web_plugin
            self.web_plugin_available = True
            self.logger.info("Advanced Web Browsing Plugin is available")
        except ImportError as e:
            self.logger.warning(f"Advanced Web Browsing Plugin not available: {e}")
            self.web_plugin_available = False

    def execute_task(self, prompt: str, context: Dict[str, Any]) -> str:
        """Execute browser task with enhanced capabilities"""
        self.logger.info(f"Executing enhanced browser task: '{prompt}'")
        prompt_lower = prompt.lower()

        try:
            # Extract browser name and URL if present
            browser_name = self._extract_browser_name(prompt)
            url = self._extract_url(prompt)
            
            # Special handling for specific site requests
            if not url and any(site in prompt_lower for site in ["github", "google", "facebook", "youtube", "twitter"]):
                url = self._infer_url_from_site_name(prompt)
            
            # Handle browser tasks
            if any(keyword in prompt_lower for keyword in ["open browser", "відкрий браузер", "открой браузер"]):
                # Set browser if specified
                if browser_name:
                    try:
                        browser = webbrowser.get(browser_name)
                    except webbrowser.Error:
                        browser = webbrowser.get()
                else:
                    browser = webbrowser.get()
                    
                # Open URL if specified, otherwise just open browser
                if url:
                    browser.open(url)
                    return f"Opened {url} in {browser_name or 'default'} browser"
                else:
                    browser.open("")
                    return f"Opened {browser_name or 'default'} browser"
                    
            # Handle navigation tasks (including specific browser requests)
            elif any(keyword in prompt_lower for keyword in ["open", "navigate", "go to", "visit"]) and (url or browser_name):
                # Set browser if specified
                if browser_name:
                    try:
                        browser = webbrowser.get(browser_name)
                    except webbrowser.Error:
                        browser = webbrowser.get()
                else:
                    browser = webbrowser.get()
                    
                # Use inferred URL if none was explicitly found
                if not url:
                    url = "https://github.com"  # Default for GitHub requests
                    
                browser.open(url)
                return f"Opened {url} in {browser_name or 'default'} browser"
                    
            elif "close browser" in prompt_lower:
                return self._handle_close_browser()
                
            # Handle other browser tasks with plugin
            elif self.web_plugin_available:
                return self._execute_with_plugin(prompt, context)
                
            return "Browser task not recognized. Available capabilities: navigate, search, click, fill, screenshot, scrape, scroll, wait."
            
        except Exception as e:
            self.logger.error(f"Browser task execution failed: {e}")
            return f"Failed to execute browser task: {str(e)}"

    def _execute_with_plugin(self, prompt: str, context: Dict[str, Any]) -> str:
        """Execute task using the Advanced Web Browsing Plugin"""
        prompt_lower = prompt.lower()

        try:
            # Handle browser open/close tasks
            if any(keyword in prompt_lower for keyword in ["open browser", "відкрий браузер", "открой браузер"]):
                # If it's a combined task like "open browser and close it"
                if any(keyword in prompt_lower for keyword in ["close", "закрий", "закрой"]):
                    return self._handle_open_and_close_browser()
                else:
                    return self._handle_open_browser()
                    
            elif any(keyword in prompt_lower for keyword in ["close browser", "закрий браузер", "закрой браузер"]):
                return self._handle_close_browser()
                
            #Navigation tasks
            elif any(keyword in prompt_lower for keyword in ["navigate", "go to", "open", "visit"]):
                url = self._extract_url(prompt)
                if url:
                    result = self.web_plugin.navigate_to_url(url)
                    return f"Navigation result: {result}"

            #Search tasks - both in-page search and site navigation
            elif any(keyword in prompt_lower for keyword in ["search for", "find", "look for", "знайди", "пошук", "settings", "настройки"]):
                search_term = self._extract_search_term(prompt)
                if search_term:
                    result = self.web_plugin.search_on_site(search_term)
                    return f"Search result: {result}"
                # If no search term found, try to navigate to common sections
                elif any(keyword in prompt_lower for keyword in ["settings", "настройки"]):
                    # Try to navigate to settings page
                    result = self.web_plugin.navigate_to_url("https://github.com/settings")
                    return f"Navigated to GitHub settings: {result}"

            #Click tasks
            elif any(keyword in prompt_lower for keyword in ["click", "press", "tap"]):
                selector = self._extract_selector(prompt)
                if selector:
                    result = self.web_plugin.click_element(selector)
                    return f"Click result: {result}"
                #Try text-based clicking
                text = self._extract_text_to_click(prompt)
                if text:
                    result = self.web_plugin.click_element("", "css", text=text)
                    return f"Text click result: {result}"

            #Fill form tasks
            elif any(keyword in prompt_lower for keyword in ["fill", "type", "enter", "input"]):
                selector, value = self._extract_fill_params(prompt)
                if selector and value:
                    result = self.web_plugin.fill_form_field(selector, value)
                    return f"Fill result: {result}"

            #Screenshot tasks
            elif any(keyword in prompt_lower for keyword in ["screenshot", "capture", "snap"]):
                filename = self._extract_filename(prompt)
                result = self.web_plugin.take_screenshot(filename)
                return f"Screenshot result: {result}"

            #Scraping tasks
            elif any(keyword in prompt_lower for keyword in ["scrape", "extract", "get content"]):
                selectors = self._extract_selectors(prompt)
                result = self.web_plugin.scrape_page_content(selectors)
                return f"Scraping result: {result}"

            #Scroll tasks
            elif any(keyword in prompt_lower for keyword in ["scroll", "move down", "move up"]):
                direction, amount = self._extract_scroll_params(prompt)
                result = self.web_plugin.scroll_page(direction, amount)
                return f"Scroll result: {result}"

            #Wait tasks
            elif any(keyword in prompt_lower for keyword in ["wait for", "wait until"]):
                selector, timeout = self._extract_wait_params(prompt)
                if selector:
                    result = self.web_plugin.wait_for_element(selector, timeout)
                    return f"Wait result: {result}"

            #If no specific task matched, try basic navigation
            url = self._extract_url(prompt)
            if url:
                result = self.web_plugin.navigate_to_url(url)
                return f"Navigation result: {result}"

            return f"Enhanced browser task not recognized. Available capabilities: navigate, search, click, fill, screenshot, scrape, scroll, wait. Task: '{prompt}'"

        except Exception as e:
            self.logger.error(f"Plugin execution failed: {e}")
            return self._execute_basic(prompt, context)

    def _execute_basic(self, prompt: str, context: Dict[str, Any]) -> str:
        """Fallback to basic browser functionality"""
        #Simple URL extraction using regex
        url_pattern = re.compile(r"https?://[\S]+")
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

        #Simple web search capability
        search_prefix = "search for "
        if prompt.lower().startswith(search_prefix):
            query = prompt[len(search_prefix):].strip()
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            try:
                webbrowser.open(search_url)
                self.logger.info(f"Successfully searched for: '{query}'")
                return f"Successfully performed web search for: '{query}'"
            except Exception as e:
                self.logger.error(f"Failed to perform web search for '{query}': {e}")
                return f"Error performing web search for '{query}': {e}"

        return f"Basic browser task not recognized: '{prompt}'. Try 'navigate to <URL>' or 'search for <query>'."

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
        #Look for explicit URLs
        url_pattern = re.compile(r"https?://[\S]+")
        match = url_pattern.search(prompt)
        if match:
            return match.group(0)

        #Look for common website patterns
        site_patterns = [
            r"auto\.ria\.com",
            r"google\.com",
            r"facebook\.com",
            r"youtube\.com",
            r"github\.com",
        ]

        for pattern in site_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return f"https://{re.search(pattern, prompt, re.IGNORECASE).group(0)}"

        return None

    def _extract_search_term(self, prompt: str) -> Optional[str]:
        """Extract search term from prompt"""
        #Look for common search patterns
        patterns = [
            r"search for (.+)",
            r"find (.+)",
            r"look for (.+)",
            r"search (.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_selector(self, prompt: str) -> Optional[str]:
        """Extract CSS selector from prompt"""
        #Look for quoted selectors
        quotes_pattern = r'["\']([^"\']+)["\']'
        match = re.search(quotes_pattern, prompt)
        if match:
            return match.group(1)

        #Look for common selector patterns
        if "#" in prompt:
            id_match = re.search(r"#([\w-]+)", prompt)
            if id_match:
                return f"#{id_match.group(1)}"

        if "." in prompt and "class" in prompt.lower():
            class_match = re.search(r'class["\s]*([.\w-]+)', prompt, re.IGNORECASE)
            if class_match:
                return f".{class_match.group(1).replace('.', '')}"

        return None

    def _extract_text_to_click(self, prompt: str) -> Optional[str]:
        """Extract text to click from prompt"""
        #Look for quoted text
        quotes_pattern = r'["\']([^"\']+)["\']'
        match = re.search(quotes_pattern, prompt)
        if match:
            return match.group(1)

        #Look for common button text
        button_patterns = [
            r"click (?:on )?(.+?)(?:\s|$)",
            r"press (.+?)(?:\s|$)",
            r"tap (.+?)(?:\s|$)",
        ]

        for pattern in button_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                if len(text) < 50:  #Reasonable button text length
                    return text

        return None

    def _extract_fill_params(self, prompt: str) -> tuple:
        """Extract selector and value for form filling"""
        #Look for "fill X with Y" pattern
        fill_pattern = r"fill (.+?) with (.+)"
        match = re.search(fill_pattern, prompt, re.IGNORECASE)
        if match:
            selector = match.group(1).strip()
            value = match.group(2).strip()

            #Clean up selector
            if not any(selector.startswith(prefix) for prefix in ["#", ".", "[", "//"]):
                selector = f'[name="{selector}"]'  #Default to name attribute

            return selector, value

        return None, None

    def _extract_filename(self, prompt: str) -> Optional[str]:
        """Extract filename from prompt"""
        #Look for quoted filename
        quotes_pattern = r'["\']([^"\']+\.(?:png|jpg|jpeg|gif|bmp))["\']'
        match = re.search(quotes_pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    def _extract_selectors(self, prompt: str) -> Optional[str]:
        """Extract selectors for scraping"""
        #Look for JSON array of selectors
        json_pattern = r"\[([^\]]+)\]"
        match = re.search(json_pattern, prompt)
        if match:
            try:
                return json.dumps(json.loads(f"[{match.group(1)}]"))
            except:
                pass

        return None

    def _extract_scroll_params(self, prompt: str) -> tuple:
        """Extract scroll direction and amount"""
        direction = "down"  #default
        amount = 3  #default

        if any(word in prompt.lower() for word in ["up", "top"]):
            direction = "up"
        elif any(word in prompt.lower() for word in ["down", "bottom"]):
            direction = "down"
        elif "top" in prompt.lower():
            direction = "top"
        elif "bottom" in prompt.lower():
            direction = "bottom"

        #Look for numbers
        number_pattern = r"(\d+)"
        match = re.search(number_pattern, prompt)
        if match:
            amount = int(match.group(1))

        return direction, amount

    def _extract_wait_params(self, prompt: str) -> tuple:
        """Extract selector and timeout for waiting"""
        selector = self._extract_selector(prompt)
        timeout = 30  #default

        #Look for timeout
        timeout_pattern = r"(\d+)\s*(?:seconds?|secs?|s)"
        match = re.search(timeout_pattern, prompt, re.IGNORECASE)
        if match:
            timeout = int(match.group(1))

        return selector, timeout

    def _extract_browser_name(self, prompt: str) -> Optional[str]:
        """Extract browser name from prompt"""
        prompt_lower = prompt.lower()
        browser_keywords = {
            "safari": ["safari", "сафарі", "сафари"],
            "chrome": ["chrome", "google chrome", "хром", "гугл хром"],
            "firefox": ["firefox", "mozilla", "фаєрфокс", "файрфокс"],
            "edge": ["edge", "microsoft edge", "едж"]
        }
        
        for browser, keywords in browser_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return browser
        return None
        
    def _handle_open_browser(self) -> str:
        """Handle browser open requests"""
        try:
            # Default browser
            webbrowser.open("")  # Empty string opens the default browser
            return "Successfully opened the default browser"
        except Exception as e:
            self.logger.error(f"Failed to open browser: {e}")
            return f"Failed to open browser: {str(e)}"
            
    def _handle_close_browser(self) -> str:
        """Handle browser close requests"""
        try:
            if self.web_plugin_available:
                self.web_plugin.close_browser()
                return "Browser closed successfully"
            return "Unable to close browser - plugin not available"
        except Exception as e:
            self.logger.error(f"Failed to close browser: {e}")
            return f"Failed to close browser: {str(e)}"
            
    def _handle_open_and_close_browser(self) -> str:
        """Handle combined open and close browser requests"""
        open_result = self._handle_open_browser()
        close_result = self._handle_close_browser()
        return f"{open_result}. {close_result}"
