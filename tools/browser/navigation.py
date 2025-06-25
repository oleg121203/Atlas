from typing import Dict, Optional, Any
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserNavigation:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.logger = logging.getLogger(__name__)

    def navigate_to(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Navigate to a URL."""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            return {
                "success": True,
                "data": {
                    "url": self.driver.current_url,
                    "title": self.driver.title
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to navigate to URL: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def find_links(self, 
                  selector: Optional[str] = None,
                  text_contains: Optional[str] = None,
                  timeout: int = 10) -> Dict[str, Any]:
        """Find links on the page."""
        try:
            if selector:
                elements = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
            else:
                elements = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
                )
            
            links = []
            for element in elements:
                if text_contains and text_contains.lower() not in element.text.lower():
                    continue
                
                links.append({
                    'text': element.text,
                    'url': element.get_attribute('href'),
                    'element': element
                })
            
            return {
                "success": True,
                "data": links
            }
        except Exception as e:
            self.logger.error(f"Failed to find links: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def click_link(self, 
                  selector: Optional[str] = None,
                  text_contains: Optional[str] = None,
                  timeout: int = 10) -> Dict[str, Any]:
        """Click a link on the page."""
        try:
            links = self.find_links(selector, text_contains, timeout)
            if not links["success"] or not links["data"]:
                return links
                
            # Click the first matching link
            links["data"][0]["element"].click()
            
            return {
                "success": True,
                "data": {
                    "message": "Link clicked successfully"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to click link: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def scroll_to_element(self, element: Any) -> Dict[str, Any]:
        """Scroll to an element on the page."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            return {
                "success": True,
                "data": {
                    "message": "Scrolled to element"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to scroll to element: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def scroll_page(self, direction: str = 'down', pixels: int = 500) -> Dict[str, Any]:
        """Scroll the page."""
        try:
            if direction == 'down':
                self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            else:
                self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            return {
                "success": True,
                "data": {
                    "message": f"Scrolled {direction} by {pixels} pixels"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to scroll page: {e}")
            return {
                "success": False,
                "error": str(e)
            }
