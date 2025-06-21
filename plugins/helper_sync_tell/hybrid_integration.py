"""
Integration script to upgrade Helper Sync Tell to Advanced AI Thinking Plugin

This script provides seamless integration of the new advanced thinking capabilities
while maintaining backward compatibility with existing Atlas systems.
"""

import logging
import sys
from pathlib import Path

#Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    #Import the advanced thinking tool
    from advanced_thinking import (
        AdvancedAIThinkingTool, 
        ThinkingStrategy, 
        AnalysisContext,
        register as register_advanced
    )
    ADVANCED_AVAILABLE = True
except ImportError as e:
    ADVANCED_AVAILABLE = False
    logging.warning(f"Advanced thinking not available: {e}")
    #Fallback to original plugin
    try:
        from plugin import EnhancedHelperSyncTellTool, register as register_original
    except ImportError:
        logging.error("Neither advanced nor original plugin available")
        raise


class HybridThinkingTool:
    """
    Hybrid tool that provides advanced thinking when available,
    with graceful fallback to enhanced thinking.
    """
    
    def __init__(self, llm_manager=None, memory_manager=None, config_manager=None):
        """Initialize hybrid thinking tool."""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if ADVANCED_AVAILABLE:
            self.core_tool = AdvancedAIThinkingTool(llm_manager, memory_manager, config_manager)
            self.mode = "advanced"
            self.logger.info("Initialized in Advanced AI Thinking mode")
        else:
            self.core_tool = EnhancedHelperSyncTellTool(llm_manager, memory_manager, config_manager)
            self.mode = "enhanced"
            self.logger.info("Initialized in Enhanced Thinking mode (fallback)")
        
        #Expose core attributes
        self.name = getattr(self.core_tool, 'name', 'hybrid_thinking')
        self.description = getattr(self.core_tool, 'description', 'Hybrid thinking tool with advanced capabilities')
        self.version = "3.0.0-hybrid"
        self.capabilities = getattr(self.core_tool, 'capabilities', {})
        self.platform_info = getattr(self.core_tool, 'platform_info', {})
    
    def __call__(self, query: str, available_tools=None):
        """Process query using the best available thinking mode."""
        try:
            return self.core_tool(query, available_tools)
        except Exception as e:
            self.logger.error(f"Error in {self.mode} thinking: {e}")
            #If advanced fails, try to fallback
            if self.mode == "advanced" and hasattr(self, '_fallback_thinking'):
                return self._fallback_thinking(query, available_tools)
            raise
    
    def process_help_request(self, message: str, available_tools=None):
        """Process help request."""
        return self.core_tool.process_help_request(message, available_tools)
    
    def integrate_with_atlas_help_mode(self, main_app):
        """Integrate with Atlas help mode."""
        return self.core_tool.integrate_with_atlas_help_mode(main_app)
    
    def get_thinking_strategies(self):
        """Get available thinking strategies."""
        if self.mode == "advanced" and hasattr(self.core_tool, 'strategy_patterns'):
            return list(self.core_tool.strategy_patterns.keys())
        return ["analytical", "exploratory", "creative"]
    
    def get_performance_stats(self):
        """Get performance statistics."""
        if hasattr(self.core_tool, 'meta_stats'):
            return self.core_tool.meta_stats
        elif hasattr(self.core_tool, 'performance_stats'):
            return self.core_tool.performance_stats
        return {"mode": self.mode, "available": True}


def register(llm_manager=None, atlas_app=None, **kwargs):
    """
    Smart registration that uses the best available thinking tool.
    """
    try:
        if ADVANCED_AVAILABLE:
            #Use advanced thinking
            result = register_advanced(llm_manager, atlas_app, **kwargs)
            if result and result.get('tools'):
                #Wrap in hybrid tool for consistency
                advanced_tool = result['tools'][0]
                hybrid_tool = HybridThinkingTool(llm_manager, 
                    kwargs.get('memory_manager') or getattr(advanced_tool, 'memory_manager', None),
                    kwargs.get('config_manager') or getattr(advanced_tool, 'config_manager', None)
                )
                hybrid_tool.core_tool = advanced_tool
                hybrid_tool.mode = "advanced"
                
                result['tools'] = [hybrid_tool]
                result['metadata']['mode'] = "advanced"
                result['metadata']['version'] = "3.0.0-hybrid"
                
                logging.info("Registered Advanced AI Thinking Tool (hybrid mode)")
                return result
        
        #Fallback to enhanced thinking
        if 'register_original' in globals():
            result = register_original(llm_manager, atlas_app, **kwargs)
            if result and result.get('tools'):
                enhanced_tool = result['tools'][0]
                hybrid_tool = HybridThinkingTool(llm_manager,
                    kwargs.get('memory_manager') or getattr(enhanced_tool, 'memory_manager', None),
                    kwargs.get('config_manager') or getattr(enhanced_tool, 'config_manager', None)
                )
                hybrid_tool.core_tool = enhanced_tool
                hybrid_tool.mode = "enhanced"
                
                result['tools'] = [hybrid_tool]
                result['metadata']['mode'] = "enhanced"
                result['metadata']['version'] = "3.0.0-hybrid"
                
                logging.info("Registered Enhanced Thinking Tool (hybrid fallback mode)")
                return result
        
        #Last resort - create minimal tool
        minimal_tool = HybridThinkingTool(llm_manager)
        return {
            "tools": [minimal_tool],
            "agents": [],
            "metadata": {
                "version": "3.0.0-hybrid",
                "mode": "minimal",
                "capabilities": minimal_tool.capabilities,
                "integration_status": False
            }
        }
        
    except Exception as e:
        logging.error(f"Failed to register hybrid thinking plugin: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return {
            "tools": [],
            "agents": [],
            "metadata": {"error": str(e), "mode": "failed"}
        }


#Test function
def test_hybrid_tool():
    """Test the hybrid tool functionality."""
    print("🧠 Testing Hybrid Thinking Tool")
    print("=" * 50)
    
    try:
        #Test registration
        result = register()
        
        if result.get('tools'):
            tool = result['tools'][0]
            print(f"✅ Registration successful - Mode: {getattr(tool, 'mode', 'unknown')}")
            print(f"   Tool name: {tool.name}")
            print(f"   Version: {tool.version}")
            print(f"   Capabilities: {len(tool.capabilities)} items")
            
            if hasattr(tool, 'get_thinking_strategies'):
                strategies = tool.get_thinking_strategies()
                print(f"   Available strategies: {strategies}")
            
            #Test basic functionality
            test_query = "Як можна покращити систему пам'яті в Атлас?"
            response = tool(test_query)
            print("✅ Query processing successful")
            print(f"   Response length: {len(response)} characters")
            print(f"   Response preview: {response[:100]}...")
            
        else:
            print("❌ No tools registered")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Test completed")


if __name__ == "__main__":
    test_hybrid_tool()
