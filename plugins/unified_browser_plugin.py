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

from .base_plugin import BasePlugin, PluginMetadata, PluginResult

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
                    "message": f"{self.current_browser} closed successfully",
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
            return True
        except ImportError:
            return False
    
    def initialize(self) -> bool:
        """Initialize Selenium WebDriver."""
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
            logger.error(f"Selenium initialization failed: {e}")
            return False
    
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to URL using Selenium."""
        if not self.is_initialized or not self.driver:
            return {"success": False, "error": "Selenium not initialized"}
        
        try:
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
    
    def close(self) -> Dict[str, Any]:
        """Close browser using Selenium."""
        if not self.is_initialized or not self.driver:
            return {"success": False, "error": "Selenium not initialized"}
        
        try:
            self.driver.quit()
            self.driver = None
            return {
                "success": True,
                "message": "Browser closed successfully",
                "method": self.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": self.name
            }

class UnifiedBrowserPlugin(BasePlugin):
    """Unified browser automation plugin with multiple methods."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.methods = {}
        self.current_method = None
        self.preferred_method = self.config.get("preferred_method", "applescript")
        
        # Initialize available methods
        self._initialize_methods()
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="unified_browser",
            version="2.0.0",
            description="Unified browser automation with multiple methods (AppleScript, Selenium, Playwright)",
            author="Atlas Team",
            category="automation",
            tags=["browser", "automation", "web", "selenium", "applescript"],
            dependencies=["selenium", "playwright"],
            config_schema={
                "preferred_method": {"type": "string", "default": "applescript"},
                "timeout": {"type": "integer", "default": 30},
                "headless": {"type": "boolean", "default": False}
            }
        )
    
    def initialize(self, provider: Any) -> bool:
        """Initialize the plugin with the active provider."""
        try:
            self.active_provider = provider
            
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
    
    def execute(self, command: str, **kwargs) -> PluginResult:
        """Execute a browser plugin command."""
        if not self.current_method:
            return PluginResult(
                success=False,
                error="No browser method initialized"
            )
        
        method = self.methods[self.current_method]
        
        try:
            if command == "navigate_to_url":
                result = method.navigate_to_url(kwargs.get("url", ""))
            elif command == "get_page_title":
                result = method.get_page_title()
            elif command == "open_browser":
                result = {"success": True, "message": f"Browser ready with {self.current_method}"}
            elif command == "close_browser":
                result = method.close()
            elif command == "execute_javascript":
                result = method.execute_javascript(kwargs.get("script", ""))
            elif command == "open_gmail":
                result = method.navigate_to_url("https://gmail.com")
            elif command == "search_gmail":
                # First navigate to Gmail
                nav_result = method.navigate_to_url("https://gmail.com")
                if nav_result["success"]:
                    time.sleep(3)
                    # Search using JavaScript
                    search_script = f"""
                    document.querySelector('[aria-label="Search mail"]').value = '{kwargs.get("query", "")}';
                    document.querySelector('[aria-label="Search mail"]').form.submit();
                    """
                    result = method.execute_javascript(search_script)
                else:
                    result = nav_result
            else:
                return PluginResult(
                    success=False,
                    error=f"Unknown command: {command}"
                )
            
            return PluginResult(
                success=result.get("success", False),
                data=result,
                error=result.get("error"),
                metadata={"method": self.current_method}
            )
                
        except Exception as e:
            logger.error(f"Error executing browser command {command}: {e}")
            return PluginResult(
                success=False,
                error=str(e),
                metadata={"method": self.current_method}
            )
    
    def get_commands(self) -> List[str]:
        """Get list of available commands."""
        return [
            "navigate_to_url",
            "get_page_title",
            "open_browser",
            "close_browser",
            "execute_javascript",
            "open_gmail",
            "search_gmail"
        ]
    
    def get_help(self) -> str:
        """Get help information for the plugin."""
        available_methods = [name for name, method in self.methods.items() if method.check_availability()]
        
        help_text = f"""
Unified Browser Plugin Help
===========================

Description: {self.metadata.description}

Available Commands:
- navigate_to_url: Navigate to a specific URL
- get_page_title: Get the title of the current page
- open_browser: Initialize browser (ready state)
- close_browser: Close the browser
- execute_javascript: Execute JavaScript code
- open_gmail: Open Gmail in the browser
- search_gmail: Search within Gmail

Usage Examples:
- navigate_to_url(url="https://gmail.com")
- open_gmail()
- search_gmail(query="security")
- get_page_title()
- close_browser()

Current Method: {self.current_method or "None"}
Available Methods: {', '.join(available_methods)}
Preferred Method: {self.preferred_method}
        """
        return help_text.strip()
    
    def _initialize_methods(self):
        """Initialize available browser methods."""
        # AppleScript method (macOS)
        self.methods["applescript"] = AppleScriptMethod()
        
        # Selenium method (cross-platform)
        self.methods["selenium"] = SeleniumMethod()
        
        # TODO: Add Playwright and System Events methods
        # self.methods["playwright"] = PlaywrightMethod()
        # self.methods["system_events"] = SystemEventsMethod()
    
    def get_available_methods(self) -> List[str]:
        """Get list of available methods."""
        return [name for name, method in self.methods.items() if method.check_availability()]
    
    def switch_method(self, method_name: str) -> bool:
        """Switch to a different browser method."""
        if method_name not in self.methods:
            return False
        
        method = self.methods[method_name]
        if method.check_availability() and method.initialize():
            # Close current method if it exists
            if self.current_method and self.current_method != method_name:
                self.methods[self.current_method].close()
            
            self.current_method = method_name
            logger.info(f"Switched to method: {method_name}")
            return True
        
        return False

# Plugin registration function
def register_unified_browser_plugin(config: Optional[Dict[str, Any]] = None) -> bool:
    """Register the unified browser plugin."""
    from .base_plugin import register_plugin
    
    plugin = UnifiedBrowserPlugin(config)
    return register_plugin(plugin) 