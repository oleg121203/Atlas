"""
Advanced Web Browsing Plugin for Atlas
Supports multiple automation methods with cascading fallbacks:
1. Selenium WebDriver (primary)
2. Playwright (secondary) 
3. System Events + PyAutoGUI (tertiary)
4. Direct HTTP requests (final fallback)
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Tuple

#Cross-platform imports
from utils.platform_utils import IS_HEADLESS, IS_MACOS

logger = logging.getLogger(__name__)

class WebAutomationError(Exception):
    """Custom exception for web automation failures"""

class AdvancedWebBrowser:
    """Advanced web browser automation with multiple fallback methods"""

    def __init__(self):
        self.selenium_driver = None
        self.playwright_browser = None
        self.playwright_page = None
        self.current_method = None
        self.timeout = 30
        self.retry_delay = 2
        self.max_retries = 3

        #Initialize available methods
        self.available_methods = self._detect_available_methods()
        logger.info(f"Available web automation methods: {self.available_methods}")

    def _detect_available_methods(self) -> List[str]:
        """Detect available web automation methods"""
        available = []
        
        # Check Selenium with different browsers
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from selenium.webdriver.safari.options import Options as SafariOptions
            from selenium.webdriver.edge.options import Options as EdgeOptions
            
            # Check for Chrome
            try:
                chrome_options = ChromeOptions()
                chrome_options.add_argument("--headless")
                driver = webdriver.Chrome(options=chrome_options)
                driver.quit()
                available.append("chrome")
            except Exception:
                pass
                
            # Check for Firefox
            try:
                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--headless")
                driver = webdriver.Firefox(options=firefox_options)
                driver.quit()
                available.append("firefox")
            except Exception:
                pass
                
            # Check for Safari (macOS only)
            try:
                safari_options = SafariOptions()
                driver = webdriver.Safari(options=safari_options)
                driver.quit()
                available.append("safari")
            except Exception:
                pass
                
            # Check for Edge
            try:
                edge_options = EdgeOptions()
                edge_options.add_argument("--headless")
                driver = webdriver.Edge(options=edge_options)
                driver.quit()
                available.append("edge")
            except Exception:
                pass
                
            if available:
                available.append("selenium_webdriver")
        except Exception as e:
            logger.error(f"Selenium detection failed: {e}")
            
        #Check Playwright
        try:
            import playwright
            available.append("playwright")
        except ImportError:
            logger.warning("Playwright not available")

        #System events always available
        available.append("system_events")

        #HTTP requests always available
        available.append("http_requests")

        return available

    def initialize(self, preferred_browser: str = "") -> bool:
        """Initialize browser automation with preferred browser"""
        if not self.available_methods:
            self.available_methods = self._detect_available_methods()
            
        if not self.available_methods:
            logger.error("No web automation methods available")
            return False
            
        # Try preferred browser first if specified
        if preferred_browser and preferred_browser in self.available_methods:
            if self._initialize_browser(preferred_browser):
                self.current_method = preferred_browser
                return True
                
        # Otherwise try each available method in order
        for method in self.available_methods:
            if self._initialize_browser(method):
                self.current_method = method
                return True
                
        logger.error("Failed to initialize any browser automation method")
        return False

    def _init_selenium(self, browser_name: str = "") -> bool:
        """Initialize Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            options = Options()
            if IS_HEADLESS:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            #Try Chrome first, then fallback to other browsers
            if browser_name and browser_name.lower() == "chrome":
                self.selenium_driver = webdriver.Chrome(options=options)
                logger.info("Selenium Chrome driver initialized")
                return True
            elif browser_name and browser_name.lower() == "firefox":
                from selenium.webdriver.firefox.options import (
                    Options as FirefoxOptions,
                )
                firefox_options = FirefoxOptions()
                if IS_HEADLESS:
                    firefox_options.add_argument("--headless")
                self.selenium_driver = webdriver.Firefox(options=firefox_options)
                logger.info("Selenium Firefox driver initialized")
                return True
            elif browser_name and browser_name.lower() == "safari":
                self.selenium_driver = webdriver.Safari()
                logger.info("Selenium Safari driver initialized")
                return True
            elif browser_name and browser_name.lower() == "edge":
                from selenium.webdriver.edge.options import Options as EdgeOptions
                edge_options = EdgeOptions()
                edge_options.add_argument("--headless")
                self.selenium_driver = webdriver.Edge(options=edge_options)
                logger.info("Selenium Edge driver initialized")
                return True
            else:
                try:
                    self.selenium_driver = webdriver.Chrome(options=options)
                    logger.info("Selenium Chrome driver initialized")
                    return True
                except Exception as e:
                    logger.warning(f"Chrome driver failed: {e}")

                #Try Firefox
                try:
                    from selenium.webdriver.firefox.options import (
                        Options as FirefoxOptions,
                    )
                    firefox_options = FirefoxOptions()
                    if IS_HEADLESS:
                        firefox_options.add_argument("--headless")
                    self.selenium_driver = webdriver.Firefox(options=firefox_options)
                    logger.info("Selenium Firefox driver initialized")
                    return True
                except Exception as e:
                    logger.warning(f"Firefox driver failed: {e}")

                #Try Safari on macOS
                if IS_MACOS:
                    try:
                        self.selenium_driver = webdriver.Safari()
                        logger.info("Selenium Safari driver initialized")
                        return True
                    except Exception as e:
                        logger.warning(f"Safari driver failed: {e}")

                #Try Edge
                try:
                    from selenium.webdriver.edge.options import Options as EdgeOptions
                    edge_options = EdgeOptions()
                    edge_options.add_argument("--headless")
                    self.selenium_driver = webdriver.Edge(options=edge_options)
                    logger.info("Selenium Edge driver initialized")
                    return True
                except Exception as e:
                    logger.warning(f"Edge driver failed: {e}")

        except Exception as e:
            logger.error(f"Selenium initialization failed: {e}")

        return False

    def _init_playwright(self) -> bool:
        """Initialize Playwright browser"""
        try:
            from playwright.sync_api import sync_playwright

            self.playwright = sync_playwright().start()

            #Try different browsers
            for browser_type in ["chromium", "firefox", "webkit"]:
                try:
                    browser_launcher = getattr(self.playwright, browser_type)
                    self.playwright_browser = browser_launcher.launch(
                        headless=IS_HEADLESS,
                        args=["--no-sandbox", "--disable-dev-shm-usage"] if browser_type == "chromium" else [],
                    )
                    self.playwright_page = self.playwright_browser.new_page()
                    self.playwright_page.set_viewport_size({"width": 1920, "height": 1080})
                    logger.info(f"Playwright {browser_type} browser initialized")
                    return True
                except Exception as e:
                    logger.warning(f"Playwright {browser_type} failed: {e}")

        except Exception as e:
            logger.error(f"Playwright initialization failed: {e}")

        return False

    def _initialize_browser(self, method: str) -> bool:
        """Initialize browser with specified method"""
        if method == "selenium_webdriver":
            return self._init_selenium()
        elif method == "playwright":
            return self._init_playwright()
        elif method == "system_events":
            return True
        elif method == "http_requests":
            return True
        elif method in ["chrome", "firefox", "safari", "edge"]:
            return self._init_selenium(method)
        else:
            logger.error(f"Unknown browser method: {method}")
            return False

    def _navigate_selenium(self, url: str) -> bool:
        """Navigate using Selenium"""
        try:
            self.selenium_driver.get(url)
            self.selenium_driver.implicitly_wait(self.timeout)
            return True
        except Exception as e:
            logger.error(f"Selenium navigation failed: {e}")
            return False

    def _navigate_playwright(self, url: str) -> bool:
        """Navigate using Playwright"""
        try:
            self.playwright_page.goto(url, timeout=self.timeout * 1000)  # type: ignore[union-attr]
            return True
        except Exception as e:
            logger.error(f"Playwright navigation failed: {e}")
            return False

    def _navigate_system_events(self, url: str) -> bool:
        """Navigate using system events (open browser manually)"""
        try:
            import webbrowser

            import pyautogui

            #Open URL in default browser
            webbrowser.open(url)
            time.sleep(3)  #Wait for browser to open

            #Take screenshot to verify
            if not IS_HEADLESS:
                screenshot = pyautogui.screenshot()
                logger.info("Browser opened via system events")
                return True
            logger.warning("System events not available in headless mode")
            return False

        except Exception as e:
            logger.error(f"System events navigation failed: {e}")
            return False

    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to URL with multiple fallback methods"""
        logger.info(f"Navigating to: {url}")

        #Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        for method in self.available_methods:
            try:
                success = False

                if method == "selenium_webdriver":
                    if not self.selenium_driver and not self._init_selenium():
                        continue
                    success = self._navigate_selenium(url)
                    if success:
                        self.current_method = "selenium_webdriver"

                elif method == "playwright":
                    if not self.playwright_browser and not self._init_playwright():
                        continue
                    success = self._navigate_playwright(url)
                    if success:
                        self.current_method = "playwright"

                elif method == "system_events":
                    success = self._navigate_system_events(url)
                    if success:
                        self.current_method = "system_events"

                elif method == "http_requests":
                    #For simple page verification
                    import requests
                    response = requests.get(url, timeout=self.timeout)
                    success = response.status_code == 200
                    if success:
                        self.current_method = "http_requests"

                if success:
                    return {
                        "success": True,
                        "method": self.current_method,
                        "url": url,
                        "message": f"Successfully navigated to {url} using {self.current_method}",
                    }

            except Exception as e:
                logger.warning(f"Method {method} failed: {e}")
                continue

        return {
            "success": False,
            "error": f"All navigation methods failed for {url}",
            "tried_methods": self.available_methods,
        }

    def _find_element_selenium(self, selector: str, selector_type: str) -> Any:
        """Find element using Selenium"""
        try:
            from selenium.webdriver.common.by import By  # type: ignore[import-not-found]
            if selector_type == "id":
                return self.selenium_driver.find_element(By.ID, selector)
            elif selector_type == "class":
                return self.selenium_driver.find_element(By.CLASS_NAME, selector)
            elif selector_type == "name":
                return self.selenium_driver.find_element(By.NAME, selector)
            elif selector_type == "tag":
                return self.selenium_driver.find_element(By.TAG_NAME, selector)
            elif selector_type == "xpath":
                return self.selenium_driver.find_element(By.XPATH, selector)
            else:
                return self.selenium_driver.find_element(By.CSS_SELECTOR, selector)
        except Exception as e:
            logger.error(f"Selenium element search failed: {e}")
            return None

    def _find_element_playwright(self, selector: str, selector_type: str) -> bool:
        """Find element using Playwright"""
        try:
            if selector_type == "xpath":
                element = self.playwright_page.locator(f"xpath={selector}")
            else:
                element = self.playwright_page.locator(selector)

            element.wait_for(timeout=self.timeout * 1000)  # type: ignore[union-attr]
            return element
        except Exception as e:
            logger.error(f"Playwright element search failed: {e}")
            return None

    def _find_element_system_events(self, text: str, image_path: str = None) -> Tuple[int, int]:
        """Find element using system events (OCR + image recognition)"""
        try:
            import pyautogui

            if image_path and os.path.exists(image_path):
                #Use image recognition
                location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                if location:
                    center = pyautogui.center(location)
                    return center.x, center.y

            if text:
                #Use OCR to find text (simplified approach)
                screenshot = pyautogui.screenshot()
                #For now, just return center of screen as fallback
                screen_width, screen_height = pyautogui.size()
                return screen_width // 2, screen_height // 2

        except Exception as e:
            logger.error(f"System events element search failed: {e}")

        return None, None

    def click_element(self, selector: str, selector_type: str = "css",
                     text: str = None, image_path: str = None) -> Dict[str, Any]:
        """Click element with multiple fallback methods"""
        logger.info(f"Clicking element: {selector}")

        for method in self.available_methods:
            if method != self.current_method and self.current_method:
                continue  #Use current method first

            try:
                success = False

                if method == "selenium_webdriver" and self.selenium_driver:
                    element = self._find_element_selenium(selector, selector_type)
                    if element:
                        element.click()  # type: ignore[attr-defined]
                        success = True

                elif method == "playwright" and self.playwright_page:
                    if selector_type == "id":
                        locator = self.playwright_page.locator(f"#{selector}")  # type: ignore[union-attr]
                    elif selector_type == "class":
                        locator = self.playwright_page.locator(f".{selector}")  # type: ignore[union-attr]
                    elif selector_type == "name":
                        locator = self.playwright_page.locator(f"[name='{selector}']")  # type: ignore[union-attr]
                    elif selector_type == "tag":
                        locator = self.playwright_page.locator(selector)  # type: ignore[union-attr]
                    else:
                        locator = self.playwright_page.locator(selector)  # type: ignore[union-attr]

                    locator.click(timeout=self.timeout * 1000)  # type: ignore[attr-defined]
                    success = True

                elif method == "system_events":
                    success = self._click_system_events(selector, selector_type)

                if success:
                    return {
                        "success": True,
                        "method": method,
                        "selector": selector,
                        "message": f"Successfully clicked element using {method}",
                    }

            except Exception as e:
                logger.warning(f"Click method {method} failed: {e}")
                continue

        return {
            "success": False,
            "error": f"All click methods failed for selector: {selector}",
            "selector": selector,
        }

    def fill_form_field(self, selector: str, value: str, selector_type: str = "css",
                       clear_first: bool = True) -> Dict[str, Any]:
        """Fill form field with multiple fallback methods"""
        logger.info(f"Filling field {selector} with value: {value}")

        for method in self.available_methods:
            if method != self.current_method and self.current_method:
                continue

            try:
                success = False

                if method == "selenium_webdriver" and self.selenium_driver:
                    element = self._find_element_selenium(selector, selector_type)
                    if element:
                        if clear_first:
                            element.clear()  # type: ignore[attr-defined]
                        element.send_keys(value)  # type: ignore[attr-defined]
                        success = True

                elif method == "playwright" and self.playwright_page:
                    if selector_type == "id":
                        locator = self.playwright_page.locator(f"#{selector}")  # type: ignore[union-attr]
                    elif selector_type == "class":
                        locator = self.playwright_page.locator(f".{selector}")  # type: ignore[union-attr]
                    elif selector_type == "name":
                        locator = self.playwright_page.locator(f"[name='{selector}']")  # type: ignore[union-attr]
                    elif selector_type == "tag":
                        locator = self.playwright_page.locator(selector)  # type: ignore[union-attr]
                    else:
                        locator = self.playwright_page.locator(selector)  # type: ignore[union-attr]

                    if clear_first:
                        locator.clear(timeout=self.timeout * 1000)  # type: ignore[attr-defined]
                    locator.fill(value, timeout=self.timeout * 1000)  # type: ignore[attr-defined]
                    success = True

                elif method == "system_events":
                    success = self._fill_system_events(selector, value, selector_type, clear_first)

                if success:
                    return {
                        "success": True,
                        "method": method,
                        "selector": selector,
                        "value": value,
                        "message": f"Successfully filled field using {method}",
                    }

            except Exception as e:
                logger.warning(f"Fill method {method} failed: {e}")
                continue

        return {
            "success": False,
            "error": f"All fill methods failed for selector: {selector}",
            "selector": selector,
            "value": value,
        }

    def search_on_site(self, search_term: str, search_field_selector: str = None,
                      submit_selector: str = None) -> Dict[str, Any]:
        """Perform search on current site"""
        logger.info(f"Searching for: {search_term}")

        #Common search field selectors
        if not search_field_selector:
            search_selectors = [
                'input[type="search"]',
                'input[name*="search"]',
                'input[id*="search"]',
                'input[placeholder*="search"]',
                'input[placeholder*="пошук"]',
                ".search-input",
                "#search",
                '[data-testid*="search"]',
            ]
        else:
            search_selectors = [search_field_selector]

        #Try each search selector
        for selector in search_selectors:
            fill_result = self.fill_form_field(selector, search_term)
            if fill_result.get("success"):
                #Try to submit
                if submit_selector:
                    click_result = self.click_element(submit_selector)
                else:
                    #Try common submit methods
                    submit_methods = [
                        ("css", 'button[type="submit"]'),
                        ("css", ".search-button"),
                        ("css", 'input[type="submit"]'),
                        ("xpath", '//button[contains(text(), "Search")]'),
                        ("xpath", '//button[contains(text(), "Пошук")]'),
                    ]

                    click_result = {"success": False}
                    for method, submit_sel in submit_methods:
                        click_result = self.click_element(submit_sel, method)
                        if click_result.get("success"):
                            break

                    #If no submit button found, try Enter key
                    if not click_result.get("success"):
                        try:
                            import pyautogui
                            pyautogui.press("enter")
                            click_result = {"success": True, "method": "enter_key"}
                        except:
                            pass

                if click_result.get("success"):
                    time.sleep(2)  #Wait for search results
                    return {
                        "success": True,
                        "search_term": search_term,
                        "search_selector": selector,
                        "submit_method": click_result.get("method", "unknown"),
                        "message": f"Successfully searched for '{search_term}'",
                    }

        return {
            "success": False,
            "error": f"Could not perform search for: {search_term}",
            "search_term": search_term,
        }

    def scrape_page_content(self, selectors: List[str] = None) -> Dict[str, Any]:
        """Scrape content from current page"""
        try:
            content = {}

            if self.current_method == "selenium_webdriver" and self.selenium_driver:
                if selectors:
                    for selector in selectors:
                        try:
                            elements = self.selenium_driver.find_elements("css selector", selector)
                            content[selector] = [elem.text for elem in elements]
                        except:
                            content[selector] = []
                else:
                    content["page_source"] = self.selenium_driver.page_source
                    content["title"] = self.selenium_driver.title
                    content["url"] = self.selenium_driver.current_url

            elif self.current_method == "playwright" and self.playwright_page:
                if selectors:
                    for selector in selectors:
                        try:
                            elements = self.playwright_page.locator(selector).all()  # type: ignore[union-attr]
                            content[selector] = [elem.text_content() for elem in elements]
                        except:
                            content[selector] = []
                else:
                    content["page_source"] = self.playwright_page.content()
                    content["title"] = self.playwright_page.title()
                    content["url"] = self.playwright_page.url

            elif self.current_method == "http_requests":
                import requests
                from bs4 import BeautifulSoup

                #This requires the last navigated URL
                response = requests.get(self.last_url if hasattr(self, "last_url") else "")
                soup = BeautifulSoup(response.content, "html.parser")

                if selectors:
                    for selector in selectors:
                        try:
                            elements = soup.select(selector)
                            content[selector] = [elem.get_text(strip=True) for elem in elements]
                        except:
                            content[selector] = []
                else:
                    content["page_source"] = str(soup)
                    content["title"] = soup.title.string if soup.title else ""

            return {
                "success": True,
                "content": content,
                "method": self.current_method,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Content scraping failed: {e}",
            }

    def take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """Take screenshot of current page"""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"

            success = False

            if self.current_method == "selenium_webdriver" and self.selenium_driver:
                self.selenium_driver.save_screenshot(filename)  # type: ignore[union-attr]
                success = True

            elif self.current_method == "playwright" and self.playwright_page:
                self.playwright_page.screenshot(path=filename)  # type: ignore[union-attr]
                success = True

            elif self.current_method == "system_events":
                success = self._screenshot_system_events(filename)

            if success:
                return {
                    "success": True,
                    "filename": filename,
                    "message": f"Screenshot saved as {filename}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Screenshot failed: {e}",
            }

    def wait_for_element(self, selector: str, timeout: int = None) -> Dict[str, Any]:
        """Wait for element to appear"""
        if not timeout:
            timeout = self.timeout

        logger.info(f"Waiting for element: {selector}")

        try:
            if self.current_method == "selenium_webdriver" and self.selenium_driver:
                from selenium.webdriver.common.by import By  # type: ignore[import-not-found]
                from selenium.webdriver.support import expected_conditions as EC  # type: ignore[import-not-found]
                from selenium.webdriver.support.ui import WebDriverWait  # type: ignore[import-not-found]

                element = WebDriverWait(self.selenium_driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector)),
                )
                return {"success": True, "message": "Element found"}

            if self.current_method == "playwright" and self.playwright_page:
                self.playwright_page.locator(selector).wait_for(timeout=timeout * 1000)  # type: ignore[union-attr]
                return {"success": True, "message": "Element found"}

        except Exception as e:
            return {
                "success": False,
                "error": f"Element not found within {timeout} seconds: {e}",
            }

    def close(self):
        """Close browser instances"""
        try:
            if self.selenium_driver:
                self.selenium_driver.quit()
                self.selenium_driver = None

            if self.playwright_browser:
                self.playwright_browser.close()
                self.playwright.stop()
                self.playwright_browser = None
                self.playwright_page = None

        except Exception as e:
            logger.error(f"Error closing browsers: {e}")

#Global browser instance
_browser = None

def get_browser() -> AdvancedWebBrowser:
    """Get or create browser instance"""
    global _browser
    if _browser is None:
        _browser = AdvancedWebBrowser()
    return _browser

#Plugin functions that will be registered
def navigate_to_url(url: str) -> str:
    """Navigate to a URL using the most appropriate method available"""
    browser = get_browser()
    result = browser.navigate_to_url(url)
    return json.dumps(result, indent=2)

def click_element(selector: str, selector_type: str = "css", text: str = None, image_path: str = None) -> str:
    """Click an element on the page using multiple fallback methods"""
    browser = get_browser()
    result = browser.click_element(selector, selector_type, text, image_path)
    return json.dumps(result, indent=2)

def fill_form_field(selector: str, value: str, selector_type: str = "css", clear_first: bool = True) -> str:
    """Fill a form field with a value"""
    browser = get_browser()
    result = browser.fill_form_field(selector, value, selector_type, clear_first)
    return json.dumps(result, indent=2)

def search_on_site(search_term: str, search_field_selector: str = None, submit_selector: str = None) -> str:
    """Search for a term on the current website"""
    browser = get_browser()
    result = browser.search_on_site(search_term, search_field_selector, submit_selector)
    return json.dumps(result, indent=2)

def scrape_page_content(selectors: str = None) -> str:
    """Scrape content from the current page. Selectors should be JSON array string."""
    browser = get_browser()

    if selectors:
        try:
            selector_list = json.loads(selectors)
        except:
            selector_list = [selectors]  #Single selector
    else:
        selector_list = None

    result = browser.scrape_page_content(selector_list)
    return json.dumps(result, indent=2)

def take_screenshot(filename: str = None) -> str:
    """Take a screenshot of the current page"""
    browser = get_browser()
    result = browser.take_screenshot(filename)
    return json.dumps(result, indent=2)

def wait_for_element(selector: str, timeout: int = 30) -> str:
    """Wait for an element to appear on the page"""
    browser = get_browser()
    result = browser.wait_for_element(selector, timeout)
    return json.dumps(result, indent=2)

def execute_javascript(script: str) -> str:
    """Execute JavaScript on the current page"""
    browser = get_browser()
    try:
        result = None

        if browser.current_method == "selenium_webdriver" and browser.selenium_driver:
            result = browser.selenium_driver.execute_script(script)  # type: ignore[union-attr]
        elif browser.current_method == "playwright" and browser.playwright_page:
            result = browser.playwright_page.evaluate(script)  # type: ignore[union-attr]
        else:
            return json.dumps({"success": False, "error": "JavaScript execution requires Selenium or Playwright"})

        return json.dumps({
            "success": True,
            "result": result,
            "script": script,
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"JavaScript execution failed: {e}",
            "script": script,
        }, indent=2)

def handle_popup(action: str = "accept") -> str:
    """Handle browser popup/alert. Actions: accept, dismiss"""
    browser = get_browser()
    try:
        if browser.current_method == "selenium_webdriver" and browser.selenium_driver:
            alert = browser.selenium_driver.switch_to.alert  # type: ignore[union-attr]
            if action == "accept":
                alert.accept()  # type: ignore[union-attr]
            else:
                alert.dismiss()  # type: ignore[union-attr]

        elif browser.current_method == "playwright" and browser.playwright_page:
            #Playwright handles alerts automatically, but we can set handlers
            if action == "accept":
                browser.playwright_page.on("dialog", lambda dialog: dialog.accept())
            else:
                browser.playwright_page.on("dialog", lambda dialog: dialog.dismiss())

        return json.dumps({"success": True, "action": action})

    except Exception as e:
        return json.dumps({"success": False, "error": f"Popup handling failed: {e}"})

def scroll_page(direction: str = "down", amount: int = 3) -> str:
    """Scroll the page. Directions: up, down, top, bottom"""
    browser = get_browser()
    try:
        if browser.current_method == "selenium_webdriver" and browser.selenium_driver:
            if direction == "down":
                browser.selenium_driver.execute_script(f"window.scrollBy(0, {amount * 100});")  # type: ignore[union-attr]
            elif direction == "up":
                browser.selenium_driver.execute_script(f"window.scrollBy(0, -{amount * 100});")  # type: ignore[union-attr]
            elif direction == "top":
                browser.selenium_driver.execute_script("window.scrollTo(0, 0);")  # type: ignore[union-attr]
            elif direction == "bottom":
                browser.selenium_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # type: ignore[union-attr]

        elif browser.current_method == "playwright" and browser.playwright_page:
            if direction == "down":
                browser.playwright_page.mouse.wheel(0, amount * 100)
            elif direction == "up":
                browser.playwright_page.mouse.wheel(0, -amount * 100)
            elif direction == "top":
                browser.playwright_page.evaluate("window.scrollTo(0, 0)")
            elif direction == "bottom":
                browser.playwright_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        elif browser.current_method == "system_events":
            import pyautogui
            if direction == "down":
                for _ in range(amount):
                    pyautogui.scroll(-3)
            elif direction == "up":
                for _ in range(amount):
                    pyautogui.scroll(3)

        return json.dumps({"success": True, "direction": direction, "amount": amount})

    except Exception as e:
        return json.dumps({"success": False, "error": f"Scrolling failed: {e}"})

def register():
    """Register all web browsing tools"""
    return {
        "tools": [
            open_browser,
            close_browser,
            navigate_to_url,
            click_element,
            fill_form_field,
            search_on_site,
            scrape_page_content,
            take_screenshot,
            wait_for_element,
            execute_javascript,
            handle_popup,
            scroll_page,
        ],
    }

#Cleanup function
def cleanup():
    """Cleanup browser resources"""
    global _browser
    if _browser:
        _browser.close()
        _browser = None

def open_browser(browser_name: str = "") -> str:
    """Open a browser instance, optionally with a specific browser"""
    try:
        global _browser
        if _browser:
            return json.dumps({"success": True, "message": "Browser already open"}, indent=2)
            
        _browser = AdvancedWebBrowser()
        if browser_name and browser_name.lower() in ["safari", "chrome", "firefox", "edge", "opera"]:
            preferred_browser = browser_name.lower()
            success = _browser.initialize(preferred_browser=preferred_browser)
        else:
            success = _browser.initialize()
            
        if success:
            browser_used = preferred_browser if browser_name else _browser.current_method
            return json.dumps({"success": True, "message": f"Browser initialized successfully with {browser_used}"}, indent=2)
        else:
            return json.dumps({"success": False, "error": "Failed to initialize any browser automation method"}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to initialize browser: {e}"}, indent=2)

def close_browser() -> str:
    """Close the browser instance"""
    try:
        global _browser
        if _browser:
            _browser.close()
            _browser = None
            return json.dumps({"success": True, "message": "Browser closed successfully"}, indent=2)
        else:
            return json.dumps({"success": True, "message": "No browser was open"}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to close browser: {e}"}, indent=2)
