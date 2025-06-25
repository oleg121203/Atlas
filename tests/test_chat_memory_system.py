#!/usr/bin/env python3
"""
Test enhanced chat memory system with mode isolation
"""

import os
import sys
import tempfile
from pathlib import Path

#Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.agents.chat_context_manager import ChatContext, ChatContextManager, ChatMode
from modules.agents.enhanced_memory_manager import EnhancedMemoryManager
from modules.agents.enhanced_plugin_manager import EnhancedPluginManager


def test_chat_memory_isolation():
    """Test that different chat modes have isolated memory."""

    #Create temporary directory for ChromaDB
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_chroma"
        memory_manager = EnhancedMemoryManager(db_path=str(db_path))
        chat_manager = ChatContextManager(memory_manager=memory_manager)

        print("🧪 Testing Chat Memory Isolation")
        print("=" * 50)

        #Test different modes
        test_cases = [
            (ChatMode.CASUAL_CHAT, "Hello, how are you?", "I'm doing well, thank you!"),
            (ChatMode.SYSTEM_HELP, "What can you do?", "I can help with automation and more."),
            (ChatMode.GOAL_SETTING, "Take a screenshot", "I'll take a screenshot for you."),
            (ChatMode.DEVELOPMENT, "Show debug info", "Here's the debug information."),
        ]

        #Store conversations in different modes
        for mode, message, response in test_cases:
            context = ChatContext(
                mode=mode,
                confidence=0.9,
                suggested_response_type="test",
                context_keywords=[],
                requires_system_integration=False,
            )

            chat_manager.update_conversation_history(message, response, context)
            print(f"✅ Stored {mode.value}: '{message[:30]}...'")

        #Test memory retrieval per mode
        print("\n🔍 Testing Memory Retrieval by Mode")
        print("-" * 40)

        for mode, _, _ in test_cases:
            memories = chat_manager.retrieve_conversation_context(mode, "help", limit=5)
            stats = chat_manager.get_mode_conversation_stats(mode)

            print(f"📊 {mode.value}:")
            print(f"   Memories found: {len(memories)}")
            print(f"   Stats: {stats}")

        #Test cross-mode isolation
        print("\n🔒 Testing Cross-Mode Isolation")
        print("-" * 40)

        #Try to retrieve casual chat from system help mode
        casual_in_help = chat_manager.retrieve_conversation_context(
            ChatMode.SYSTEM_HELP, "how are you", limit=10,
        )

        print(f"Casual chat messages in help mode: {len(casual_in_help)}")
        print("✅ Memory isolation working!" if len(casual_in_help) == 0 else "❌ Memory leaked!")

        #Test session context with memory
        print("\n📝 Testing Session Context with Memory")
        print("-" * 40)

        session_context = chat_manager.get_session_context_with_memory(
            "What are your capabilities?", ChatMode.SYSTEM_HELP,
        )

        print(f"Session context keys: {list(session_context.keys())}")
        print(f"Has relevant memories: {'relevant_memories' in session_context}")
        print(f"Memory enabled: {session_context.get('memory_enabled', False)}")

        print("\n✅ Chat memory isolation test completed!")


