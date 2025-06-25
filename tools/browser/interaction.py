from typing import Dict, List, Any
import logging
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserInteraction:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.logger = logging.getLogger(__name__)

    def human_like_typing(self, 
                         element: Any, 
                         text: str, 
                         min_delay: float = 0.05, 
                         max_delay: float = 0.2) -> Dict[str, Any]:
        """Type text with human-like timing."""
        try:
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(min_delay, max_delay))
            return {
                "success": True,
                "data": {
                    "message": "Text typed successfully"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to type text: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def human_like_click(self, element: Any) -> Dict[str, Any]:
        """Click element with human-like behavior."""
        try:
            # Move mouse to element
            self.driver.execute_script("""
                var element = arguments[0];
                var rect = element.getBoundingClientRect();
                var x = rect.left + (rect.width / 2);
                var y = rect.top + (rect.height / 2);
                
                // Simulate mouse movement
                var steps = 10;
                var stepX = (x - window.innerWidth / 2) / steps;
                var stepY = (y - window.innerHeight / 2) / steps;
                
                for (var i = 0; i < steps; i++) {
                    window.dispatchEvent(new MouseEvent('mousemove', {
                        clientX: window.innerWidth / 2 + stepX * i,
                        clientY: window.innerHeight / 2 + stepY * i
                    }));
                }
            """, element)
            
            # Click with delay
            time.sleep(random.uniform(0.1, 0.3))
            element.click()
            
            return {
                "success": True,
                "data": {
                    "message": "Element clicked with human-like behavior"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to click element: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def copy_text(self, selector: str, timeout: int = 10) -> Dict[str, Any]:
        """Copy text from an element."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # Select text
            self.driver.execute_script("""
                var element = arguments[0];
                var range = document.createRange();
                range.selectNodeContents(element);
                var selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
            """, element)
            
            # Copy text
            self.driver.execute_script("document.execCommand('copy');")
            
            # Get copied text
            copied_text = self.driver.execute_script("""
                var textarea = document.createElement('textarea');
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.value = navigator.clipboard.readText();
                var result = textarea.value;
                document.body.removeChild(textarea);
                return result;
            """)
            
            return {
                "success": True,
                "data": {
                    "text": copied_text
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to copy text: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def paste_text(self, selector: str, timeout: int = 10) -> Dict[str, Any]:
        """Paste text into an element."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # Paste text
            self.driver.execute_script("""
                var element = arguments[0];
                element.focus();
                document.execCommand('paste');
            """, element)
            
            return {
                "success": True,
                "data": {
                    "message": "Text pasted successfully"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to paste text: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def simulate_mouse_movements(self, 
                               elements: List[Any], 
                               duration: float = 5.0) -> Dict[str, Any]:
        """Simulate natural mouse movements over elements."""
        try:
            if not elements:
                return {
                    "success": False,
                    "error": "No elements provided"
                }
            
            start_time = time.time()
            current_time = start_time
            
            while current_time - start_time < duration:
                # Randomly select an element
                element = random.choice(elements)
                
                # Move mouse to element
                self.driver.execute_script("""
                    var element = arguments[0];
                    var rect = element.getBoundingClientRect();
                    var x = rect.left + (rect.width / 2);
                    var y = rect.top + (rect.height / 2);
                    
                    // Simulate mouse movement
                    var steps = 10;
                    var stepX = (x - window.innerWidth / 2) / steps;
                    var stepY = (y - window.innerHeight / 2) / steps;
                    
                    for (var i = 0; i < steps; i++) {
                        window.dispatchEvent(new MouseEvent('mousemove', {
                            clientX: window.innerWidth / 2 + stepX * i,
                            clientY: window.innerHeight / 2 + stepY * i,
                            movementX: stepX,
                            movementY: stepY
                        }));
                        
                        // Random delay between movements
                        var delay = Math.random() * 50;
                        setTimeout(function() {}, delay);
                    }
                """, element)
                
                # Random delay between movements
                time.sleep(random.uniform(0.1, 0.5))
                current_time = time.time()
            
            return {
                "success": True,
                "data": {
                    "message": "Mouse movements simulated"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to simulate mouse movements: {e}")
            return {
                "success": False,
                "error": str(e)
            }
