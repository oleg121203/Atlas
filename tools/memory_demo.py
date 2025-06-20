#!/usr/bin/env python3
"""
Demonstration script for the enhanced memory organization in Atlas
"""

import logging
import time
from typing import Dict, Any

from utils.config_manager import ConfigManager
from agents.llm_manager import LLMManager
from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryScope, MemoryType


def demo_enhanced_memory():
    """Demonstrate the enhanced memory features"""
    print("🧠 Atlas Enhanced Memory Manager Demo")
    print("=" * 40)
    
    #Initialize managers
    config_manager = ConfigManager()
    llm_manager = LLMManager(config_manager)
    memory_manager = EnhancedMemoryManager(llm_manager, config_manager)
    
    print("✅ Managers initialized")
    
    #Demo 1: Agent-specific memory storage
    print("\n📝 Demo 1: Agent-specific Memory Storage")
    print("-" * 40)
    
    #Master Agent storing plans
    memory_manager.add_memory_for_agent(
        agent_type=MemoryScope.MASTER_AGENT,
        memory_type=MemoryType.PLAN,
        content="Execute task: Take a screenshot and analyze the desktop",
        metadata={"goal": "desktop_analysis", "priority": "high"}
    )
    print("✅ Master Agent plan stored")
    
    #Screen Agent storing observations
    memory_manager.add_memory_for_agent(
        agent_type=MemoryScope.SCREEN_AGENT,
        memory_type=MemoryType.OBSERVATION,
        content="Screen captured: 1920x1080 pixels, desktop visible with multiple windows",
        metadata={"resolution": "1920x1080", "window_count": 5}
    )
    print("✅ Screen Agent observation stored")
    
    #Security Agent storing events
    memory_manager.add_memory_for_agent(
        agent_type=MemoryScope.SECURITY_AGENT,
        memory_type=MemoryType.OBSERVATION,
        content="Action approved: screenshot capture within safe parameters",
        metadata={"action": "ALLOW", "rule_triggered": None}
    )
    print("✅ Security Agent event stored")
    
    #User feedback
    memory_manager.add_memory_for_agent(
        agent_type=MemoryScope.USER_DATA,
        memory_type=MemoryType.FEEDBACK,
        content="Task completed successfully, desktop analysis was accurate",
        metadata={"rating": "good", "completion_time": "30s"}
    )
    print("✅ User feedback stored")
    
    #Demo 2: Agent-specific memory search
    print("\n🔍 Demo 2: Agent-specific Memory Search")
    print("-" * 40)
    
    #Search Master Agent plans
    plans = memory_manager.search_memories_for_agent(
        agent_type=MemoryScope.MASTER_AGENT,
        query="screenshot",
        memory_type=MemoryType.PLAN,
        n_results=5
    )
    print(f"📋 Found {len(plans)} Master Agent plans about screenshots")
    
    #Search Screen Agent observations
    observations = memory_manager.search_memories_for_agent(
        agent_type=MemoryScope.SCREEN_AGENT,
        query="desktop",
        memory_type=MemoryType.OBSERVATION,
        n_results=5
    )
    print(f"👁️  Found {len(observations)} Screen Agent observations about desktop")
    
    #Search user feedback
    feedback = memory_manager.search_memories_for_agent(
        agent_type=MemoryScope.USER_DATA,
        query="task",
        memory_type=MemoryType.FEEDBACK,
        n_results=5
    )
    print(f"💬 Found {len(feedback)} user feedback about tasks")
    
    #Demo 3: Memory statistics
    print("\n📊 Demo 3: Memory Statistics")
    print("-" * 40)
    
    stats = memory_manager.get_memory_stats()
    print(f"Total collections: {stats.get('total_collections', 0)}")
    print(f"Total memories: {stats.get('total_memories', 0)}")
    
    print("\nMemories by scope:")
    for scope, count in stats.get('memory_by_scope', {}).items():
        print(f"  {scope}: {count}")
    
    print("\nMemories by type:")
    for mem_type, count in stats.get('memory_by_type', {}).items():
        print(f"  {mem_type}: {count}")
    
    #Demo 4: TTL and cleanup demonstration
    print("\n🧹 Demo 4: TTL and Cleanup")
    print("-" * 40)
    
    #Add temporary memory with short TTL
    memory_manager.add_memory(
        content="Temporary action: mouse click at (100, 200)",
        collection_name="current_session",
        metadata={"action": "click", "coordinates": "(100, 200)"}
    )
    print("✅ Temporary memory added")
    
    #Check cleanup
    cleaned = memory_manager.cleanup_all_expired()
    print(f"🗑️  Cleaned up {cleaned} expired memories")
    
    #Demo 5: Cross-agent search
    print("\n🔄 Demo 5: Cross-agent Search")
    print("-" * 40)
    
    all_results = memory_manager.search_memories("screenshot", n_results=10)
    print(f"🔍 Cross-agent search found {len(all_results)} memories about screenshots")
    
    for result in all_results[:3]:  #Show first 3
        collection = result.get('collection', 'unknown')
        relevance = result.get('relevance', 0)
        print(f"  📄 {collection}: {relevance:.2f} relevance")
    
    print("\n🎉 Demo completed!")
    print("\nKey benefits demonstrated:")
    print("  ✅ Organized memory by agent type and memory type")
    print("  ✅ Agent-specific search and isolation") 
    print("  ✅ Comprehensive statistics and monitoring")
    print("  ✅ Automatic cleanup with TTL")
    print("  ✅ Cross-agent search when needed")
    print("  ✅ Rich metadata for better context")


def compare_old_vs_new():
    """Compare old vs new memory approach"""
    print("\n📈 Old vs New Memory Approach")
    print("=" * 40)
    
    print("❌ Old Approach Issues:")
    print("  • Mixed contexts in same collections")
    print("  • No automatic cleanup")
    print("  • No agent isolation")
    print("  • Limited organization")
    print("  • Manual memory management")
    
    print("\n✅ New Approach Benefits:")
    print("  • Structured collections by agent/type")
    print("  • Automatic TTL cleanup")
    print("  • Agent-specific memory isolation")
    print("  • Hierarchical organization")
    print("  • Rich metadata system")
    print("  • Comprehensive monitoring")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        demo_enhanced_memory()
        compare_old_vs_new()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Note: This demo requires ChromaDB and LLM providers to be configured")
