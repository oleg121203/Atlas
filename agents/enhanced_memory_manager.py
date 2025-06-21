"""
Enhanced Memory Manager with better organization for different processes
"""

import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import chromadb
from chromadb import EmbeddingFunction

from monitoring.metrics_manager import metrics_manager
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

    #Chat-specific types for mode isolation
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

    #Development mode types
    DEV_OPERATIONS = "dev_operations"
    EXPERIMENTS = "experiments"
    DEBUG_SESSIONS = "debug_sessions"


@dataclass
class MemoryConfig:
    """Configuration for memory collections"""
    scope: MemoryScope
    memory_type: MemoryType
    ttl_hours: Optional[int] = None  #Time-to-live in hours
    max_entries: Optional[int] = None  #Maximum entries before cleanup
    auto_archive: bool = False  #Auto-archive old entries


class EnhancedMemoryManager:
    """Enhanced memory manager with better organization for different processes"""

    def __init__(self, llm_manager: LLMManager, config_manager: ConfigManager):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm_manager = llm_manager
        self.config_manager = config_manager

        db_path = self.config_manager.get_app_data_path("memory")
        self.client = chromadb.PersistentClient(path=str(db_path))

        #Initialize memory configurations
        self._init_memory_configs()

        self.logger.info(f"EnhancedMemoryManager initialized. Database path: {db_path}")

    def _init_memory_configs(self):
        """Initialize predefined memory configurations"""
        self.memory_configs = {
            #Agent-specific memories
            "master_agent_plans": MemoryConfig(MemoryScope.MASTER_AGENT, MemoryType.PLAN, ttl_hours=24*7),
            "master_agent_feedback": MemoryConfig(MemoryScope.MASTER_AGENT, MemoryType.FEEDBACK, ttl_hours=24*30),
            "screen_agent_observations": MemoryConfig(MemoryScope.SCREEN_AGENT, MemoryType.OBSERVATION, ttl_hours=24),
            "browser_agent_interactions": MemoryConfig(MemoryScope.BROWSER_AGENT, MemoryType.INTERACTION, ttl_hours=24*7),
            "security_agent_events": MemoryConfig(MemoryScope.SECURITY_AGENT, MemoryType.OBSERVATION, ttl_hours=24*7),
            "deputy_agent_monitoring": MemoryConfig(MemoryScope.DEPUTY_AGENT, MemoryType.OBSERVATION, ttl_hours=24),

            #User data
            "user_feedback": MemoryConfig(MemoryScope.USER_DATA, MemoryType.FEEDBACK, ttl_hours=24*30),
            "user_preferences": MemoryConfig(MemoryScope.USER_DATA, MemoryType.PREFERENCE),
            "user_sessions": MemoryConfig(MemoryScope.USER_DATA, MemoryType.SESSION, ttl_hours=24*7),

            #System knowledge
            "successful_patterns": MemoryConfig(MemoryScope.SYSTEM_KNOWLEDGE, MemoryType.SUCCESS),
            "error_solutions": MemoryConfig(MemoryScope.SYSTEM_KNOWLEDGE, MemoryType.ERROR),
            "system_knowledge": MemoryConfig(MemoryScope.SYSTEM_KNOWLEDGE, MemoryType.KNOWLEDGE),

            #Temporary memories
            "current_session": MemoryConfig(MemoryScope.TEMPORARY, MemoryType.SESSION, ttl_hours=1),
            "recent_actions": MemoryConfig(MemoryScope.TEMPORARY, MemoryType.TEMPORARY, ttl_hours=2),
        }

    def _get_embedding_function(self) -> EmbeddingFunction:
        """Returns a ChromaDB-compatible embedding function."""
        class LLMManagerEmbeddingFunction(EmbeddingFunction):
            def __init__(self, llm_manager_instance: LLMManager):
                self._llm_manager = llm_manager_instance

            def __call__(self, input_texts: chromadb.Documents) -> chromadb.Embeddings:
                return [self._llm_manager.get_embedding(text) for text in input_texts]

        return LLMManagerEmbeddingFunction(self.llm_manager)

    def get_collection(self, collection_name: str) -> chromadb.Collection:
        """Gets or creates a collection with proper configuration."""
        return self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._get_embedding_function(),
        )

    def add_memory_for_agent(self,
                           agent_type: MemoryScope,
                           memory_type: MemoryType,
                           content: str,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add memory specific to an agent type."""
        collection_name = f"{agent_type.value}_{memory_type.value}"
        return self.add_memory(content, collection_name, metadata)

    def store_memory(self,
                    agent_name: str,
                    memory_type: MemoryType,
                    content: str,
                    metadata: Optional[Dict[str, Any]] = None,
                    ttl_days: Optional[int] = None) -> str:
        """Store memory - alias for add_memory_for_agent for backwards compatibility."""
        #Convert agent_name string to MemoryScope enum
        try:
            agent_scope = MemoryScope(agent_name.lower().replace(" ", "_"))
        except ValueError:
            #Fallback to GLOBAL if agent name not recognized
            agent_scope = MemoryScope.GLOBAL

        collection_name = f"{agent_scope.value}_{memory_type.value}"
        return self.add_memory(content, collection_name, metadata)

    def add_memory(self, content: str, collection_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Adds a memory to the specified collection with enhanced metadata."""
        if not content:
            raise ValueError("Content cannot be empty.")

        collection = self.get_collection(collection_name)

        doc_id = str(uuid.uuid4())
        final_metadata = metadata or {}

        #Add standard metadata
        final_metadata.update({
            "timestamp": time.time(),
            "collection": collection_name,
            "id": doc_id,
        })

        #Add TTL if configured
        if collection_name in self.memory_configs:
            config = self.memory_configs[collection_name]
            if config.ttl_hours:
                final_metadata["expires_at"] = time.time() + (config.ttl_hours * 3600)

        collection.add(
            documents=[content],
            metadatas=[final_metadata],
            ids=[doc_id],
        )

        self.logger.info(f"Added memory to '{collection_name}' with ID: {doc_id}")

        #Check if cleanup is needed
        self._maybe_cleanup_collection(collection_name)

        return doc_id

    def retrieve_memories(self,
                         agent_name: str,
                         memory_type: MemoryType,
                         query: str,
                         limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve memories - alias for search_memories_for_agent for backwards compatibility."""
        #Convert agent_name string to MemoryScope enum
        try:
            agent_scope = MemoryScope(agent_name.lower().replace(" ", "_"))
        except ValueError:
            #Fallback to GLOBAL if agent name not recognized
            agent_scope = MemoryScope.GLOBAL

        return self.search_memories_for_agent(agent_scope, memory_type, query, limit)

    def search_memories_for_agent(self,
                                agent_type: MemoryScope,
                                memory_type: MemoryType,
                                query: str,
                                n_results: int = 10) -> List[Dict[str, Any]]:
        """Search memories specific to an agent type."""
        if memory_type:
            collection_names = [f"{agent_type.value}_{memory_type.value}"]
        else:
            #Search all collections for this agent
            collection_names = [name for name in self.memory_configs.keys()
                              if name.startswith(agent_type.value)]

        return self.search_memories(query, collection_names, n_results)

    def search_memories(self,
                       query: str,
                       collection_names: Optional[List[str]] = None,
                       n_results: int = 10) -> List[Dict[str, Any]]:
        """Enhanced search with better organization and filtering."""
        self.logger.info(f"Searching for memories matching '{query}' in collections '{collection_names or 'all'}'")
        start_time = time.perf_counter()

        try:
            query_embedding = self.llm_manager.get_embedding(query)
            if not query_embedding:
                self.logger.error("Could not generate embedding for query.")
                return []

            collections_to_search = []

            if collection_names:
                for name in collection_names:
                    try:
                        collection = self.client.get_collection(name=name, embedding_function=self._get_embedding_function())
                        collections_to_search.append(collection)
                    except Exception as e:
                        self.logger.warning(f"Collection '{name}' not found: {e}")
            else:
                db_collections = self.client.list_collections()
                for coll in db_collections:
                    collections_to_search.append(
                        self.client.get_collection(name=coll.name, embedding_function=self._get_embedding_function()),
                    )

            all_results = []
            current_time = time.time()

            for collection in collections_to_search:
                count = collection.count()
                if count == 0:
                    continue

                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(n_results * 2, count),  #Get more to filter
                    include=["metadatas", "documents", "distances"],
                )

                ids = results.get("ids", [[]])[0]
                docs = results.get("documents", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]

                for i in range(len(ids)):
                    metadata = metadatas[i] if metadatas else {}

                    #Filter expired memories
                    if "expires_at" in metadata and metadata["expires_at"] < current_time:
                        continue

                    all_results.append({
                        "id": ids[i],
                        "content": docs[i],
                        "metadata": metadata,
                        "distance": distances[i],
                        "collection": collection.name,
                        "relevance": 1 - distances[i],  #Convert distance to relevance
                    })

            #Sort by relevance and limit results
            sorted_results = sorted(all_results, key=lambda x: x["distance"])
            final_results = sorted_results[:n_results]

            self.logger.info(f"Found {len(final_results)} relevant memories for query: '{query[:50]}...'")
            return final_results

        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}", exc_info=True)
            return []
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            metrics_manager.record_memory_search_latency(duration)
            self.logger.info(f"Memory search completed in {duration:.4f} seconds.")

    def _maybe_cleanup_collection(self, collection_name: str):
        """Clean up collection if needed based on configuration."""
        if collection_name not in self.memory_configs:
            return

        config = self.memory_configs[collection_name]
        collection = self.get_collection(collection_name)

        try:
            count = collection.count()

            #Clean up expired entries
            if config.ttl_hours:
                self._cleanup_expired_memories(collection)

            #Clean up if max entries exceeded
            if config.max_entries and count > config.max_entries:
                self._cleanup_old_memories(collection, config.max_entries)

        except Exception as e:
            self.logger.error(f"Error during cleanup of '{collection_name}': {e}")

    def _cleanup_expired_memories(self, collection: chromadb.Collection):
        """Remove expired memories from collection."""
        try:
            current_time = time.time()

            #Get all documents with metadata
            all_data = collection.get(include=["metadatas"])
            ids_to_delete = []

            for i, metadata in enumerate(all_data["metadatas"]):
                if metadata and "expires_at" in metadata:
                    if metadata["expires_at"] < current_time:
                        ids_to_delete.append(all_data["ids"][i])

            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                self.logger.info(f"Cleaned up {len(ids_to_delete)} expired memories from '{collection.name}'")

        except Exception as e:
            self.logger.error(f"Error cleaning expired memories: {e}")

    def _cleanup_old_memories(self, collection: chromadb.Collection, max_entries: int):
        """Remove oldest memories to stay under max_entries limit."""
        try:
            count = collection.count()
            if count <= max_entries:
                return

            #Get all documents with timestamps
            all_data = collection.get(include=["metadatas"])

            #Sort by timestamp and delete oldest
            entries_with_time = []
            for i, metadata in enumerate(all_data["metadatas"]):
                timestamp = metadata.get("timestamp", 0) if metadata else 0
                entries_with_time.append((timestamp, all_data["ids"][i]))

            entries_with_time.sort()  #Oldest first

            entries_to_delete = count - max_entries
            ids_to_delete = [entry[1] for entry in entries_with_time[:entries_to_delete]]

            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                self.logger.info(f"Cleaned up {len(ids_to_delete)} old memories from '{collection.name}'")

        except Exception as e:
            self.logger.error(f"Error cleaning old memories: {e}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        try:
            collections = self.client.list_collections()
            stats = {
                "total_collections": len(collections),
                "collections": {},
                "total_memories": 0,
                "memory_by_scope": {},
                "memory_by_type": {},
            }

            for coll in collections:
                collection = self.client.get_collection(name=coll.name, embedding_function=self._get_embedding_function())
                count = collection.count()
                stats["total_memories"] += count
                stats["collections"][coll.name] = count

                #Categorize by scope and type
                for scope in MemoryScope:
                    if coll.name.startswith(scope.value):
                        stats["memory_by_scope"][scope.value] = stats["memory_by_scope"].get(scope.value, 0) + count
                        break

                for mem_type in MemoryType:
                    if mem_type.value in coll.name:
                        stats["memory_by_type"][mem_type.value] = stats["memory_by_type"].get(mem_type.value, 0) + count
                        break

            return stats

        except Exception as e:
            self.logger.error(f"Error getting memory stats: {e}")
            return {}

    def cleanup_all_expired(self):
        """Clean up all expired memories across all collections."""
        try:
            collections = self.client.list_collections()
            total_cleaned = 0

            for coll in collections:
                collection = self.client.get_collection(name=coll.name, embedding_function=self._get_embedding_function())
                before_count = collection.count()
                self._cleanup_expired_memories(collection)
                after_count = collection.count()
                total_cleaned += (before_count - after_count)

            self.logger.info(f"Cleaned up {total_cleaned} expired memories across all collections")
            return total_cleaned

        except Exception as e:
            self.logger.error(f"Error during global cleanup: {e}")
            return 0
