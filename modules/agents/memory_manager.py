import logging
import time
import uuid
from typing import Any, Dict, List, Optional

import chromadb
from chromadb import EmbeddingFunction

from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


class MemoryManager:
    """Manages the agent's long-term memory using a vector store."""

    def __init__(self, llm_manager: LLMManager, config_manager: ConfigManager):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm_manager = llm_manager
        self.config_manager = config_manager

        db_path = self.config_manager.get_app_data_path("memory")
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.logger.info(f"MemoryManager initialized. Database path: {db_path}")

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Generates an embedding for a given text."""
        try:
            return self.llm_manager.get_embedding(text)
        except Exception as e:
            self.logger.error(f"Failed to get embedding: {e}", exc_info=True)
            return None

    def _get_embedding_function(self) -> EmbeddingFunction:
        """Returns a ChromaDB-compatible embedding function."""
        class LLMManagerEmbeddingFunction(EmbeddingFunction):
            def __init__(self, llm_manager_instance: LLMManager):
                self._llm_manager = llm_manager_instance

            def __call__(self, input_texts: chromadb.Documents) -> chromadb.Embeddings:
                return [self._llm_manager.get_embedding(text) for text in input_texts]

        return LLMManagerEmbeddingFunction(self.llm_manager)

    def get_collection_safe(self, name: str) -> Optional[chromadb.Collection]:
        """Safely get or create a collection, handling errors gracefully."""
        try:
            # Try to get existing collection
            try:
                return self.client.get_collection(name=name, embedding_function=self._get_embedding_function())
            except Exception:
                # If not found or error, try to create
                try:
                    return self.client.create_collection(name=name, embedding_function=self._get_embedding_function())
                except Exception as e:
                    self.logger.error(f"Failed to create collection '{name}': {e}")
                    return None
        except Exception as e:
            self.logger.error(f"Error accessing collection '{name}': {e}")
            return None

    def get_collection(self, name: str) -> chromadb.Collection:
        """DEPRECATED: Use get_collection_safe instead for robust error handling."""
        self.logger.warning("get_collection is deprecated. Use get_collection_safe instead.")
        return self.get_collection_safe(name)

    def add_memory(self, content: str, collection_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Adds a memory to the specified collection, automatically adding a timestamp."""
        if not content:
            raise ValueError("Content cannot be empty.")

        collection = self.get_collection_safe(collection_name)
        if not collection:
            self.logger.error(f"Could not get or create collection '{collection_name}'")
            return ""

        doc_id = str(uuid.uuid4())
        final_metadata = metadata or {}
        if "timestamp" not in final_metadata:
            final_metadata["timestamp"] = time.time()

        collection.add(
            documents=[content],
            metadatas=[final_metadata],
            ids=[doc_id],
        )
        self.logger.info(f"Added memory to '{collection_name}' with ID: {doc_id}")
        return doc_id

    def search_memories(self, query: str, collection_name: Optional[str] = None, n_results: int = 10) -> List[Dict[str, Any]]:
        """Searches for memories matching a query across one or all collections."""
        self.logger.info(f"Searching for memories matching '{query}' in collection '{collection_name or 'all'}'")
        start_time = time.perf_counter()

        try:
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                self.logger.error("Could not generate embedding for query.")
                return []

            collections_to_search = []
            if collection_name:
                collection = self.get_collection_safe(collection_name)
                if collection:
                    collections_to_search.append(collection)
            else:
                db_collections = self.client.list_collections()
                for coll in db_collections:
                    collection = self.get_collection_safe(coll.name)
                    if collection:
                        collections_to_search.append(collection)

            all_results = []
            for collection in collections_to_search:
                count = collection.count()
                if count == 0:
                    continue

                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(n_results, count),
                    include=["metadatas", "documents", "distances"],
                )

                ids = results.get("ids", [[]])[0]
                docs = results.get("documents", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]

                for i in range(len(ids)):
                    all_results.append({
                        "id": ids[i],
                        "content": docs[i],
                        "metadata": metadatas[i] if metadatas else {},
                        "distance": distances[i],
                        "collection": collection.name,
                    })

            sorted_results = sorted(all_results, key=lambda x: x["distance"])
            self.logger.info(f"Found {len(sorted_results)} memories for query: '{query[:50]}...'")
            return sorted_results[:n_results]

        except Exception as e:
            self.logger.error(f"Error searching memories: {e}")
            return []
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            metrics_manager_instance.record_memory_search_latency(duration)
            self.logger.info(f"Memory search completed in {duration:.4f} seconds.")

    def get_memory(self, collection_name: str, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific memory by its ID from a specific collection."""
        try:
            collection = self.client.get_collection(name=collection_name, embedding_function=self._get_embedding_function())
            return collection.get(ids=[memory_id])
        except Exception as e:
            self.logger.error(f"Failed to get memory '{memory_id}' from '{collection_name}': {e}", exc_info=True)
            return None
