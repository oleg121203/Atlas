"""
Helper Sync Tell - Post-load Integration

This script integrates the Helper Sync Tell plugin with Atlas's helper mode
after all plugins have been loaded. This approach avoids import issues during
the plugin loading phase.
"""

import logging
import sys
from typing import Optional

logger = logging.getLogger("HelperSyncTellIntegration")

def integrate_helper_sync_tell(app) -> bool:
    """
    Integrate Helper Sync Tell with the main Atlas application.
    This should be called after all plugins are loaded.
    
    Args:
        app: The main Atlas application instance
        
    Returns:
        True if integration was successful, False otherwise
    """
    try:
        #Check if the plugin was loaded
        if not hasattr(app, 'plugin_manager'):
            logger.warning("Plugin manager not found in application")
            return False
        
        plugins = app.plugin_manager.get_all_plugins()
        if 'helper_sync_tell' not in plugins:
            logger.warning("Helper Sync Tell plugin not found")
            return False
        
        #Get the plugin
        plugin_info = plugins['helper_sync_tell']
        if not plugin_info.get('tools'):
            logger.warning("Helper Sync Tell plugin has no tools")
            return False
        
        #Get the helper sync tell tool
        helper_tool = plugin_info['tools'][0]
        
        #Check if the original help mode handler exists
        if not hasattr(app, '_handle_help_mode'):
            logger.warning("Help mode handler not found in application")
            return False
        
        #Store the original handler
        original_handler = app._handle_help_mode
        
        #Create the enhanced handler
        def enhanced_help_mode_handler(message: str, context) -> str:
            """Enhanced help mode handler using structured thinking."""
            #Check if the message is a specific command that should use the original handler
            specific_commands = [
                'read file', 'show file', 'list directory', 'list folder', 'list dir',
                'tree', 'structure', 'search for', 'search in', 'info about', 'info file'
            ]
            
            message_lower = message.lower()
            is_specific_command = any(cmd in message_lower for cmd in specific_commands)
            
            if is_specific_command:
                #Use the original handler for specific commands
                return original_handler(message, context)
            
            #For complex help requests, use structured thinking
            try:
                #Create available tools dictionary
                available_tools = {}
                
                #Add code reader if available
                if hasattr(app, 'code_reader'):
                    available_tools['code_search'] = lambda q: app.code_reader.search_in_files(q)
                    available_tools['file_info'] = lambda q: app.code_reader.get_file_info(q)
                
                #Add memory query if available
                if hasattr(app, 'memory_manager'):
                    available_tools['memory_query'] = lambda q: "Memory query functionality not implemented yet"
                
                #Use the helper tool for structured thinking
                response = helper_tool(message, available_tools)
                return response
                
            except Exception as e:
                logger.error(f"Error in enhanced help mode: {e}")
                #Fall back to original handler
                return original_handler(message, context)
        
        #Replace the help mode handler
        import types
        app._handle_help_mode = types.MethodType(enhanced_help_mode_handler, app)
        
        #Mark the integration as complete
        app._helper_sync_tell_integrated = True
        
        logger.info("Successfully integrated Helper Sync Tell with Atlas helper mode")
        return True
        
    except Exception as e:
        logger.error(f"Failed to integrate Helper Sync Tell: {e}", exc_info=True)
        return False

def check_integration_status(app) -> bool:
    """
    Check if Helper Sync Tell is properly integrated.
    
    Args:
        app: The main Atlas application instance
        
    Returns:
        True if integration is active, False otherwise
    """
    return getattr(app, '_helper_sync_tell_integrated', False)

#Auto-execute if the main app is available
def auto_integrate():
    """Automatically integrate if the main app is found."""
    try:
        main_module = sys.modules.get('__main__')
        if main_module and hasattr(main_module, 'app'):
            app = main_module.app
            if not check_integration_status(app):
                integrate_helper_sync_tell(app)
    except Exception as e:
        logger.debug(f"Auto-integration not possible: {e}")

#Call auto-integrate when this module is imported
if __name__ != "__main__":
    auto_integrate()
