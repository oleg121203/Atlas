"""
Email Strategy Manager for Atlas System

Automatically chooses between Gmail API and browser automation
based on availability and requirements.
"""

from typing import Dict, Any, Optional, List
import logging
from enum import Enum
import os
import json

class EmailAccessMethod(Enum):
    """Available email access methods."""
    GMAIL_API = "gmail_api"
    BROWSER_AUTOMATION = "browser_automation"
    HYBRID = "hybrid"

class EmailStrategyManager:
    """Manages email access strategy and method selection."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gmail_api_available = False
        self.browser_available = False
        self.current_method = None
        self._check_availability()
    
    def _check_availability(self):
        """Check availability of different email access methods."""
        
        # Check Gmail API availability
        self.gmail_api_available = self._check_gmail_api()
        
        # Check browser automation availability
        self.browser_available = self._check_browser_automation()
        
        self.logger.info(f"Email access methods - Gmail API: {self.gmail_api_available}, Browser: {self.browser_available}")
    
    def _check_gmail_api(self) -> bool:
        """Check if Gmail API is available and configured."""
        try:
            # Check for Gmail API credentials
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
            
            # Check if credentials file exists
            creds_path = os.path.expanduser("~/.atlas/gmail_credentials.json")
            if os.path.exists(creds_path):
                return True
            
            # Check if token file exists
            token_path = os.path.expanduser("~/.atlas/gmail_token.json")
            if os.path.exists(token_path):
                return True
            
            # Check environment variables
            if os.getenv("GMAIL_API_KEY") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                return True
                
            return False
            
        except ImportError:
            self.logger.warning("Gmail API libraries not available")
            return False
        except Exception as e:
            self.logger.error(f"Error checking Gmail API: {e}")
            return False
    
    def _check_browser_automation(self) -> bool:
        """Check if browser automation is available."""
        try:
            # Check if browser tools are available
            from tools.browser import BrowserTool
            return True
        except ImportError:
            self.logger.warning("Browser automation not available")
            return False
        except Exception as e:
            self.logger.error(f"Error checking browser automation: {e}")
            return False
    
    def select_access_method(self, task_description: str) -> Optional[EmailAccessMethod]:
        """
        Select the best email access method for a given task.
        
        Args:
            task_description: Description of the email task
            
        Returns:
            Selected access method
        """
        task_lower = task_description.lower()
        
        # Priority 1: Gmail API for search and filtering tasks
        if self.gmail_api_available and any(keyword in task_lower for keyword in [
            "search", "find", "filter", "security", "account", "emails", "gmail"
        ]):
            self.current_method = EmailAccessMethod.GMAIL_API
            self.logger.info("Selected Gmail API for email task")
            return EmailAccessMethod.GMAIL_API
        
        # Priority 2: Browser automation for UI interaction tasks
        elif self.browser_available and any(keyword in task_lower for keyword in [
            "browser", "safari", "navigate", "open", "click", "interact"
        ]):
            self.current_method = EmailAccessMethod.BROWSER_AUTOMATION
            self.logger.info("Selected Browser Automation for email task")
            return EmailAccessMethod.BROWSER_AUTOMATION
        
        # Priority 3: Hybrid approach for complex tasks
        elif self.gmail_api_available and self.browser_available:
            self.current_method = EmailAccessMethod.HYBRID
            self.logger.info("Selected Hybrid approach for email task")
            return EmailAccessMethod.HYBRID
        
        # Fallback: Use available method
        elif self.gmail_api_available:
            self.current_method = EmailAccessMethod.GMAIL_API
            self.logger.info("Fallback to Gmail API")
            return EmailAccessMethod.GMAIL_API
        elif self.browser_available:
            self.current_method = EmailAccessMethod.BROWSER_AUTOMATION
            self.logger.info("Fallback to Browser Automation")
            return EmailAccessMethod.BROWSER_AUTOMATION
        else:
            self.logger.error("No email access methods available")
            return None
    
    def get_tool_for_method(self, method: EmailAccessMethod) -> str:
        """
        Get the appropriate tool name for the selected method.
        
        Args:
            method: Selected access method
            
        Returns:
            Tool name to use
        """
        if method == EmailAccessMethod.GMAIL_API:
            return "EmailFilter"  # Use our Gmail API tool
        elif method == EmailAccessMethod.BROWSER_AUTOMATION:
            return "BrowserTool"  # Use browser automation
        elif method == EmailAccessMethod.HYBRID:
            return "EmailFilter"  # Start with API, fallback to browser
        else:
            return "generic_executor"
    
    def get_tool_arguments(self, method: EmailAccessMethod, task_description: str) -> Dict[str, Any]:
        """
        Get appropriate tool arguments for the selected method.
        
        Args:
            method: Selected access method
            task_description: Description of the task
            
        Returns:
            Dictionary of tool arguments
        """
        task_lower = task_description.lower()
        
        if method == EmailAccessMethod.GMAIL_API:
            # Gmail API arguments
            if "security" in task_lower:
                query = "security account access login"
            else:
                query = task_lower.replace("search for ", "").replace("find ", "")
            
            return {
                "action": "search_emails",
                "query": query,
                "max_results": 50,
                "method": "api"
            }
            
        elif method == EmailAccessMethod.BROWSER_AUTOMATION:
            # Browser automation arguments
            if "gmail" in task_lower or "email" in task_lower:
                return {
                    "action": "open_browser",
                    "url": "https://gmail.com",
                    "method": "browser"
                }
            else:
                return {
                    "action": "open_browser",
                    "url": "https://google.com",
                    "method": "browser"
                }
                
        elif method == EmailAccessMethod.HYBRID:
            # Hybrid approach - try API first, then browser
            return {
                "action": "search_emails",
                "query": "security account access login" if "security" in task_lower else task_lower,
                "max_results": 50,
                "method": "hybrid",
                "fallback_to_browser": True
            }
        
        return {"action": "execute", "task": task_description}
    
    def execute_email_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute email task using the best available method.
        
        Args:
            task_description: Description of the email task
            
        Returns:
            Execution result
        """
        # Select the best method
        method = self.select_access_method(task_description)
        
        if not method:
            return {
                "success": False,
                "error": "No email access methods available"
            }
        
        # Get tool and arguments
        tool_name = self.get_tool_for_method(method)
        tool_args = self.get_tool_arguments(method, task_description)
        
        self.logger.info(f"Executing email task with {method.value}: {tool_name}")
        
        try:
            if method == EmailAccessMethod.GMAIL_API:
                return self._execute_gmail_api_task(tool_args)
            elif method == EmailAccessMethod.BROWSER_AUTOMATION:
                return self._execute_browser_task(tool_args)
            elif method == EmailAccessMethod.HYBRID:
                return self._execute_hybrid_task(tool_args)
            else:
                return {
                    "success": False,
                    "error": f"Unknown method: {method}"
                }
                
        except Exception as e:
            self.logger.error(f"Error executing email task: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_gmail_api_task(self, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using Gmail API."""
        try:
            from tools.email.filtering import EmailFilter
            
            # Initialize Gmail service
            # This would need proper authentication setup
            email_filter = EmailFilter(service=None)  # Placeholder
            
            # Execute search
            result = email_filter.search_emails(
                query=tool_args.get("query", "security"),
                max_results=tool_args.get("max_results", 50)
            )
            
            return {
                "success": True,
                "method": "gmail_api",
                "data": result,
                "message": "Found emails using Gmail API"
            }
            
        except Exception as e:
            self.logger.error(f"Gmail API execution failed: {e}")
            return {
                "success": False,
                "error": f"Gmail API failed: {str(e)}",
                "method": "gmail_api"
            }
    
    def _execute_browser_task(self, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using browser automation with professional fallback."""
        try:
            from tools.browser import BrowserTool
            
            # First try regular browser tool
            browser = BrowserTool()
            
            # For email tasks, use the enhanced email task execution
            if "gmail" in tool_args.get("url", "") or "email" in str(tool_args):
                # Use the enhanced email task execution method
                result = browser.execute_email_task("Find security emails in Gmail")
                
                # Check if we actually found emails
                if result.get("success") and result.get("emails_found", 0) > 0:
                    return {
                        "success": True,
                        "method": "browser_automation",
                        "data": {
                            "emails": result.get("emails", []),
                            "emails_found": result.get("emails_found", 0),
                            "search_query": result.get("search_query", "security"),
                            "browser_result": result
                        },
                        "message": f"Found {result.get('emails_found', 0)} emails using browser automation"
                    }
                else:
                    # No emails found - try professional Safari tool as fallback
                    self.logger.info("Regular browser tool failed, trying Safari Professional Tool")
                    return self._execute_safari_professional_fallback()
            
            # For non-email tasks, just open browser
            elif tool_args.get("action") == "open_browser":
                url = tool_args.get("url", "https://gmail.com")
                result = browser.open_url(url)
                
                return {
                    "success": True,
                    "method": "browser_automation",
                    "data": result,
                    "message": f"Opened {url} in browser"
                }
            
            return {
                "success": False,
                "error": f"Unknown browser action: {tool_args.get('action')}",
                "method": "browser_automation"
            }
            
        except Exception as e:
            self.logger.error(f"Browser automation failed: {e}")
            # Try professional fallback even on error
            try:
                return self._execute_safari_professional_fallback()
            except Exception as fallback_error:
                self.logger.error(f"Safari professional fallback also failed: {fallback_error}")
                return {
                    "success": False,
                    "error": f"Both browser automation and professional fallback failed: {str(e)}",
                    "method": "browser_automation"
                }

    def _execute_safari_professional_fallback(self) -> Dict[str, Any]:
        """Execute using Safari Professional Tool as fallback."""
        try:
            from tools.safari_professional_tool import SafariProfessionalTool
            
            self.logger.info("Using Safari Professional Tool as fallback")
            safari_tool = SafariProfessionalTool()
            
            # Execute professional email task
            result = safari_tool.execute_email_task_professional("Find security emails in Gmail")
            
            # Close professional browser
            safari_tool.close_browser()
            
            if result.get("success") and result.get("emails_found", 0) > 0:
                return {
                    "success": True,
                    "method": "safari_professional_fallback",
                    "data": {
                        "emails": result.get("emails", []),
                        "emails_found": result.get("emails_found", 0),
                        "search_query": result.get("search_query", "security"),
                        "browser_result": result
                    },
                    "message": f"Found {result.get('emails_found', 0)} emails using Safari Professional Tool"
                }
            else:
                return {
                    "success": False,
                    "error": "Safari Professional Tool also failed to find emails",
                    "data": {
                        "emails": [],
                        "emails_found": 0,
                        "search_query": "security"
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Safari Professional Tool fallback failed: {e}")
            return {
                "success": False,
                "error": f"Safari Professional Tool failed: {str(e)}",
                "method": "safari_professional_fallback"
            }
    
    def _execute_hybrid_task(self, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using hybrid approach (API first, browser fallback)."""
        
        # Try Gmail API first
        api_result = self._execute_gmail_api_task(tool_args)
        
        if api_result["success"]:
            return api_result
        
        # Fallback to browser if API failed
        if tool_args.get("fallback_to_browser", False):
            self.logger.info("Gmail API failed, falling back to browser automation")
            return self._execute_browser_task(tool_args)
        
        return api_result

# Global email strategy manager instance
email_strategy_manager = EmailStrategyManager() 