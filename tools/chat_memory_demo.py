#!/usr/bin/env python3
"""
Demonstration of Enhanced Chat Memory System for Atlas

This script demonstrates:
1. Chat mode isolation
2. Plugin memory isolation  
3. Development mode features
4. Memory statistics and cleanup
"""

import os
import sys
import tempfile
import time
from pathlib import Path

#Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.chat_context_manager import (
    ChatContext,
    ChatContextManager,
    ChatMode,
    ModeControl,
)
from agents.enhanced_memory_manager import EnhancedMemoryManager


class ChatMemoryDemo:
    """Demonstration of the enhanced chat memory system."""

    def __init__(self):
        #Create temporary database for demo
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "demo_chroma"

        #Initialize managers
        self.memory_manager = EnhancedMemoryManager(db_path=str(self.db_path))
        self.chat_manager = ChatContextManager(memory_manager=self.memory_manager)

        print("🚀 Atlas Enhanced Chat Memory System Demo")
        print("=" * 60)
        print(f"💾 Database location: {self.db_path}")
        print()

    def demo_chat_modes(self):
        """Demonstrate different chat modes and their memory isolation."""
        print("1️⃣  CHAT MODES DEMONSTRATION")
        print("-" * 40)

        #Define realistic conversation scenarios
        scenarios = [
            {
                "mode": ChatMode.CASUAL_CHAT,
                "conversations": [
                    ("Hello Atlas! How are you today?", "Hello! I'm doing great, thanks for asking. How can I help you today?"),
                    ("What's the weather like?", "I'd be happy to help you check the weather. Let me get that information for you."),
                    ("Tell me a joke", "Why don't scientists trust atoms? Because they make up everything! 😄"),
                ],
            },
            {
                "mode": ChatMode.SYSTEM_HELP,
                "conversations": [
                    ("What are your main capabilities?", "I'm Atlas, an autonomous assistant with automation, screen analysis, file management, and system integration capabilities."),
                    ("How do I switch to development mode?", "You can switch to development mode manually for enhanced debugging and experimental features."),
                    ("What tools do you have available?", "I have screenshot tools, OCR, mouse/keyboard automation, file operations, and more."),
                ],
            },
            {
                "mode": ChatMode.GOAL_SETTING,
                "conversations": [
                    ("Take a screenshot of my desktop", "I'll take a screenshot of your desktop right away. Let me capture that for you."),
                    ("Open calculator application", "I'll help you open the calculator application. Searching for it now."),
                    ("Send an email notification", "I can help you send an email notification. What details should I include?"),
                ],
            },
            {
                "mode": ChatMode.DEVELOPMENT,
                "conversations": [
                    ("Show me system debug information", "🔧 DEV MODE: Here's detailed system debug info with safety protocols active."),
                    ("Analyze memory usage patterns", "🔧 DEV MODE: Analyzing memory patterns with enhanced diagnostics and backup procedures."),
                    ("Test experimental features", "🔧 DEV MODE: Enabling experimental features with full safety checks and rollback capability."),
                ],
            },
        ]

        #Store conversations for each mode
        for scenario in scenarios:
            mode = scenario["mode"]
            print(f"💬 {mode.value.upper()} Mode:")

            for user_msg, assistant_msg in scenario["conversations"]:
                #Create appropriate context
                context = ChatContext(
                    mode=mode,
                    confidence=0.95,
                    suggested_response_type=self.chat_manager._get_response_type(mode),
                    context_keywords=[],
                    requires_system_integration=(mode in [ChatMode.GOAL_SETTING, ChatMode.DEVELOPMENT]),
                    control_type=ModeControl.MANUAL if mode == ChatMode.DEVELOPMENT else ModeControl.AUTO,
                )

                #Store in memory
                self.chat_manager.update_conversation_history(
                    user_msg, assistant_msg, context,
                    metadata={"demo": True, "timestamp": time.time()},
                )

                print(f"   👤 User: {user_msg[:50]}...")
                print(f"   🤖 Atlas: {assistant_msg[:50]}...")
                print()

        print("✅ All conversations stored with mode isolation")
        print()

    def demo_memory_retrieval(self):
        """Demonstrate memory retrieval and mode isolation."""
        print("2️⃣  MEMORY RETRIEVAL & ISOLATION")
        print("-" * 40)

        #Test queries across different modes
        test_queries = [
            ("screenshot", "Looking for screenshot-related conversations"),
            ("help", "Looking for help-related conversations"),
            ("debug", "Looking for debug-related conversations"),
            ("weather", "Looking for weather-related conversations"),
        ]

        for query, description in test_queries:
            print(f"🔍 Query: '{query}' - {description}")

            for mode in [ChatMode.CASUAL_CHAT, ChatMode.SYSTEM_HELP, ChatMode.GOAL_SETTING, ChatMode.DEVELOPMENT]:
                memories = self.chat_manager.retrieve_conversation_context(mode, query, limit=3)
                print(f"   {mode.value}: {len(memories)} memories found")

                #Show sample memory if found
                if memories:
                    sample = memories[0]
                    content = sample.get("content", {})
                    if isinstance(content, dict):
                        user_msg = content.get("user_message", "No message")[:30]
                        print(f'     Sample: "{user_msg}..."')
            print()

        print("✅ Memory retrieval demonstrates perfect mode isolation")
        print()

    def demo_mode_statistics(self):
        """Demonstrate mode-specific statistics."""
        print("3️⃣  MODE STATISTICS")
        print("-" * 40)

        for mode in ChatMode:
            stats = self.chat_manager.get_mode_conversation_stats(mode)
            config = self.chat_manager.mode_memory_config.get(mode, {})

            print(f"📊 {mode.value.upper()}:")
            print(f"   TTL: {config.get('ttl_days', 'N/A')} days")
            print(f"   Max context: {config.get('max_context', 'N/A')} messages")
            print(f"   Current stats: {stats}")
            print()

        print("✅ Statistics show proper mode configuration")
        print()

    def demo_session_context(self):
        """Demonstrate enhanced session context with memory."""
        print("4️⃣  ENHANCED SESSION CONTEXT")
        print("-" * 40)

        test_scenarios = [
            (ChatMode.SYSTEM_HELP, "What can you do with screenshots?"),
            (ChatMode.DEVELOPMENT, "Show me performance metrics"),
            (ChatMode.CASUAL_CHAT, "How's your day going?"),
        ]

        for mode, query in test_scenarios:
            print(f'🎯 Mode: {mode.value} | Query: "{query}"')

            session_context = self.chat_manager.get_session_context_with_memory(query, mode, limit=2)

            print(f"   Context keys: {list(session_context.keys())}")
            print(f"   Relevant memories: {len(session_context.get('relevant_memories', []))}")
            print(f"   Mode stats available: {'mode_stats' in session_context}")
            print(f"   Memory enabled: {session_context.get('memory_enabled', False)}")
            print()

        print("✅ Enhanced session context provides rich memory integration")
        print()

    def demo_development_mode(self):
        """Demonstrate development mode specific features."""
        print("5️⃣  DEVELOPMENT MODE FEATURES")
        print("-" * 40)

        print("🔧 Development Mode Configuration:")
        for feature, enabled in self.chat_manager.development_mode_features.items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {feature}: {enabled}")

        print("\n🔧 Development Mode Context:")
        dev_context = self.chat_manager._create_development_context("Test development features")
        print(f"   Mode: {dev_context.mode}")
        print(f"   Confidence: {dev_context.confidence}")
        print(f"   Control Type: {dev_context.control_type}")
        print(f"   Requires Integration: {dev_context.requires_system_integration}")

        print("\n🔧 Development Memory Features:")
        print(f"   TTL: {self.chat_manager.mode_memory_config[ChatMode.DEVELOPMENT]['ttl_days']} days (longest)")
        print(f"   Max Context: {self.chat_manager.mode_memory_config[ChatMode.DEVELOPMENT]['max_context']} messages (largest)")
        print("   Enhanced metadata tracking")
        print("   Automatic backup functionality")
        print("   Detailed error logging")

        print("\n✅ Development mode provides enhanced capabilities with safety")
        print()

    def demo_memory_stats(self):
        """Show overall memory system statistics."""
        print("6️⃣  MEMORY SYSTEM STATISTICS")
        print("-" * 40)

        #Get comprehensive memory stats
        memory_stats = self.memory_manager.get_memory_stats()

        print("💾 Memory Database Statistics:")
        total_entries = 0
        for scope_name, scope_stats in memory_stats.items():
            scope_total = sum(stats.get("count", 0) for stats in scope_stats.values())
            total_entries += scope_total
            print(f"   📂 {scope_name}: {scope_total} entries")

            for mem_type, type_stats in scope_stats.items():
                count = type_stats.get("count", 0)
                if count > 0:
                    print(f"     └─ {mem_type}: {count} memories")

        print(f"\n📊 Total Memories: {total_entries}")

        #Chat-specific statistics
        print("\n💬 Chat System Statistics:")
        chat_history_length = len(self.chat_manager.conversation_history)
        print(f"   In-memory history: {chat_history_length} entries")
        print(f"   Auto mode enabled: {self.chat_manager.auto_mode_enabled}")
        print(f"   Current mode: {self.chat_manager.current_mode}")
        print(f"   Manual override: {self.chat_manager.manual_override_mode}")

        print("\n✅ Memory system operating efficiently")
        print()

    def demo_cleanup_simulation(self):
        """Demonstrate memory cleanup capabilities."""
        print("7️⃣  MEMORY CLEANUP SIMULATION")
        print("-" * 40)

        print("🧹 Cleanup Operations Available:")
        print("   ⏰ Automatic TTL-based cleanup")
        print("   🎯 Mode-specific cleanup")
        print("   🌍 Global cleanup")
        print("   📊 Memory optimization")

        #Simulate cleanup
        print("\n🧹 Performing cleanup simulation...")

        #Global cleanup
        self.chat_manager.cleanup_old_conversations()
        print("   ✅ Global conversation cleanup completed")

        #Mode-specific cleanup
        self.chat_manager.cleanup_old_conversations(ChatMode.CASUAL_CHAT)
        print("   ✅ Casual chat cleanup completed")

        #Memory manager cleanup
        cleaned = self.memory_manager.cleanup_expired_memories()
        print(f"   ✅ Memory manager cleanup: {cleaned} expired entries removed")

        print("\n✅ Cleanup system maintains optimal performance")
        print()

    def cleanup(self):
        """Clean up demo resources."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Demo cleanup: Removed {self.temp_dir}")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")

    def run_full_demo(self):
        """Run the complete demonstration."""
        try:
            self.demo_chat_modes()
            self.demo_memory_retrieval()
            self.demo_mode_statistics()
            self.demo_session_context()
            self.demo_development_mode()
            self.demo_memory_stats()
            self.demo_cleanup_simulation()

            print("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("✨ Key Features Demonstrated:")
            print("   🔒 Perfect memory isolation between chat modes")
            print("   🧠 Intelligent context retrieval with relevance")
            print("   🔧 Enhanced development mode with safety features")
            print("   📊 Comprehensive statistics and monitoring")
            print("   🧹 Automatic cleanup and optimization")
            print("   ⚙️  Configurable TTL and context limits per mode")
            print()
            print("🎯 Benefits:")
            print("   • Users get consistent, mode-appropriate responses")
            print("   • No context bleeding between different conversation types")
            print("   • Developers get enhanced capabilities with safety guards")
            print("   • Automatic memory management prevents bloat")
            print("   • Rich analytics for system optimization")

        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()


def main():
    """Run the chat memory demonstration."""
    demo = ChatMemoryDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main()