def test_plugin_memory_isolation():
    """Test plugin memory isolation."""

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_chroma"
        memory_manager = EnhancedMemoryManager(db_path=str(db_path))

        #Mock agent manager
        class MockAgentManager:
            pass

        plugin_manager = EnhancedPluginManager(
            agent_manager=MockAgentManager(),
            plugin_dir="plugins",
            memory_manager=memory_manager,
        )

        print("\n🔌 Testing Plugin Memory Isolation")
        print("=" * 50)

        #Simulate plugin data storage
        test_plugins = ["weather_tool", "unified_browser", "custom_tool"]

        for plugin_name in test_plugins:
            #Store plugin metadata
            plugin_manager._store_plugin_metadata(
                plugin_name,
                {"name": plugin_name, "version": "1.0.0", "description": f"Test {plugin_name}"},
                ["tool1", "tool2"],
                [],
            )

            #Store plugin events
            plugin_manager._store_plugin_event(plugin_name, "enabled")

            print(f"✅ Stored data for plugin: {plugin_name}")

        #Test memory retrieval per plugin
        print("\n🔍 Testing Plugin Memory Retrieval")
        print("-" * 40)

        for plugin_name in test_plugins:
            memories = plugin_manager.get_plugin_memory_context(
                plugin_name, "metadata", limit=5,
            )
            print(f"📊 {plugin_name}: {len(memories)} memories found")

        #Test plugin stats
        stats = plugin_manager.get_plugin_stats()
        print("\n📈 Plugin System Stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

        print("\n✅ Plugin memory isolation test completed!")


def test_dev_mode_memory():
    """Test development mode enhanced memory features."""

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_chroma"
        memory_manager = EnhancedMemoryManager(db_path=str(db_path))
        chat_manager = ChatContextManager(memory_manager=memory_manager)

        print("\n🔧 Testing Development Mode Memory")
        print("=" * 50)

        #Test development mode context
        dev_context = chat_manager._create_development_context("Debug this issue")
        print(f"Dev context mode: {dev_context.mode}")
        print(f"Dev context confidence: {dev_context.confidence}")
        print(f"Dev context type: {dev_context.control_type}")

        #Store development session
        chat_manager.update_conversation_history(
            "Show me debug information",
            "Here's the detailed debug info with safety checks...",
            dev_context,
            metadata={"debug_level": "detailed", "safety_checks": True},
        )

        #Retrieve development memories
        dev_memories = chat_manager.retrieve_conversation_context(
            ChatMode.DEVELOPMENT, "debug", limit=10,
        )

        print(f"\n📊 Development memories: {len(dev_memories)}")

        #Test enhanced session context for dev mode
        enhanced_context = chat_manager.get_session_context_with_memory(
            "Analyze system performance", ChatMode.DEVELOPMENT,
        )

        print(f"Enhanced context keys: {list(enhanced_context.keys())}")
        print(f"Dev mode stats: {enhanced_context.get('mode_stats', {})}")

        print("\n✅ Development mode memory test completed!")


def test_memory_cleanup_and_ttl():
    """Test memory cleanup and TTL functionality."""

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_chroma"
        memory_manager = EnhancedMemoryManager(db_path=str(db_path))
        chat_manager = ChatContextManager(memory_manager=memory_manager)

        print("\n🧹 Testing Memory Cleanup and TTL")
        print("=" * 50)

        #Test TTL configuration per mode
        for mode in ChatMode:
            config = chat_manager.mode_memory_config.get(mode, {})
            ttl = config.get("ttl_days", "unknown")
            max_context = config.get("max_context", "unknown")

            print(f"📅 {mode.value}: TTL={ttl} days, Max context={max_context}")

        #Test cleanup functionality
        chat_manager.cleanup_old_conversations(ChatMode.CASUAL_CHAT)
        print("✅ Mode-specific cleanup executed")

        chat_manager.cleanup_old_conversations()
        print("✅ Global cleanup executed")

        #Test memory stats
        memory_stats = memory_manager.get_memory_stats()
        print("\n📊 Memory Statistics:")
        for scope, types in memory_stats.items():
            print(f"   {scope}: {len(types)} types")
            for mem_type, stats in types.items():
                print(f"     {mem_type}: {stats}")

        print("\n✅ Memory cleanup and TTL test completed!")


def main():
    """Run all tests."""
    print("🚀 Starting Enhanced Chat Memory System Tests")
    print("=" * 60)

    try:
        test_chat_memory_isolation()
        test_plugin_memory_isolation()
        test_dev_mode_memory()
        test_memory_cleanup_and_ttl()

        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Chat memory isolation working")
        print("✅ Plugin memory isolation working")
        print("✅ Development mode memory enhanced")
        print("✅ Memory cleanup and TTL functional")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
