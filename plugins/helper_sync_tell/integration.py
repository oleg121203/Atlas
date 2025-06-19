"""
Helper Sync Tell - Integration Module

This module integrates the Helper Sync Tell plugin with Atlas's helper mode.
It provides utility functions to connect the structured thinking process
with Atlas's main application flow.
"""

import logging
from typing import Dict, Any, Callable, Optional

# Import the tool
try:
    from .plugin import HelperSyncTellTool
except ImportError:
    # Fall back to direct import
    from plugin import HelperSyncTellTool

class HelperModeIntegration:
    """
    Integrates the Helper Sync Tell tool with Atlas's helper mode.
    This class provides utility methods to connect the structured thinking
    process with the main application's helper mode.
    """
    
    def __init__(self, helper_tool: HelperSyncTellTool):
        """
        Initialize the integration module.
        
        Args:
            helper_tool: The Helper Sync Tell tool instance
        """
        self.helper_tool = helper_tool
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Helper Sync Tell integration initialized")
    
    def process_help_request(self, message: str, available_tools: Dict[str, Callable]) -> str:
        """
        Process a help request using the structured thinking approach.
        
        Args:
            message: The user's help request message
            available_tools: Dictionary of tools available for analysis
            
        Returns:
            The structured response to the help request
        """
        self.logger.info(f"Processing help request with structured thinking: {message[:50]}...")
        
        # Process the request using the helper tool
        response = self.helper_tool(message, available_tools)
        
        return response
    
    def patch_main_application(self, main_app) -> bool:
        """
        Patch the main application to use the structured thinking process.
        This method should be called during plugin initialization.
        
        Args:
            main_app: The main application instance (typically from main.py)
            
        Returns:
            True if patching was successful, False otherwise
        """
        try:
            # Store the original help mode handler
            original_handler = main_app._handle_help_mode
            
            # Define a new handler that uses our tool
            def enhanced_help_mode_handler(self, message: str, context) -> str:
                """Enhanced help mode handler using structured thinking."""
                # Check if the message is a specific command that should use the original handler
                if any(cmd in message.lower() for cmd in ['read file', 'list directory', 'tree', 'search for', 'info about']):
                    # Use the original handler for specific commands
                    return original_handler(message, context)
                
                # For normal help requests, use our structured thinking process
                available_tools = {
                    "code_reader": lambda q: self.code_reader.search_in_files(q) if hasattr(self, 'code_reader') else None,
                    "memory_query": lambda q: "Memory not implemented yet" # Replace with actual memory query when available
                }
                
                return self.helper_sync_tell_integration.process_help_request(message, available_tools)
            
            # Create the integration instance and attach it to the main app
            main_app.helper_sync_tell_integration = self
            
            # Replace the original handler with our enhanced version
            # Note: This uses a non-standard but common technique to replace a method
            import types
            main_app._handle_help_mode = types.MethodType(enhanced_help_mode_handler, main_app)
            
            self.logger.info("Successfully patched main application to use structured thinking")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to patch main application: {e}", exc_info=True)
            return False


def get_integration(helper_tool: HelperSyncTellTool) -> HelperModeIntegration:
    """
    Get an integration instance for the given helper tool.
    
    Args:
        helper_tool: The Helper Sync Tell tool instance
        
    Returns:
        A helper mode integration instance
    """
    return HelperModeIntegration(helper_tool)
