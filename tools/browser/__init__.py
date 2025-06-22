from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Dict, Any, List
import logging
import time
from .navigation import BrowserNavigation
from .interaction import BrowserInteraction
from .analysis import BrowserAnalysis

class BrowserTool:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None
        self._initialize_driver()
        
        # Initialize browser modules
        self.navigation = BrowserNavigation(self.driver)
        self.interaction = BrowserInteraction(self.driver)
        self.analysis = BrowserAnalysis(self.driver)

    def _initialize_driver(self) -> None:
        """Initialize Chrome WebDriver."""
        try:
            chrome_options = Options()
            # Enable headless mode
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Add user agent to make it look more human-like
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            
            # Add experimental options for better performance
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise

    def open_url(self, url: str) -> Dict[str, Any]:
        """Open a URL in the browser."""
        return self.navigation.navigate_to(url)

    def find_links(self, 
                  selector: Optional[str] = None,
                  text_contains: Optional[str] = None,
                  timeout: int = 10) -> Dict[str, Any]:
        """Find links on the page."""
        return self.navigation.find_links(selector, text_contains, timeout)

    def click_link(self, 
                  selector: Optional[str] = None,
                  text_contains: Optional[str] = None,
                  timeout: int = 10) -> Dict[str, Any]:
        """Click a link on the page."""
        return self.navigation.click_link(selector, text_contains, timeout)

    def scroll_to_element(self, element: Any) -> Dict[str, Any]:
        """Scroll to an element on the page."""
        return self.navigation.scroll_to_element(element)

    def scroll_page(self, direction: str = 'down', pixels: int = 500) -> Dict[str, Any]:
        """Scroll the page."""
        return self.navigation.scroll_page(direction, pixels)
        """Execute JavaScript code."""
        try:
            result = self.driver.execute_script(script, *args)
            return {
                "success": True,
                "data": {
                    "result": result
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to execute script: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def close(self) -> None:
        """Close the browser."""
        try:
            if self.driver:
                self.driver.quit()
            self.logger.info("Browser closed successfully")
        except Exception as e:
            self.logger.error(f"Failed to close browser: {e}")

    def __del__(self):
        self.close()

__all__ = ['BrowserTool']
