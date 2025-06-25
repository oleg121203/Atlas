"""
Browser automation tools for Atlas.
"""

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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BrowserTool:
    """Enhanced browser automation tool with Gmail email search capabilities."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None
        self.wait = None
        self._initialize_driver()
        
        # Initialize browser modules after driver is created
        if self.driver:
            self.navigation = BrowserNavigation(self.driver)
            self.interaction = BrowserInteraction(self.driver)
            self.analysis = BrowserAnalysis(self.driver)
        else:
            self.logger.error("Failed to initialize browser modules - driver is None")

    def _initialize_driver(self) -> None:
        """Initialize Chrome WebDriver."""
        try:
            chrome_options = Options()
            # Disable headless mode for better interaction with Gmail
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Add user agent to make it look more human-like
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            
            # Add experimental options for better performance
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)  # Increased timeout
            self.logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise

    def open_url(self, url: str) -> Dict[str, Any]:
        """Open URL in browser."""
        try:
            if not self.driver:
                return {"success": False, "error": "Browser not initialized"}
                
            self.logger.info(f"Opening URL: {url}")
            
            self.driver.get(url)
            self.logger.info("Chrome WebDriver initialized successfully")
            
            return {
                "success": True, 
                "data": {
                    "url": url,
                    "title": self.driver.title
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to open URL: {e}")
            return {"success": False, "error": str(e)}

    def find_links(self, 
                  selector: Optional[str] = None,
                  text_contains: Optional[str] = None,
                  timeout: int = 10) -> Dict[str, Any]:
        """Find links on the page."""
        if not self.driver:
            return {"success": False, "error": "Browser not initialized"}
        return self.navigation.find_links(selector, text_contains, timeout)

    def click_link(self, 
                  selector: Optional[str] = None,
                  text_contains: Optional[str] = None,
                  timeout: int = 10) -> Dict[str, Any]:
        """Click a link on the page."""
        if not self.driver:
            return {"success": False, "error": "Browser not initialized"}
        return self.navigation.click_link(selector, text_contains, timeout)

    def scroll_to_element(self, element: Any) -> Dict[str, Any]:
        """Scroll to an element on the page."""
        if not self.driver:
            return {"success": False, "error": "Browser not initialized"}
        return self.navigation.scroll_to_element(element)

    def scroll_page(self, direction: str = 'down', pixels: int = 500) -> Dict[str, Any]:
        """Scroll the page."""
        if not self.driver:
            return {"success": False, "error": "Browser not initialized"}
        return self.navigation.scroll_page(direction, pixels)

    def search_gmail_emails(self, search_query: str = "security") -> Dict[str, Any]:
        """Search for emails in Gmail with specific query."""
        try:
            if not self.driver or not self.wait:
                return {"success": False, "error": "Browser not initialized"}
            
            self.logger.info(f"Searching Gmail for: {search_query}")
            
            # Wait for Gmail to load
            time.sleep(3)
            
            # Find and click search box
            try:
                search_box = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search mail']"))
                )
                search_box.clear()
                search_box.send_keys(search_query)
                
                # Press Enter to search
                from selenium.webdriver.common.keys import Keys
                search_box.send_keys(Keys.RETURN)
                
                self.logger.info("Search query entered successfully")
                
            except TimeoutException:
                self.logger.warning("Search box not found, trying alternative selectors")
                # Try alternative selectors
                try:
                    search_box = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                    search_box.clear()
                    search_box.send_keys(search_query)
                    search_box.send_keys(Keys.RETURN)
                except NoSuchElementException:
                    return {"success": False, "error": "Could not find search box"}
            
            # Wait for search results
            time.sleep(5)
            
            # Extract email information
            emails = self._extract_email_data()
            
            return {
                "success": True,
                "search_query": search_query,
                "emails_found": len(emails),
                "emails": emails,
                "message": f"Found {len(emails)} emails matching '{search_query}'"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to search Gmail: {e}")
            return {"success": False, "error": str(e)}

    def _extract_email_data(self) -> List[Dict[str, Any]]:
        """Extract email data from Gmail search results."""
        emails = []
        
        try:
            if not self.driver:
                return emails
                
            # Find email elements
            email_elements = self.driver.find_elements(By.CSS_SELECTOR, "tr[role='row']")
            
            for element in email_elements[:10]:  # Limit to first 10 emails
                try:
                    # Extract sender
                    sender_element = element.find_element(By.CSS_SELECTOR, "td[data-th='From'] span")
                    sender = sender_element.text.strip()
                    
                    # Extract subject
                    subject_element = element.find_element(By.CSS_SELECTOR, "td[data-th='Subject'] span")
                    subject = subject_element.text.strip()
                    
                    # Extract snippet
                    snippet_element = element.find_element(By.CSS_SELECTOR, "td[data-th='Snippet'] span")
                    snippet = snippet_element.text.strip()
                    
                    # Extract date
                    date_element = element.find_element(By.CSS_SELECTOR, "td[data-th='Date'] span")
                    date = date_element.text.strip()
                    
                    # Determine priority based on content
                    priority = "low"
                    if any(keyword in subject.lower() for keyword in ["security", "alert", "warning", "critical"]):
                        priority = "high"
                    elif any(keyword in subject.lower() for keyword in ["verify", "confirm", "login"]):
                        priority = "medium"
                    
                    email_data = {
                        "sender": sender,
                        "subject": subject,
                        "snippet": snippet,
                        "date": date,
                        "priority": priority
                    }
                    
                    emails.append(email_data)
                    
                except NoSuchElementException:
                    continue  # Skip elements that don't have all required fields
            
            self.logger.info(f"Extracted {len(emails)} emails")
            
        except Exception as e:
            self.logger.error(f"Failed to extract email data: {e}")
        
        return emails

    def navigate_to_gmail(self) -> Dict[str, Any]:
        """Navigate to Gmail and wait for it to load."""
        try:
            if not self.driver:
                return {"success": False, "error": "Browser not initialized"}
                
            self.logger.info("Navigating to Gmail")
            
            # Open Gmail
            result = self.open_url("https://gmail.com")
            if not result.get("success"):
                return result
            
            # Wait for Gmail to load
            time.sleep(5)
            
            # Check if we're on Gmail page
            if "gmail" in self.driver.current_url.lower():
                self.logger.info("Successfully navigated to Gmail")
                return {"success": True, "message": "Gmail loaded successfully"}
            else:
                return {"success": False, "error": "Failed to load Gmail"}
                
        except Exception as e:
            self.logger.error(f"Failed to navigate to Gmail: {e}")
            return {"success": False, "error": str(e)}

    def close_browser(self) -> Dict[str, Any]:
        """Close the browser."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
                self.logger.info("Browser closed successfully")
                return {"success": True, "message": "Browser closed successfully"}
            else:
                return {"success": True, "message": "No browser to close"}
        except Exception as e:
            self.logger.error(f"Failed to close browser: {e}")
            return {"success": False, "error": str(e)}

    def execute_email_task(self, task_description: str) -> Dict[str, Any]:
        """Execute email-related task with browser automation."""
        try:
            self.logger.info(f"Executing email task: {task_description}")
            
            # Navigate to Gmail
            nav_result = self.navigate_to_gmail()
            if not nav_result.get("success"):
                return nav_result
            
            # Wait for Gmail to fully load
            time.sleep(8)
            
            # Determine search query based on task
            search_query = "security"
            if "google account security" in task_description.lower():
                search_query = "google account security"
            elif "security" in task_description.lower():
                search_query = "security"
            elif "login" in task_description.lower():
                search_query = "login"
            
            # Search for emails
            search_result = self.search_gmail_emails(search_query)
            
            # Close browser
            self.close_browser()
            
            # Verify we actually found emails
            if search_result.get("success") and search_result.get("emails_found", 0) > 0:
                self.logger.info(f"Successfully found {search_result.get('emails_found')} emails")
                return search_result
            else:
                self.logger.warning("No emails found in search")
                return {
                    "success": False,
                    "error": "No emails found matching the search criteria",
                    "search_query": search_query,
                    "emails_found": 0
                }
            
        except Exception as e:
            self.logger.error(f"Failed to execute email task: {e}")
            self.close_browser()
            return {"success": False, "error": str(e)}

    def __del__(self):
        self.close_browser()

__all__ = ['BrowserTool']
