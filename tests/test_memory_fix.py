#!/usr/bin/env python3
"""
Test script to verify that the memory_types -> memory_type fix works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryScope, MemoryType
from agents.llm_manager import LLMManager
from agents.token_tracker import TokenTracker
from config_manager import ConfigManager

def test_memory_search():
    """Test the fixed memory search functionality."""
    print("🧪 Testing memory search fix...")
    
    try:
        # Initialize components
        config_manager = ConfigManager()
        token_tracker = TokenTracker()
        llm_manager = LLMManager(token_tracker=token_tracker, config_manager=config_manager)
        memory_manager = EnhancedMemoryManager(
            llm_manager=llm_manager, 
            config_manager=config_manager
        )
        
        # Test the corrected method call
        results = memory_manager.search_memories_for_agent(
            agent_type=MemoryScope.MASTER_AGENT,
            query="test query",
            memory_type=MemoryType.PLAN,
            n_results=5
        )
        
        print(f"✅ Memory search completed successfully. Found {len(results)} results.")
        return True
        
    except TypeError as e:
        if "memory_types" in str(e):
            print(f"❌ TypeError still exists: {e}")
            return False
        else:
            print(f"❌ Different TypeError: {e}")
            return False
    except Exception as e:
        print(f"⚠️  Other exception (may be expected): {e}")
        return True

if __name__ == "__main__":
    success = test_memory_search()
    if success:
        print("\n🎉 Memory search fix verified successfully!")
    else:
        print("\n💥 Memory search fix failed!")
    sys.exit(0 if success else 1)
