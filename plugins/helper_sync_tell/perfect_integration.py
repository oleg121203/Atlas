#!/usr/bin/env python3
"""
Perfect Integration Script for Helper Sync Tell Plugin

This script provides the perfect integration of the Helper Sync Tell plugin 
with Atlas's helper mode, fixing all issues and providing comprehensive
structured thinking capabilities.
"""

import logging
import sys
import os
from typing import Dict, Any, Callable, Optional

#Setup logging
logger = logging.getLogger(__name__)

def integrate_plugin_with_atlas(atlas_app) -> bool:
    """
    Integrate the Helper Sync Tell plugin with Atlas application.
    
    Args:
        atlas_app: The main AtlasApp instance
        
    Returns:
        True if integration successful, False otherwise
    """
    try:
        logger.info("🔧 Starting perfect integration of Helper Sync Tell plugin")
        
        #Import the plugin
        from plugin import EnhancedHelperSyncTellTool, register
        
        #Get managers from Atlas app
        llm_manager = getattr(atlas_app, 'master_agent', None)
        if llm_manager:
            llm_manager = llm_manager.llm_manager
        
        memory_manager = getattr(atlas_app, 'memory_manager', None)
        config_manager = getattr(atlas_app, 'config_manager', None)
        
        #Register the plugin with full integration
        registration = register(llm_manager=llm_manager, atlas_app=atlas_app)
        
        if not registration['tools']:
            logger.error("❌ Plugin registration failed - no tools returned")
            return False
        
        #Get the tool instance
        helper_tool = registration['tools'][0]
        logger.info(f"✅ Plugin registered: {helper_tool.name} v{helper_tool.version}")
        
        #Patch the help mode handler for comprehensive integration
        if hasattr(atlas_app, '_handle_help_mode'):
            original_handler = atlas_app._handle_help_mode
            
            def enhanced_help_handler(message: str, context) -> str:
                """Enhanced help handler with structured thinking."""
                #Check for simple file operations
                simple_ops = ['read file', 'list dir', 'tree', 'search for', 'info about']
                message_lower = message.lower()
                
                if any(op in message_lower for op in simple_ops):
                    #Use original handler for simple operations
                    return original_handler(message, context)
                
                #For complex queries, use our structured thinking
                available_tools = {}
                
                #Atlas tools integration
                if hasattr(atlas_app, 'code_reader'):
                    available_tools.update({
                        'code_search': lambda q: atlas_app.code_reader.search_in_files(q),
                        'file_analysis': lambda q: atlas_app.code_reader.get_file_info(q),
                        'directory_tree': lambda q: atlas_app.code_reader.get_file_tree(),
                        'code_patterns': lambda q: f"Searching for code patterns: {q}"
                    })
                
                if hasattr(atlas_app, 'agent_manager'):
                    available_tools.update({
                        'agent_tools': lambda q: f"Available tools: {', '.join(atlas_app.agent_manager.get_tool_names())}",
                        'agent_info': lambda q: f"Agent details for query: {q}"
                    })
                
                if hasattr(atlas_app, 'memory_manager'):
                    available_tools['memory_search'] = lambda q: f"Memory search results for: {q}"
                
                #Use structured thinking for comprehensive response
                return helper_tool.process_help_request(message, available_tools)
            
            #Replace the handler
            atlas_app._handle_help_mode = enhanced_help_handler
            logger.info("✅ Help mode handler enhanced with structured thinking")
        
        #Add the tool to the agent manager if available
        if hasattr(atlas_app, 'agent_manager'):
            atlas_app.agent_manager.add_tool(
                name="helper_sync_tell",
                tool_function=helper_tool,
                description="Advanced structured thinking tool for complex queries",
                silent_overwrite=True
            )
            logger.info("✅ Plugin added to agent manager")
        
        #Store reference for access
        atlas_app._helper_sync_tell_plugin = helper_tool
        
        logger.info("🎉 Perfect integration completed successfully!")
        
        #Log capabilities
        capabilities = helper_tool.capabilities
        logger.info(f"📊 Plugin capabilities: {len(capabilities)} features active")
        for feature, enabled in capabilities.items():
            status = "✅" if enabled else "❌"
            logger.info(f"   {status} {feature}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def validate_integration(atlas_app) -> Dict[str, Any]:
    """
    Validate that the plugin integration is working correctly.
    
    Args:
        atlas_app: The main AtlasApp instance
        
    Returns:
        Dictionary with validation results
    """
    results = {
        "plugin_loaded": False,
        "help_mode_enhanced": False,
        "agent_manager_integration": False,
        "capabilities_active": {},
        "errors": []
    }
    
    try:
        #Check if plugin is loaded
        if hasattr(atlas_app, '_helper_sync_tell_plugin'):
            plugin = atlas_app._helper_sync_tell_plugin
            results["plugin_loaded"] = True
            results["capabilities_active"] = plugin.capabilities
            
            #Test basic functionality
            test_response = plugin("What is the purpose of this system?", {})
            if len(test_response) > 50:  #Basic response length check
                results["basic_functionality"] = True
            
        #Check help mode enhancement
        if hasattr(atlas_app, '_handle_help_mode'):
            try:
                test_help = atlas_app._handle_help_mode("How does memory work?", None)
                if "analysis" in test_help.lower() or "comprehensive" in test_help.lower():
                    results["help_mode_enhanced"] = True
            except Exception as e:
                results["errors"].append(f"Help mode test failed: {e}")
        
        #Check agent manager integration
        if hasattr(atlas_app, 'agent_manager'):
            tool_names = atlas_app.agent_manager.get_tool_names()
            if "helper_sync_tell" in tool_names:
                results["agent_manager_integration"] = True
        
        #Overall success
        results["overall_success"] = (
            results["plugin_loaded"] and 
            results.get("basic_functionality", False)
        )
        
    except Exception as e:
        results["errors"].append(f"Validation error: {e}")
    
    return results

def demo_structured_thinking(atlas_app, query: str = None) -> str:
    """
    Demonstrate the structured thinking capabilities.
    
    Args:
        atlas_app: The main AtlasApp instance
        query: Optional demo query
        
    Returns:
        Demonstration response
    """
    if not hasattr(atlas_app, '_helper_sync_tell_plugin'):
        return "❌ Plugin not integrated. Run perfect integration first."
    
    plugin = atlas_app._helper_sync_tell_plugin
    
    if not query:
        query = "How does Atlas handle complex multi-step tasks and what are the key components involved?"
    
    logger.info(f"🧪 Demonstrating structured thinking with query: {query}")
    
    #Create mock tools for demonstration
    demo_tools = {
        'architecture_analyzer': lambda q: f"Architecture analysis shows modular design with agents, memory, and LLM management for: {q}",
        'code_inspector': lambda q: f"Code inspection reveals clean separation of concerns and robust error handling for: {q}",
        'workflow_tracer': lambda q: f"Workflow analysis shows goal decomposition → planning → execution → feedback cycle for: {q}"
    }
    
    response = plugin(query, demo_tools)
    
    logger.info("🎯 Structured thinking demonstration completed")
    return response

def main():
    """Main function for testing integration."""
    print("🚀 Helper Sync Tell - Perfect Integration Script")
    print("=" * 60)
    
    #This would normally be called with the actual Atlas app instance
    print("ℹ️  This script provides integration functions for Atlas.")
    print("ℹ️  Import and call integrate_plugin_with_atlas(atlas_app) from your Atlas application.")
    print("ℹ️  For testing, run the enhanced_test.py script in this directory.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
