#!/usr/bin/env python3
"""
Test enhanced memory manager integration
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from modules.agents.enhanced_memory_manager import (
    EnhancedMemoryManager,
    MemoryScope,
    MemoryType,
)

from utils.config_manager import ConfigManager


class MockLLMManager:
    """Mock LLM manager for testing"""

    def get_embedding(self, text: str):
        # Return a simple mock embedding
        return [0.1] * 384  # Typical embedding dimension


class TestEnhancedMemoryManager(unittest.TestCase):
    """Test enhanced memory manager functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager()
        # Override the data path to use temp directory
        self.config_manager.get_app_data_path = lambda x: Path(self.temp_dir) / x

        self.llm_manager = MockLLMManager()
        self.memory_manager = EnhancedMemoryManager(
            self.llm_manager, self.config_manager
        )

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_agent_specific_memory(self):
        """Test agent-specific memory storage and retrieval"""
        # Add memory for Master Agent
        memory_id = self.memory_manager.add_memory_for_agent(
            agent_type=MemoryScope.MASTER_AGENT,
            memory_type=MemoryType.PLAN,
            content="Test plan for desktop analysis",
            metadata={"goal": "test_goal"},
        )

        self.assertIsNotNone(memory_id)

        # Search memories for Master Agent
        results = self.memory_manager.search_memories_for_agent(
            agent_type=MemoryScope.MASTER_AGENT,
            query="desktop",
            memory_type=MemoryType.PLAN,
        )

        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["metadata"]["goal"], "test_goal")

    def test_memory_isolation(self):
        """Test memory isolation between agents"""
        # Add memory for different agents
        self.memory_manager.add_memory_for_agent(
            agent_type=MemoryScope.MASTER_AGENT,
            memory_type=MemoryType.PLAN,
            content="Master agent plan",
            metadata={"agent": "master"},
        )

        self.memory_manager.add_memory_for_agent(
            agent_type=MemoryScope.SCREEN_AGENT,
            memory_type=MemoryType.OBSERVATION,
            content="Screen agent observation",
            metadata={"agent": "screen"},
        )

        # Search should return only Master Agent memories
        master_results = self.memory_manager.search_memories_for_agent(
            agent_type=MemoryScope.MASTER_AGENT,
            query="agent",
        )

        # Search should return only Screen Agent memories
        screen_results = self.memory_manager.search_memories_for_agent(
            agent_type=MemoryScope.SCREEN_AGENT,
            query="agent",
        )

        # Verify isolation
        for result in master_results:
            self.assertEqual(result["metadata"]["agent"], "master")

        for result in screen_results:
            self.assertEqual(result["metadata"]["agent"], "screen")

    def test_memory_stats(self):
        """Test memory statistics functionality"""
        # Add some memories
        self.memory_manager.add_memory_for_agent(
            MemoryScope.MASTER_AGENT,
            MemoryType.PLAN,
            "Plan 1",
        )
        self.memory_manager.add_memory_for_agent(
            MemoryScope.SCREEN_AGENT,
            MemoryType.OBSERVATION,
            "Observation 1",
        )

        stats = self.memory_manager.get_memory_stats()

        self.assertIn("total_collections", stats)
        self.assertIn("total_memories", stats)
        self.assertIn("memory_by_scope", stats)
        self.assertIn("memory_by_type", stats)

        self.assertGreater(stats["total_memories"], 0)

    def test_ttl_metadata(self):
        """Test TTL metadata is added correctly"""
        memory_id = self.memory_manager.add_memory(
            content="Test content",
            collection_name="current_session",  # This has TTL configured
        )

        # Get the memory back to check metadata
        collection = self.memory_manager.get_collection("current_session")
        result = collection.get(ids=[memory_id], include=["metadatas"])

        metadata = result["metadatas"][0] if result["metadatas"] else {}
        self.assertIn("expires_at", metadata)
        self.assertIn("timestamp", metadata)


def run_integration_test():
    """Run integration test"""
    print("🧪 Running Enhanced Memory Manager Integration Test")
    print("=" * 50)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedMemoryManager)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ All tests passed! Enhanced Memory Manager is working correctly.")
        return True
    print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
    return False


if __name__ == "__main__":
    try:
        run_integration_test()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Note: This test requires ChromaDB to be installed")
    except Exception as e:
        print(f"❌ Test failed: {e}")
