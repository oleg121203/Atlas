from __future__ import annotations

"""
Enhanced Memory Manager with better organization for different processes
"""

import logging
import threading
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

    def __init__(self, llm_manager: LLMManager, config_manager: ConfigManager, logger: logging.Logger):
        self.llm_manager = llm_manager
        self.config_manager = config_manager
        self.db_path = self.config_manager.get_app_data_path("memory")
        self._client: Optional[Client] = None
        self._client_lock = threading.Lock()
        self._init_memory_configs()
        self.logger = logger
        self.logger.info(f"EnhancedMemoryManager initialized. DB path configured for lazy loading: {self.db_path}")
        self.memory_database = []

    @property
    def client(self) -> Client:
        if self._client is None:
            with self._client_lock:
                if self._client is None:  # Double-check locking
                    try:
                        self.logger.info(f"Initializing ChromaDB client at path: {self.db_path}")
                        self._client = chromadb.PersistentClient(path=str(self.db_path))
                        self.logger.info("ChromaDB client initialized successfully.")
                    except Exception as e:
                        self.logger.error(f"Failed to initialize ChromaDB client: {e}", exc_info=True)
                        raise
        if self._client is None:
            raise ConnectionError("Failed to get a valid ChromaDB client instance.")
        return self._client

    def _get_embedding_function(self) -> Any:
        return self

    def __call__(self, input_texts: List[str]) -> List[List[float]]:
        embeddings_list = []
        for text in input_texts:
            embedding = self.llm_manager.get_embedding(text)
            embeddings_list.append(embedding if isinstance(embedding, list) else [0.0] * 1536)
        return embeddings_list

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Gets or creates a collection atomically, ensuring thread safety."""
        try:
            # Use the atomic get_or_create_collection method
            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self._get_embedding_function()
            )
            self.logger.debug(f"Successfully retrieved or created collection: {collection_name}")
            self._maybe_cleanup_collection(collection_name)
            return collection
        except Exception as e:
            self.logger.error(f"Failed to get or create collection '{collection_name}': {e}", exc_info=True)
            return None

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
        collection = self.get_collection(collection_name)
        if collection is None:
            self.logger.error(f"Failed to get/create collection {collection_name}")
            return
            
        doc_id = f"{collection_name}_{int(time.time())}_{hash(content) % 10000}"
        final_metadata = metadata or {}
        config = self.memory_configs.get(collection_name)
        if config and config.ttl_hours:
            final_metadata["expires_at"] = time.time() + config.ttl_hours * 3600
        
        try:
            collection.add(documents=[content], metadatas=[final_metadata], ids=[doc_id])
            self.logger.info(f"Added memory to '{collection_name}' with ID: {doc_id}")
        except Exception as e:
            self.logger.error(f"Failed to add memory to {collection_name}: {str(e)}")

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
        if collection_names is None:
            try:
                collection_names = [coll.name for coll in self.client.list_collections()]
            except Exception as e:
                self.logger.error(f"Failed to list collections: {str(e)}")
                return []
                
        results = []
        for name in collection_names:
            collection = self.get_collection(name)
            if collection is None:
                self.logger.warning(f"Skipping unavailable collection: {name}")
                continue
                
            try:
                query_result = collection.query(query_texts=[query], n_results=n_results)
                if query_result and query_result.get("documents") and query_result["documents"][0]:
                    for i, doc in enumerate(query_result["documents"][0]):
                        results.append({
                            "collection": name,
                            "content": doc,
                            "metadata": query_result["metadatas"][0][i],
                            "distance": query_result["distances"][0][i],
                        })
            except Exception as e:
                self.logger.error(f"Failed to query collection {name}: {str(e)}")
                continue
        results.sort(key=lambda x: x.get("distance", float("inf")))
        return results

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

    def _maybe_cleanup_collection(self, collection_name: str):
        """Clean up collection if needed based on configuration."""
        config = self.memory_configs.get(collection_name)
        if not config:
            return

        collection = self.get_collection(collection_name)
        if collection is None:
            self.logger.warning(f"Cannot clean up collection {collection_name} - does not exist")
            return
        if config.ttl_hours:
            self._cleanup_expired_memories(collection)
        if config.max_entries:
            self._cleanup_old_memories(collection, config.max_entries)

    def _cleanup_expired_memories(self, collection: Collection) -> int:
        """Remove expired memories from collection."""
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

    def _cleanup_old_memories(self, collection: Collection, max_entries: int):
        """Remove oldest memories to stay under max_entries limit."""
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

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        collections = self.client.list_collections()
        stats: Dict[str, Any] = {
            "total_collections": len(collections),
            "collections": {},
            "total_memories": 0,
            "memory_by_scope": {scope.value: 0 for scope in MemoryScope},
            "memory_by_type": {m_type.value: 0 for m_type in MemoryType},
        }

        for coll in collections:
            collection = self.get_collection(coll.name)
            if collection is None:
                continue
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

        # Clean up empty keys for a tidier output
        stats["memory_by_scope"] = {k: v for k, v in stats["memory_by_scope"].items() if v > 0}
        stats["memory_by_type"] = {k: v for k, v in stats["memory_by_type"].items() if v > 0}

        return stats

    def cleanup_all_expired(self) -> int:
        """Clean up all expired memories across all collections."""
        collections = self.client.list_collections()
        total_cleaned = 0
        self.logger.info(
            f"Starting cleanup of expired memories across {len(collections)} collections."
        )

        for coll in collections:
            collection = self.get_collection(coll.name)
            if collection is None:
                continue
            cleaned_count = self._cleanup_expired_memories(collection)
            total_cleaned += cleaned_count

        self.logger.info(f"Completed cleanup. Total expired memories removed: {total_cleaned}")
        return total_cleaned

    def add_active_learning_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add memory for active learning, e.g., questions for clarification.
        """
        self.add_memory(content, collection_name=MemoryScope.CHAT_CONTEXT.value, metadata=metadata)
        self.logger.info("Added active learning memory.")

    def add_passive_learning_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add memory for passive learning, e.g., inferred user preferences from observations.
        """
        self.add_memory(content, collection_name=MemoryScope.USER_DATA.value, metadata=metadata)
        self._maybe_cleanup_collection(MemoryScope.USER_DATA.value)

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            collection_name: Name of the collection to check
            
        Returns:
            True if the collection exists, False otherwise
        """
        try:
            if self.client:
                collections = self.client.list_collections()
                return any(c.name == collection_name for c in collections)
            return False
        except Exception as e:
            self.logger.error(f"Error checking collection existence: {str(e)}")
            return False
            
    def create_collection(self, collection_name: str) -> bool:
        """
        Create a new collection if it doesn't exist.
        
        Args:
            collection_name: Name of the collection to create
            
        Returns:
            True if the collection was created or already existed, False on error
        """
        try:
            if not self.collection_exists(collection_name):
                if self.client:
                    self.client.create_collection(
                        name=collection_name,
                        embedding_function=self._get_embedding_function()
                    )
                    self.logger.info(f"Created collection: {collection_name}")
                    return True
                else:
                    self.logger.warning("ChromaDB client not available")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to create collection {collection_name}: {str(e)}")
            return False
            
    def store_memory(
        self, agent_name: str, memory_type: MemoryType, content: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a memory in the specified collection.
        
        Args:
            agent_name: Name of the agent/scope to store memory for
            memory_type: Type of memory (GOAL, TASK_RESULT, etc)
            content: The content to store
            metadata: Optional metadata to store with the content
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Ensure collection exists
            if not self.create_collection(agent_name):
                self.logger.error(f"Failed to create/verify collection {agent_name}")
                return False
                
            # Prepare memory document
            memory_doc = {
                "type": memory_type.value,
                "content": content,
                "metadata": metadata or {},
                "timestamp": time.time()
            }
            
            # Store in database
            if self.db and hasattr(self.db, 'insert_one'):
                self.db[agent_name].insert_one(memory_doc)
                return True
            
            self.logger.warning("Database doesn't support memory storage")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to store memory: {str(e)}")
            return False
        
    def get_collection_safe(self, collection_name: str) -> Optional[Any]:
        """
        Safely get or create a collection without throwing exceptions.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection object or None if failed
        """
        try:
            if not self.client:
                self.logger.error("ChromaDB client not initialized")
                return None
                
            try:
                # Try to get existing collection
                collection = self.client.get_collection(name=collection_name)
                return collection
            except ValueError:
                # Collection doesn't exist, create it
                try:
                    collection = self.client.create_collection(
                        name=collection_name,
                        embedding_function=self._get_embedding_function()
                    )
                    self.logger.info(f"Created new collection: {collection_name}")
                    return collection
                except Exception as e:
                    self.logger.error(f"Failed to create collection {collection_name}: {str(e)}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting collection {collection_name}: {str(e)}")
            return None

    def store_memory_safe(self, agent_name: str, memory_type: MemoryType, content: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Safely store a memory with comprehensive error handling.
        
        Args:
            agent_name: Name of the agent/scope to store memory for
            memory_type: Type of memory (GOAL, TASK_RESULT, etc)
            content: The content to store
            metadata: Optional metadata to store with the content
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Get or create collection
            collection = self.get_collection_safe(agent_name)
            if not collection:
                self.logger.error(f"Failed to get/create collection {agent_name}")
                return False
                
            # Prepare memory document
            memory_id = f"{agent_name}_{memory_type.value}_{int(time.time() * 1000)}"
            memory_metadata = metadata or {}
            memory_metadata.update({
                "type": memory_type.value,
                "timestamp": time.time(),
                "agent": agent_name
            })
            
            # Convert content to string if it's not already
            content_str = str(content) if not isinstance(content, str) else content
            
            # Store in collection
            collection.add(
                ids=[memory_id],
                documents=[content_str],
                metadatas=[memory_metadata]
            )
            
            self.logger.debug(f"Stored memory in {agent_name}: {memory_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store memory safely: {str(e)}")
            return False

    def execute_task(self, prompt: str, context: Dict[str, Any]) -> str:
        """Execute a memory-related task."""
        self.logger.info(f"Executing memory task: {prompt}")
        try:
            if any(term in prompt.lower() for term in ["store", "save", "remember", "add", "log"]):
                return self._store_memory(prompt, context)
            elif any(term in prompt.lower() for term in ["recall", "retrieve", "find", "search", "history", "past", "previous", "context"]):
                return self._recall_memory(prompt, context)
            elif any(term in prompt.lower() for term in ["forget", "delete", "remove", "clear"]):
                return self._forget_memory(prompt, context)
            else:
                self.logger.warning(f"No specific handler for memory task: {prompt}")
                return self._default_task_handler(prompt, context)
        except Exception as e:
            self.logger.error(f"Error executing memory task: {str(e)}")
            return f"Failed to execute memory task: {str(e)}"

    def _store_memory(self, prompt: str, context: Dict[str, Any]) -> str:
        """Store a memory entry in the vector database."""
        self.logger.info(f"Storing memory: {prompt}")
        memory_content = self._extract_memory_content(prompt)
        if memory_content:
            vector = self._generate_vector(memory_content)
            self.memory_database.append({
                'content': memory_content,
                'vector': vector,
                'context': context,
                'timestamp': time.time()
            })
            return f"Memory stored: {memory_content}"
        return "No memory content to store."

    def _recall_memory(self, prompt: str, context: Dict[str, Any]) -> str:
        """Recall a memory entry from the vector database."""
        self.logger.info(f"Recalling memory: {prompt}")
        query = self._extract_memory_query(prompt)
        if query:
            query_vector = self._generate_vector(query)
            best_match = None
            best_score = -1
            for entry in self.memory_database:
                score = self._cosine_similarity(query_vector, entry['vector'])
                if score > best_score:
                    best_score = score
                    best_match = entry
            if best_match and best_score > 0.5:  # Threshold for relevance
                return f"Recalled memory: {best_match['content']}"
            return "No relevant memory found."
        return "No memory query specified."

    def _forget_memory(self, prompt: str, context: Dict[str, Any]) -> str:
        """Forget a memory entry from the vector database."""
        self.logger.info(f"Forgetting memory: {prompt}")
        query = self._extract_memory_query(prompt)
        if query:
            query_vector = self._generate_vector(query)
            best_match_index = -1
            best_score = -1
            for i, entry in enumerate(self.memory_database):
                score = self._cosine_similarity(query_vector, entry['vector'])
                if score > best_score:
                    best_score = score
                    best_match_index = i
            if best_match_index >= 0 and best_score > 0.5:  # Threshold for relevance
                forgotten = self.memory_database.pop(best_match_index)
                return f"Forgotten memory: {forgotten['content']}"
            return "No relevant memory found to forget."
        return "No memory query specified to forget."

    def _default_task_handler(self, prompt: str, context: Dict[str, Any]) -> str:
        """Handle memory tasks that don't match specific categories."""
        self.logger.info(f"Handling default memory task: {prompt}")
        return f"Memory task executed with default handler: {prompt}"

    def _extract_memory_content(self, prompt: str) -> str:
        """Extract content to store as memory from the prompt."""
        words = prompt.split()
        content_start = False
        content = []
        for i, word in enumerate(words):
            if word.lower() in ["store", "save", "remember", "add", "log"] and i + 1 < len(words):
                content_start = True
            elif content_start:
                content.append(word)
        return " ".join(content)

    def _extract_memory_query(self, prompt: str) -> str:
        """Extract query to recall or forget memory from the prompt."""
        words = prompt.split()
        query_start = False
        query = []
        for i, word in enumerate(words):
            if word.lower() in ["recall", "retrieve", "find", "search", "history", "past", "previous", "context", "forget", "delete", "remove", "clear"] and i + 1 < len(words):
                query_start = True
            elif query_start:
                query.append(word)
        return " ".join(query)

    def _generate_vector(self, text: str) -> list:
        """Generate a simple vector representation of text for similarity comparison."""
        # This is a placeholder for a real vectorization method (e.g., using embeddings)
        return [ord(c) for c in text[:10]] if text else [0] * 10

    def _cosine_similarity(self, vec1: list, vec2: list) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)
