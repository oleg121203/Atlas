from typing import Dict, List, Any
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

class BrowserAnalysis:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.logger = logging.getLogger(__name__)

    def analyze_page(self) -> Dict[str, Any]:
        """Analyze the current page content."""
        try:
            # Get page metadata
            title = self.driver.title
            url = self.driver.current_url
            
            # Get page content
            content = self.driver.page_source
            
            # Analyze links
            links = self._find_links()
            
            # Analyze text content
            text = self._extract_text()
            keywords = self._extract_keywords(text)
            
            # Analyze images
            images = self._find_images()
            
            return {
                "success": True,
                "data": {
                    "title": title,
                    "url": url,
                    "links": links,
                    "text": text,
                    "keywords": keywords,
                    "images": images
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to analyze page: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _find_links(self) -> List[Dict[str, Any]]:
        """Find and analyze links on the page."""
        try:
            elements = self.driver.find_elements(By.TAG_NAME, 'a')
            links = []
            for element in elements:
                href = element.get_attribute('href')
                text = element.text
                if href and text:
                    links.append({
                        'text': text,
                        'url': href,
                        'attributes': element.get_attribute('outerHTML')
                    })
            return links
        except Exception as e:
            self.logger.error(f"Failed to find links: {e}")
            return []

    def _extract_text(self) -> str:
        """Extract visible text from the page."""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, 'body *')
            text = ' '.join(element.text for element in elements if element.text)
            return text
        except Exception as e:
            self.logger.error(f"Failed to extract text: {e}")
            return ""

    def _extract_keywords(self, text: str) -> Dict[str, int]:
        """Extract keywords from text."""
        try:
            # Remove punctuation and split into words
            words = re.findall(r'\w+', text.lower())
            
            # Count word frequencies
            keywords = {}
            for word in words:
                if len(word) > 2:  # Ignore short words
                    keywords[word] = keywords.get(word, 0) + 1
            
            return keywords
        except Exception as e:
            self.logger.error(f"Failed to extract keywords: {e}")
            return {}

    def _find_images(self) -> List[Dict[str, Any]]:
        """Find and analyze images on the page."""
        try:
            elements = self.driver.find_elements(By.TAG_NAME, 'img')
            images = []
            for element in elements:
                src = element.get_attribute('src')
                alt = element.get_attribute('alt')
                if src:
                    images.append({
                        'src': src,
                        'alt': alt or "",
                        'attributes': element.get_attribute('outerHTML')
                    })
            return images
        except Exception as e:
            self.logger.error(f"Failed to find images: {e}")
            return []

    def find_elements_by_text(self, text: str) -> List[Any]:
        """Find elements containing specific text."""
        try:
            elements = self.driver.find_elements(By.XPATH, f"//*[text()[contains(., '{text}')]]")
            return elements
        except Exception as e:
            self.logger.error(f"Failed to find elements by text: {e}")
            return []

    def find_elements_by_attribute(self, 
                                 attribute: str, 
                                 value: str) -> List[Any]:
        """Find elements by attribute value."""
        try:
            elements = self.driver.find_elements(By.XPATH, f"//*[@{attribute}='{value}']")
            return elements
        except Exception as e:
            self.logger.error(f"Failed to find elements by attribute: {e}")
            return []
