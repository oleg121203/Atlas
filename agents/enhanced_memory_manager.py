from __future__ import annotations

"""
Enhanced Memory Manager with better organization for different processes
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import chromadb
from chromadb import Client, Collection, EmbeddingFunction

from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


class MemoryScope(Enum):
    """Memory scope definitions for different processes"""

    MASTER_AGENT = "master_agent"
    SCREEN_AGENT = "screen_agent"
    BROWSER_AGENT = "browser_agent"
    SECURITY_AGENT = "security_agent"
    DEPUTY_AGENT = "deputy_agent"
    TEXT_AGENT = "text_agent"
    CHAT_CONTEXT = "chat_context"
    USER_DATA = "user_data"
    SYSTEM_KNOWLEDGE = "system_knowledge"
    TEMPORARY = "temporary"
    GLOBAL = "global"


class MemoryType(Enum):
    """Types of memories for better categorization"""

    PLAN = "plan"
    OBSERVATION = "observation"
    INTERACTION = "interaction"
    FEEDBACK = "feedback"
    ERROR = "error"
    SUCCESS = "success"
    PREFERENCE = "preference"
    SESSION = "session"
    KNOWLEDGE = "knowledge"
    TEMPORARY = "temporary"
    CASUAL_CHAT = "casual_chat"
    GOALS = "goals"
    GOAL_SETTING = "goal_setting"
    HELP_QUERIES = "help_queries"
    TOOL_INQUIRY = "tool_inquiry"
    TOOL_USAGE = "tool_usage"
    STATUS_CHECK = "status_check"
    STATUS_CHECKS = "status_checks"
    CONFIGURATION = "configuration"
    CONFIGURATION_CHAT = "configuration_chat"
    DEBUG_INFO = "debug_info"
    DEV_OPERATIONS = "dev_operations"
    EXPERIMENTS = "experiments"
    DEBUG_SESSIONS = "debug_sessions"


@dataclass
class MemoryConfig:
    """Configuration for memory collections"""

    scope: MemoryScope
    memory_type: MemoryType
    ttl_hours: Optional[int] = None
    max_entries: Optional[int] = None
    auto_archive: bool = False


class EnhancedMemoryManager:
    """Enhanced memory manager with better organization for different processes"""

    def __init__(self, llm_manager: LLMManager, config_manager: ConfigManager):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm_manager = llm_manager
        self.config_manager = config_manager

        self.db_path = self.config_manager.get_app_data_path("memory")
        self._client: Optional[Client] = None

        # Initialize memory configurations
        self._init_memory_configs()

        self.logger.info(f"EnhancedMemoryManager initialized. DB path configured for lazy loading: {self.db_path}")

    @property
    def client(self) -> Client:
        """Lazily initializes and returns the ChromaDB client."""
        if self._client is None:
            try:
                self._client = chromadb.PersistentClient(path=str(self.db_path))
                self.logger.info("ChromaDB client initialized successfully.")
            except Exception as e:
                self.logger.error(f"Failed to initialize ChromaDB client: {e}", exc_info=True)
                raise
        return self._client

    def _init_memory_configs(self):
        """Initialize predefined memory configurations"""
        self.memory_configs: Dict[str, MemoryConfig] = {
            f"{MemoryScope.MASTER_AGENT.value}_{MemoryType.PLAN.value}": MemoryConfig(
                scope=MemoryScope.MASTER_AGENT, memory_type=MemoryType.PLAN, ttl_hours=24 * 7
            ),
            f"{MemoryScope.MASTER_AGENT.value}_{MemoryType.GOALS.value}": MemoryConfig(
                scope=MemoryScope.MASTER_AGENT, memory_type=MemoryType.GOALS, max_entries=100
            ),
            f"{MemoryScope.CHAT_CONTEXT.value}_{MemoryType.CASUAL_CHAT.value}": MemoryConfig(
                scope=MemoryScope.CHAT_CONTEXT, memory_type=MemoryType.CASUAL_CHAT, ttl_hours=1
            ),
            f"{MemoryScope.USER_DATA.value}_{MemoryType.PREFERENCE.value}": MemoryConfig(
                scope=MemoryScope.USER_DATA, memory_type=MemoryType.PREFERENCE
            ),
            f"{MemoryScope.GLOBAL.value}_{MemoryType.KNOWLEDGE.value}": MemoryConfig(
                scope=MemoryScope.GLOBAL, memory_type=MemoryType.KNOWLEDGE
            ),
        }

    def _get_embedding_function(self) -> EmbeddingFunction:
        """Returns a ChromaDB-compatible embedding function."""
        return self

    def __call__(self, input_texts: List[str]) -> List[List[float]]:
        """Generate embeddings for the given texts."""
        return self.llm_manager.get_embedding(input_texts)

    def get_collection(self, collection_name: str) -> Collection:
        """Gets or creates a collection with proper configuration."""
        collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self._get_embedding_function()
        )
        self._maybe_cleanup_collection(collection_name)
        return collection

    def add_memory_for_agent(
        self,
        agent_type: MemoryScope,
        memory_type: MemoryType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Add memory specific to an agent type."""
        collection_name = f"{agent_type.value}_{memory_type.value}"
        self.add_memory(content, collection_name, metadata)

    def store_memory(
        self,
        agent_name: str,
        memory_type: MemoryType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_days: Optional[int] = None,  # For backward compatibility
    ):
        """Store memory - alias for add_memory_for_agent for backwards compatibility."""
        # Map old agent_name to new MemoryScope
        try:
            agent_type = MemoryScope[agent_name.upper()]
        except KeyError:
            self.logger.warning(f"Unknown agent name '{agent_name}'. Defaulting to GLOBAL scope.")
            agent_type = MemoryScope.GLOBAL

        self.add_memory_for_agent(agent_type, memory_type, content, metadata)

    def add_memory(self, content: str, collection_name: str, metadata: Optional[Dict[str, Any]] = None):
        """Adds a memory to the specified collection with enhanced metadata."""
        try:
            collection = self.get_collection(collection_name)
            doc_id = f"{collection_name}_{int(time.time())}_{hash(content) % 10000}"

            # Prepare metadata
            final_metadata = metadata.copy() if metadata else {}
            final_metadata["timestamp"] = time.time()

            # Handle TTL
            config = self.memory_configs.get(collection_name)
            if config and config.ttl_hours:
                final_metadata["expires_at"] = time.time() + config.ttl_hours * 3600

            collection.add(documents=[content], metadatas=[final_metadata], ids=[doc_id])
            self.logger.info(f"Added memory to '{collection_name}' with ID: {doc_id}")

        except Exception as e:
            self.logger.error(f"Failed to add memory to '{collection_name}': {e}", exc_info=True)

    def retrieve_memories(
        self,
        agent_name: str,
        memory_type: MemoryType,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Retrieve memories - alias for search_memories_for_agent for backwards compatibility."""
        try:
            agent_type = MemoryScope[agent_name.upper()]
        except KeyError:
            self.logger.warning(f"Unknown agent name '{agent_name}'. Defaulting to GLOBAL scope.")
            return []
        
        return self.search_memories_for_agent(agent_type, memory_type, query, n_results=limit)

    def search_memories_for_agent(
        self,
        agent_type: MemoryScope,
        memory_type: MemoryType,
        query: str,
        n_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search memories specific to an agent type."""
        collection_name = f"{agent_type.value}_{memory_type.value}"
        return self.search_memories(query, [collection_name], n_results)

    def search_memories(
        self,
        query: str,
        collection_names: Optional[List[str]] = None,
        n_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Enhanced search with better organization and filtering."""
        results: List[Dict[str, Any]] = []
        try:
            if not collection_names:
                # Search all collections if none are specified
                all_collections = self.client.list_collections()
                collection_names = [c.name for c in all_collections]

            for name in collection_names:
                try:
                    collection = self.client.get_collection(
                        name=name, embedding_function=self._get_embedding_function()
                    )
                    query_result = collection.query(query_texts=[query], n_results=n_results)
                    
                    # Process results
                    if query_result and query_result["documents"] and query_result["documents"][0]:
                        for i, doc in enumerate(query_result["documents"][0]):
                            results.append({
                                "collection": name,
                                "content": doc,
                                "metadata": query_result["metadatas"][0][i],
                                "distance": query_result["distances"][0][i],
                            })
                except Exception as e:
                    self.logger.error(f"Failed to query collection '{name}': {e}")

            # Sort results by distance (lower is better)
            results.sort(key=lambda x: x.get("distance", float("inf")))
            return results[:n_results]

        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}", exc_info=True)
            return []

    def _maybe_cleanup_collection(self, collection_name: str):
        """Clean up collection if needed based on configuration."""
        config = self.memory_configs.get(collection_name)
        if not config:
            return

        try:
            collection = self.client.get_collection(
                name=collection_name, embedding_function=self._get_embedding_function()
            )
            if config.ttl_hours:
                self._cleanup_expired_memories(collection)
            if config.max_entries:
                self._cleanup_old_memories(collection, config.max_entries)

        except Exception as e:
            self.logger.error(f"Error during cleanup for collection '{collection_name}': {e}")

    def _cleanup_expired_memories(self, collection: Collection) -> int:
        """Remove expired memories from collection."""
        try:
            all_data = collection.get(include=["metadatas"])
            ids_to_delete = []
            current_time = time.time()

            metadatas = all_data.get("metadatas")
            if metadatas:
                for i, metadata in enumerate(metadatas):
                    expires_at = metadata.get("expires_at") if metadata else None
                    if expires_at and isinstance(expires_at, (int, float)):
                        if expires_at < current_time:
                            ids_to_delete.append(all_data["ids"][i])

            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                self.logger.info(
                    f"Cleaned up {len(ids_to_delete)} expired memories from '{collection.name}'"
                )
            return len(ids_to_delete)

        except Exception as e:
            self.logger.error(f"Error cleaning expired memories: {e}")
            return 0

    def _cleanup_old_memories(self, collection: Collection, max_entries: int):
        """Remove oldest memories to stay under max_entries limit."""
        try:
            count = collection.count()
            if count <= max_entries:
                return

            # Get all documents with timestamps
            all_data = collection.get(include=["metadatas"])
            if not all_data or not all_data.get("ids"):
                return

            # Sort by timestamp and delete oldest
            entries_with_time = []
            metadatas = all_data.get("metadatas")
            if metadatas:
                for i, metadata in enumerate(metadatas):
                    timestamp = metadata.get("timestamp", 0) if metadata else 0
                    entries_with_time.append((timestamp, all_data["ids"][i]))

            entries_with_time.sort()  # Oldest first

            entries_to_delete = count - max_entries
            ids_to_delete = [entry[1] for entry in entries_with_time[:entries_to_delete]]

            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                self.logger.info(
                    f"Cleaned up {len(ids_to_delete)} old memories from '{collection.name}'"
                )

        except Exception as e:
            self.logger.error(f"Error cleaning old memories: {e}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        try:
            collections = self.client.list_collections()
            stats: Dict[str, Any] = {
                "total_collections": len(collections),
                "collections": {},
                "total_memories": 0,
                "memory_by_scope": {scope.value: 0 for scope in MemoryScope},
                "memory_by_type": {m_type.value: 0 for m_type in MemoryType},
            }

            for coll in collections:
                try:
                    collection = self.client.get_collection(
                        name=coll.name, embedding_function=self._get_embedding_function()
                    )
                    count = collection.count()

                    stats["total_memories"] += count
                    stats["collections"][coll.name] = {
                        "count": count,
                        "config": self.memory_configs.get(coll.name),
                    }

                    # Parse scope and type from collection name
                    parts = coll.name.split("_", 1)
                    if len(parts) == 2:
                        scope_str, type_str = parts
                        if scope_str in stats["memory_by_scope"]:
                            stats["memory_by_scope"][scope_str] += count
                        if type_str in stats["memory_by_type"]:
                            stats["memory_by_type"][type_str] += count

                except Exception as e:
                    self.logger.error(f"Could not process collection '{coll.name}': {e}")
                    stats["collections"][coll.name] = {"error": str(e)}

            # Clean up empty keys for a tidier output
            stats["memory_by_scope"] = {k: v for k, v in stats["memory_by_scope"].items() if v > 0}
            stats["memory_by_type"] = {k: v for k, v in stats["memory_by_type"].items() if v > 0}

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}", exc_info=True)
            return {"error": f"Failed to retrieve memory stats: {e}"}

    def cleanup_all_expired(self) -> int:
        """Clean up all expired memories across all collections."""
        try:
            collections = self.client.list_collections()
            total_cleaned = 0
            self.logger.info(
                f"Starting cleanup of expired memories across {len(collections)} collections."
            )

            for coll in collections:
                try:
                    collection = self.client.get_collection(
                        name=coll.name, embedding_function=self._get_embedding_function()
                    )
                    cleaned_count = self._cleanup_expired_memories(collection)
                    total_cleaned += cleaned_count

                except Exception as e:
                    self.logger.error(f"Error during cleanup of collection '{coll.name}': {e}")

            self.logger.info(f"Completed cleanup. Total expired memories removed: {total_cleaned}")
            return total_cleaned

        except Exception as e:
            self.logger.error(f"Failed to run cleanup_all_expired: {e}", exc_info=True)
            return 0
