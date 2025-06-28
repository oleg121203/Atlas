"""ChromaDB Manager for Atlas Memory System."""

import logging
from typing import Any, Dict, List, Optional

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not installed. Memory system functionality will be limited.")


class ChromaDBManager:
    """Manages interactions with ChromaDB for vector storage and retrieval."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDBManager with a persistence directory.

        Args:
            persist_directory (str): Directory to persist the ChromaDB data.
        """
        self.persist_directory = persist_directory
        self.client = None
        self._collections: Dict[str, Any] = {}
        if CHROMADB_AVAILABLE:
            try:
                self.client = chromadb.PersistentClient(path=self.persist_directory)
            except Exception as e:
                logging.error(f"Failed to initialize ChromaDB client: {e}")
                self.client = None
        else:
            logging.error("ChromaDB is not available. Initialization skipped.")

    def initialize(self) -> None:
        """Initialize the ChromaDB client with configured settings."""
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return

        try:
            logging.info("ChromaDB client initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize ChromaDB client: {e}")
            self.client = None

    def create_collection(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a new collection in ChromaDB.

        Args:
            name: The name of the collection to create.
            metadata: Optional metadata for the collection.

        Returns:
            bool: True if creation was successful, False otherwise.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return False

        try:
            collection = self.client.create_collection(name=name, metadata=metadata)
            self._collections[name] = collection
            logging.info(f"Created collection: {name}")
            return True
        except Exception as e:
            logging.error(f"Failed to create collection {name}: {e}")
            return False

    def delete_collection(self, name: str) -> bool:
        """Delete a collection from ChromaDB.

        Args:
            name: The name of the collection to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return False

        try:
            self.client.delete_collection(name=name)
            if name in self._collections:
                del self._collections[name]
            logging.info(f"Deleted collection: {name}")
            return True
        except Exception as e:
            logging.error(f"Failed to delete collection {name}: {e}")
            return False

    def add_to_collection(
        self,
        collection_name: str,
        vectors: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[str]] = None,
    ) -> bool:
        """Add vectors and associated data to a collection.

        Args:
            collection_name: The name of the collection to add to.
            vectors: List of vector embeddings to add.
            ids: List of unique IDs for the items.
            metadatas: Optional list of metadata dictionaries for the items.
            documents: Optional list of document strings associated with the vectors.

        Returns:
            bool: True if addition was successful, False otherwise.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return False

        if collection_name not in self._collections:
            logging.error(
                f"Collection {collection_name} not initialized."
            )
            return False

        try:
            collection = self._collections[collection_name]
            collection.add(
                embeddings=vectors, ids=ids, metadatas=metadatas, documents=documents
            )
            logging.info(f"Added {len(ids)} items to collection: {collection_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to add items to collection {collection_name}: {e}")
            return False

    def update_item(
        self,
        collection_name: str,
        item_id: str,
        vector: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        document: Optional[str] = None
    ) -> bool:
        """Update an existing item in a collection.

        Args:
            collection_name: The name of the collection containing the item.
            item_id: The ID of the item to update.
            vector: Optional updated vector embedding.
            metadata: Optional updated metadata dictionary.
            document: Optional updated document string.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return False

        if collection_name not in self._collections:
            logging.error(
                f"Collection {collection_name} not initialized."
            )
            return False

        try:
            collection = self._collections[collection_name]
            update_dict = {}
            if vector is not None:
                update_dict['embeddings'] = [vector]
            if metadata is not None:
                update_dict['metadatas'] = [metadata]
            if document is not None:
                update_dict['documents'] = [document]

            if update_dict:
                collection.update(ids=[item_id], **update_dict)
                logging.info(f"Updated item {item_id} in collection: {collection_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to update item {item_id} in collection {collection_name}: {e}")
            return False

    def delete_item(self, collection_name: str, item_id: str) -> bool:
        """Delete an item from a collection.

        Args:
            collection_name: The name of the collection containing the item.
            item_id: The ID of the item to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return False

        if collection_name not in self._collections:
            logging.error(
                f"Collection {collection_name} not initialized."
            )
            return False

        try:
            collection = self._collections[collection_name]
            collection.delete(ids=[item_id])
            logging.info(f"Deleted item {item_id} from collection: {collection_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to delete item {item_id} from collection {collection_name}: {e}")
            return False

    def get_collection(self, name: str) -> Optional[Any]:
        """Get a collection by name, creating it if it doesn't exist.

        Args:
            name (str): Name of the collection to retrieve or create.

        Returns:
            Optional[Any]: The collection if it exists, None otherwise.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return None

        try:
            if name not in self._collections:
                self._collections[name] = self.client.get_collection(name=name)
            return self._collections[name]
        except Exception as e:
            logging.error(f"Failed to get collection {name}: {e}")
            return None

    def query_collection(
        self,
        collection_name: str,
        query_vectors: Optional[List[List[float]]] = None,
        query_texts: Optional[List[str]] = None,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query a collection for similar items.

        Args:
            collection_name: The name of the collection to query.
            query_vectors: Optional list of vector embeddings to query with.
            query_texts: Optional list of text strings to query with.
            n_results: Number of results to return.
            where: Optional metadata filter for the query.
            where_document: Optional document content filter for the query.

        Returns:
            Dict[str, Any]: Query results including IDs, distances, metadatas, and documents.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return {}

        if collection_name not in self._collections:
            logging.error(
                f"Collection {collection_name} not initialized."
            )
            return {}

        try:
            collection = self._collections[collection_name]
            if query_vectors is not None:
                results = collection.query(
                    query_embeddings=query_vectors,
                    n_results=n_results,
                    where=where,
                    where_document=where_document,
                    include=["metadatas", "documents", "distances"]
                )
            elif query_texts is not None:
                results = collection.query(
                    query_texts=query_texts,
                    n_results=n_results,
                    where=where,
                    where_document=where_document,
                    include=["metadatas", "documents", "distances"]
                )
            else:
                logging.error("Either query_vectors or query_texts must be provided.")
                return {}

            logging.info(f"Queried collection {collection_name} with {n_results} results.")
            return results
        except Exception as e:
            logging.error(f"Failed to query collection {collection_name}: {e}")
            return {}

    def update_collection_metadata(self, collection_name: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a collection.

        Args:
            collection_name: The name of the collection to update.
            metadata: The new metadata dictionary for the collection.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return False

        if collection_name not in self._collections:
            logging.error(
                f"Collection {collection_name} not initialized."
            )
            return False

        try:
            collection = self._collections[collection_name]
            collection.modify(metadata=metadata)
            logging.info(f"Updated metadata for collection: {collection_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to update metadata for collection {collection_name}: {e}")
            return False

    def get_collection_metadata(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a collection.

        Args:
            collection_name: The name of the collection to retrieve metadata for.

        Returns:
            Optional[Dict[str, Any]]: The metadata dictionary if the collection exists, None otherwise.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return None

        if collection_name not in self._collections:
            logging.error(
                f"Collection {collection_name} not initialized."
            )
            return None

        try:
            collection = self._collections[collection_name]
            return collection.metadata
        except Exception as e:
            logging.error(f"Failed to get metadata for collection {collection_name}: {e}")
            return None

    def persist(self) -> bool:
        """Persist the current state of the ChromaDB to disk.

        Returns:
            bool: True if persistence was successful, False otherwise.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return False

        try:
            self.client.persist()
            logging.info("ChromaDB state persisted to disk.")
            return True
        except Exception as e:
            logging.error(f"Failed to persist ChromaDB state: {e}")
            return False

    def reset(self) -> bool:
        """Reset the ChromaDB client, clearing all collections.

        Returns:
            bool: True if reset was successful, False otherwise.
        """
        if not CHROMADB_AVAILABLE or self.client is None:
            logging.error("ChromaDB client not initialized.")
            return False

        try:
            self.client.reset()
            self._collections.clear()
            logging.info("ChromaDB client reset, all collections cleared.")
            return True
        except Exception as e:
            logging.error(f"Failed to reset ChromaDB client: {e}")
            return False
