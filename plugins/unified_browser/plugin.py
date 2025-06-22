"""
Unified Browser Plugin for Atlas

This plugin provides comprehensive browser automation with multiple methods:
1. AppleScript (macOS primary)
2. Selenium WebDriver (cross-platform)
3. Playwright (cross-platform)
4. System Events (fallback)
5. Direct HTTP requests (final fallback)
"""

import json
import logging
import os
import time
import subprocess
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class BrowserMethod:
    """Base class for browser automation methods."""
    
    def __init__(self, name: str):
        self.name = name
        self.is_available = False
        self.is_initialized = False
    
    def check_availability(self) -> bool:
        """Check if this method is available."""
        return False
    
    def initialize(self) -> bool:
        """Initialize the method."""
        return False
    
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to URL."""
        return {"success": False, "error": "Not implemented"}
    
    def get_page_title(self) -> Dict[str, Any]:
        """Get page title."""
        return {"success": False, "error": "Not implemented"}
    
    def execute_javascript(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript."""
        return {"success": False, "error": "Not implemented"}
    
    def close(self) -> Dict[str, Any]:
        """Close browser."""
        return {"success": False, "error": "Not implemented"}

class AppleScriptMethod(BrowserMethod):
    """AppleScript browser automation for macOS."""
    
    def __init__(self):
        super().__init__("applescript")
        self.is_macos = os.name == "posix" and os.uname().sysname == "Darwin"
        self.current_browser = "Safari"
    
    def check_availability(self) -> bool:
        """Check if AppleScript is available."""
        if not self.is_macos:
            return False
        
        try:
            # Test AppleScript availability
            result = subprocess.run(["osascript", "-e", "return 1"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def initialize(self) -> bool:
        """Initialize AppleScript method."""
        if not self.check_availability():
            return False
        
        self.is_available = True
        self.is_initialized = True
        logger.info("AppleScript method initialized")
        return True
    
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to URL using AppleScript."""
        if not self.is_initialized:
            return {"success": False, "error": "AppleScript not initialized"}
        
        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            script = f"""
            tell application "{self.current_browser}"
                activate
                if (count of windows) = 0 then
                    make new document
                end if
                set URL of document 1 to "{url}"
            end tell
            """
            
            result = subprocess.run(["osascript", "-e", script], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Successfully navigated to {url}",
                    "url": url,
                    "browser": self.current_browser,
                    "method": self.name
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "method": self.name
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout navigating to URL",
                "method": self.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": self.name
            }
    
    def get_page_title(self) -> Dict[str, Any]:
        """Get page title using AppleScript."""
        if not self.is_initialized:
            return {"success": False, "error": "AppleScript not initialized"}
        
        try:
            script = f"""
            tell application "{self.current_browser}"
                activate
                if (count of windows) > 0 and (count of documents) > 0 then
                    return name of document 1
                else
                    return "No page loaded"
                end if
            end tell
            """
            
            result = subprocess.run(["osascript", "-e", script], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                title = result.stdout.strip()
                return {
                    "success": True,
                    "title": title,
                    "method": self.name
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "method": self.name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": self.name
            }
    
    def execute_javascript(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript using AppleScript."""
        if not self.is_initialized:
            return {"success": False, "error": "AppleScript not initialized"}
        
        try:
            applescript = f"""
            tell application "{self.current_browser}"
                activate
                tell document 1
                    do JavaScript "{script}"
                end tell
            end tell
            """
            
            result = subprocess.run(["osascript", "-e", applescript], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "result": result.stdout.strip(),
                    "method": self.name
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "method": self.name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": self.name
            }
    
    def close(self) -> Dict[str, Any]:
        """Close browser using AppleScript."""
        if not self.is_initialized:
            return {"success": False, "error": "AppleScript not initialized"}
        
        try:
            script = f"""
            tell application "{self.current_browser}"
                quit
            end tell
            """
            
            result = subprocess.run(["osascript", "-e", script], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Closed {self.current_browser}",
                    "method": self.name
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "method": self.name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": self.name
            }

class SeleniumMethod(BrowserMethod):
    """Selenium WebDriver browser automation."""
    
    def __init__(self):
        super().__init__("selenium")
        self.driver = None
    
    def check_availability(self) -> bool:
        """Check if Selenium is available."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            return True
        except ImportError:
            return False
    
    def initialize(self) -> bool:
        """Initialize Selenium method."""
        if not self.check_availability():
            return False
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=options)
            self.is_available = True
            self.is_initialized = True
            logger.info("Selenium method initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            return False
    
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to URL using Selenium."""
        if not self.is_initialized or not self.driver:
            return {"success": False, "error": "Selenium not initialized"}
        
        try:
            # Ensure URL has protocol
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            self.driver.get(url)
            
            return {
                "success": True,
                "message": f"Successfully navigated to {url}",
                "url": url,
                "method": self.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": self.name
            }
    
    def get_page_title(self) -> Dict[str, Any]:
        """Get page title using Selenium."""
        if not self.is_initialized or not self.driver:
            return {"success": False, "error": "Selenium not initialized"}
        
        try:
            title = self.driver.title
            return {
                "success": True,
                "title": title,
                "method": self.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": self.name
            }
    
    def execute_javascript(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript using Selenium."""
        if not self.is_initialized or not self.driver:
            return {"success": False, "error": "Selenium not initialized"}
        
        try:
            result = self.driver.execute_script(script)
            return {
                "success": True,
                "result": result,
                "method": self.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": self.name
            }
    
    def close(self) -> Dict[str, Any]:
        """Close browser using Selenium."""
        if not self.is_initialized or not self.driver:
            return {"success": False, "error": "Selenium not initialized"}
        
        try:
            self.driver.quit()
            self.driver = None
            self.is_initialized = False
            
            return {
                "success": True,
                "message": "Browser closed",
                "method": self.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": self.name
            }

class UnifiedBrowserPlugin:
    """Unified browser automation plugin for Atlas."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.methods = {}
        self.current_method = None
        self.preferred_method = self.config.get("preferred_method", "applescript")
        
        # Initialize available methods
        self._initialize_methods()
    
    def initialize(self, llm_manager=None, atlas_app=None, agent_manager=None) -> bool:
        """Initialize the plugin."""
        try:
            # Try to initialize preferred method first
            if self.preferred_method in self.methods:
                if self.methods[self.preferred_method].initialize():
                    self.current_method = self.preferred_method
                    logger.info(f"Unified browser plugin initialized with preferred method: {self.preferred_method}")
                    return True
            
            # Try other available methods
            for method_name, method in self.methods.items():
                if method.check_availability() and method.initialize():
                    self.current_method = method_name
                    logger.info(f"Unified browser plugin initialized with method: {method_name}")
                    return True
            
            logger.error("No browser automation methods available")
            return False
                
        except Exception as e:
            logger.error(f"Failed to initialize unified browser plugin: {e}")
            return False
    
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to URL using current method."""
        if not self.current_method or self.current_method not in self.methods:
            return {"success": False, "error": "No browser method available"}
        
        return self.methods[self.current_method].navigate_to_url(url)
    
    def get_page_title(self) -> Dict[str, Any]:
        """Get page title using current method."""
        if not self.current_method or self.current_method not in self.methods:
            return {"success": False, "error": "No browser method available"}
        
        return self.methods[self.current_method].get_page_title()
    
    def execute_javascript(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript using current method."""
        if not self.current_method or self.current_method not in self.methods:
            return {"success": False, "error": "No browser method available"}
        
        return self.methods[self.current_method].execute_javascript(script)
    
    def close_browser(self) -> Dict[str, Any]:
        """Close browser using current method."""
        if not self.current_method or self.current_method not in self.methods:
            return {"success": False, "error": "No browser method available"}
        
        return self.methods[self.current_method].close()
    
    def switch_method(self, method_name: str) -> Dict[str, Any]:
        """Switch to a different browser method."""
        if method_name not in self.methods:
            return {"success": False, "error": f"Method {method_name} not available"}
        
        if not self.methods[method_name].check_availability():
            return {"success": False, "error": f"Method {method_name} not available on this system"}
        
        # Close current method if initialized
        if self.current_method and self.current_method in self.methods:
            self.methods[self.current_method].close()
        
        # Initialize new method
        if self.methods[method_name].initialize():
            self.current_method = method_name
            return {
                "success": True,
                "message": f"Switched to {method_name} method",
                "method": method_name
            }
        else:
            return {"success": False, "error": f"Failed to initialize {method_name} method"}
    
    def get_available_methods(self) -> Dict[str, Any]:
        """Get list of available methods."""
        available = {}
        for name, method in self.methods.items():
            available[name] = {
                "available": method.check_availability(),
                "initialized": method.is_initialized
            }
        
        return {
            "success": True,
            "methods": available,
            "current_method": self.current_method
        }
    
    def _initialize_methods(self):
        """Initialize available browser methods."""
        # Add AppleScript method
        self.methods["applescript"] = AppleScriptMethod()
        
        # Add Selenium method
        self.methods["selenium"] = SeleniumMethod()
        
        # Add other methods as needed
        # self.methods["playwright"] = PlaywrightMethod()
        # self.methods["system_events"] = SystemEventsMethod()
        # self.methods["http_requests"] = HttpRequestsMethod()

def register(llm_manager=None, atlas_app=None, agent_manager=None):
    """Register the Unified Browser plugin."""
    plugin = UnifiedBrowserPlugin()
    if plugin.initialize(llm_manager, atlas_app, agent_manager):
        return {
            "tools": [
                plugin.navigate_to_url,
                plugin.get_page_title,
                plugin.execute_javascript,
                plugin.close_browser,
                plugin.switch_method,
                plugin.get_available_methods
            ],
            "agents": []
        }
    else:
        logger.warning("Unified browser plugin initialization failed")
        return {"tools": [], "agents": []} 