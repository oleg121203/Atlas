"""
Helper Sync Tell Startup Integration

This script is executed when Atlas starts to ensure the Helper Sync Tell
plugin is properly loaded and integrated with the helper mode.
"""

import logging
import sys
from pathlib import Path

#Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("HelperSyncTellStartup")

def integrate_with_atlas():
    """
    Integrate the Helper Sync Tell plugin with Atlas's helper mode.
    This function is called when Atlas starts.
    """
    logger.info("Initializing Helper Sync Tell integration...")
    
    try:
        #Try to find the main Atlas application
        main_module = sys.modules.get('__main__')
        if not main_module or not hasattr(main_module, 'app'):
            logger.warning("Main Atlas application not found. Integration deferred to plugin registration.")
            return False
        
        #Get the main application instance
        app = main_module.app
        
        #Check if the plugin is already loaded
        if hasattr(app, 'helper_sync_tell_integration'):
            logger.info("Helper Sync Tell is already integrated with Atlas.")
            return True
        
        #Try to import the plugin
        plugin_path = Path(__file__).parent
        sys.path.insert(0, str(plugin_path))
        
        try:
            import plugin as plugin_module
            import integration as integration_module
        except ImportError as e:
            logger.error(f"Failed to import plugin modules: {e}")
            return False
        
        #Check for required components
        if not hasattr(app, 'llm_manager'):
            logger.warning("LLM Manager not found in main application. Limited functionality.")
            llm_manager = None
        else:
            llm_manager = app.llm_manager
        
        if not hasattr(app, 'memory_manager') and hasattr(app, 'agent_manager') and hasattr(app.agent_manager, 'memory_manager'):
            memory_manager = app.agent_manager.memory_manager
        else:
            logger.warning("Memory Manager not found. Limited functionality.")
            memory_manager = None
        
        #Create the helper tool
        helper_tool = plugin_module.HelperSyncTellTool(
            llm_manager=llm_manager,
            memory_manager=memory_manager
        )
        
        #Create integration and attach to app
        integration = integration_module.get_integration(helper_tool)
        integration.patch_main_application(app)
        
        logger.info("Successfully integrated Helper Sync Tell with Atlas!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to integrate Helper Sync Tell: {e}", exc_info=True)
        return False

#Auto-execute when imported
if __name__ != "__main__":
    integrate_with_atlas()
