import unittest
from unittest.mock import Mock, patch
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tools.browser import BrowserTool
from tools.browser.navigation import BrowserNavigation
from tools.browser.interaction import BrowserInteraction
from tools.browser.analysis import BrowserAnalysis

class TestBrowserTool(unittest.TestCase):
    def setUp(self):
        self.logger = Mock()
        self.driver = Mock(spec=webdriver.Chrome)
        self.navigation = Mock(spec=BrowserNavigation)
        self.interaction = Mock(spec=BrowserInteraction)
        self.analysis = Mock(spec=BrowserAnalysis)
        
        # Create a mock BrowserTool instance
        self.browser_tool = BrowserTool(self.logger)
        self.browser_tool.driver = self.driver
        self.browser_tool.navigation = self.navigation
        self.browser_tool.interaction = self.interaction
        self.browser_tool.analysis = self.analysis

    def test_open_url(self):
        url = "https://example.com"
        expected_result = {"success": True, "data": {"url": url, "title": "Example"}}
        
        self.navigation.navigate_to.return_value = expected_result
        
        result = self.browser_tool.open_url(url)
        self.assertEqual(result, expected_result)
        self.navigation.navigate_to.assert_called_once_with(url)

    def test_find_links(self):
        selector = "a"
        text_contains = "example"
        timeout = 5
        expected_result = {"success": True, "data": []}
        
        self.navigation.find_links.return_value = expected_result
        
        result = self.browser_tool.find_links(selector, text_contains, timeout)
        self.assertEqual(result, expected_result)
        self.navigation.find_links.assert_called_once_with(selector, text_contains, timeout)

    def test_click_link(self):
        selector = "a"
        text_contains = "example"
        timeout = 5
        expected_result = {"success": True, "data": {"message": "Link clicked successfully"}}
        
        self.navigation.click_link.return_value = expected_result
        
        result = self.browser_tool.click_link(selector, text_contains, timeout)
        self.assertEqual(result, expected_result)
        self.navigation.click_link.assert_called_once_with(selector, text_contains, timeout)

    def test_scroll_to_element(self):
        element = Mock()
        expected_result = {"success": True, "data": {"message": "Scrolled to element"}}
        
        self.navigation.scroll_to_element.return_value = expected_result
        
        result = self.browser_tool.scroll_to_element(element)
        self.assertEqual(result, expected_result)
        self.navigation.scroll_to_element.assert_called_once_with(element)

    def test_human_like_typing(self):
        element = Mock()
        text = "example text"
        expected_result = {"success": True, "data": {"message": "Text typed successfully"}}
        
        self.interaction.human_like_typing.return_value = expected_result
        
        result = self.browser_tool.human_like_typing(element, text)
        self.assertEqual(result, expected_result)
        self.interaction.human_like_typing.assert_called_once_with(element, text)

    def test_analyze_page(self):
        expected_result = {
            "success": True,
            "data": {
                "title": "Example",
                "url": "https://example.com",
                "links": [],
                "text": "",
                "keywords": {},
                "images": []
            }
        }
        
        self.analysis.analyze_page.return_value = expected_result
        
        result = self.browser_tool.analyze_page()
        self.assertEqual(result, expected_result)
        self.analysis.analyze_page.assert_called_once()

    def test_find_elements_by_text(self):
        text = "example"
        expected_result = [Mock()]
        
        self.analysis.find_elements_by_text.return_value = expected_result
        
        result = self.browser_tool.find_elements_by_text(text)
        self.assertEqual(result, expected_result)
        self.analysis.find_elements_by_text.assert_called_once_with(text)

    def test_close_browser(self):
        expected_result = {"success": True, "data": {"message": "Browser closed successfully"}}
        
        self.browser_tool.close_browser()
        self.driver.quit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
