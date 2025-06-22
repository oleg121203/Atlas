from typing import Dict, Optional, List, Any, Tuple
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import cv2
import numpy as np
from PIL import Image
import io
from tools.image_recognition_tool import find_template_in_image

class ElementRecognizer:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.logger = logging.getLogger(__name__)

    def find_element_by_image(self, template_path: str, threshold: float = 0.8) -> Dict[str, Any]:
        """Find element by matching image template."""
        try:
            # Get current page screenshot
            screenshot = self.driver.get_screenshot_as_png()
            screenshot = Image.open(io.BytesIO(screenshot))
            screenshot = np.array(screenshot)
            
            # Load template image
            template = cv2.imread(template_path)
            
            # Find template in screenshot
            result = find_template_in_image(screenshot, template, threshold)
            
            if result['success']:
                # Get element coordinates
                x, y, w, h = result['data']['position']
                
                # Click on the element
                script = f"""
                    var element = document.elementFromPoint({x + w/2}, {y + h/2});
                    if (element) {{
                        element.click();
                        return element;
                    }}
                    return null;
                """
                element = self.driver.execute_script(script)
                
                return {
                    "success": True,
                    "data": {
                        "element": element,
                        "position": (x, y, w, h),
                        "confidence": result['data']['confidence']
                    }
                }
            
            return {
                "success": False,
                "error": "Template not found"
            }
        except Exception as e:
            self.logger.error(f"Failed to find element by image: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def find_element_by_text(self, text: str, exact_match: bool = False) -> Dict[str, Any]:
        """Find element by text content."""
        try:
            elements = self.driver.find_elements(By.XPATH, f"//*[text()[contains(., '{text}')]]")
            
            if not elements:
                return {
                    "success": False,
                    "error": "No elements found with matching text"
                }
            
            # If exact match is required, filter elements
            if exact_match:
                elements = [e for e in elements if e.text.strip() == text.strip()]
                
            if not elements:
                return {
                    "success": False,
                    "error": "No elements found with exact matching text"
                }
            
            return {
                "success": True,
                "data": {
                    "elements": elements,
                    "count": len(elements)
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to find element by text: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def find_element_by_css(self, selector: str) -> Dict[str, Any]:
        """Find element by CSS selector."""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            
            if not elements:
                return {
                    "success": False,
                    "error": "No elements found with matching selector"
                }
            
            return {
                "success": True,
                "data": {
                    "elements": elements,
                    "count": len(elements)
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to find element by CSS: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_element_position(self, element: Any) -> Dict[str, Any]:
        """Get element position on the page."""
        try:
            rect = element.rect
            return {
                "success": True,
                "data": {
                    "x": rect['x'],
                    "y": rect['y'],
                    "width": rect['width'],
                    "height": rect['height']
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get element position: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_element(self, element: Any) -> Dict[str, Any]:
        """Analyze element properties."""
        try:
            # Get element properties
            properties = {
                "tag_name": element.tag_name,
                "class": element.get_attribute('class'),
                "id": element.get_attribute('id'),
                "text": element.text,
                "attributes": element.get_attribute('outerHTML')
            }
            
            # Get element position
            position = self.get_element_position(element)
            
            return {
                "success": True,
                "data": {
                    "properties": properties,
                    "position": position['data'] if position['success'] else None
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to analyze element: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def find_similar_elements(self, element: Any, threshold: float = 0.8) -> Dict[str, Any]:
        """Find elements similar to the given element."""
        try:
            # Get element properties
            properties = self.analyze_element(element)
            if not properties['success']:
                return properties
                
            # Build CSS selector based on properties
            selectors = []
            if properties['data']['properties']['class']:
                selectors.append(f".{properties['data']['properties']['class']}")
            if properties['data']['properties']['id']:
                selectors.append(f"#{properties['data']['properties']['id']}")
                
            # Find similar elements
            similar_elements = []
            for selector in selectors:
                result = self.find_element_by_css(selector)
                if result['success']:
                    similar_elements.extend(result['data']['elements'])
            
            return {
                "success": True,
                "data": {
                    "elements": similar_elements,
                    "count": len(similar_elements)
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to find similar elements: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_element_screenshot(self, element: Any) -> Dict[str, Any]:
        """Get screenshot of an element."""
        try:
            # Get element position
            position = self.get_element_position(element)
            if not position['success']:
                return position
                
            # Get element screenshot
            screenshot = element.screenshot_as_png
            image = Image.open(io.BytesIO(screenshot))
            
            return {
                "success": True,
                "data": {
                    "image": image,
                    "position": position['data']
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get element screenshot: {e}")
            return {
                "success": False,
                "error": str(e)
            }
