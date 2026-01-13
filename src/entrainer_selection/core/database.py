"""
Database Connection Management
==============================

Provides connection managers for Neo4j and ChromaDB with proper lifecycle management.

Usage:
    from entrainer_selection.core.database import Neo4jConnection, ChromaDBConnection

    # Context manager usage (recommended)
    with Neo4jConnection() as neo4j:
        result = neo4j.run_query("MATCH (n) RETURN n LIMIT 10")

    # Or use the singleton pattern
    neo4j = Neo4jConnection.get_instance()
"""

from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from neo4j import GraphDatabase, Driver, Session
from loguru import logger

from entrainer_selection.core.config import get_settings


class Neo4jConnection:
    """
    Neo4j database connection manager.

    Supports both context manager and singleton patterns.
    Thread-safe connection pooling is handled by the Neo4j driver.
    """

    _instance: Optional["Neo4jConnection"] = None
    _driver: Optional[Driver] = None

    def __init__(self):
        """Initialize Neo4j connection from settings."""
        settings = get_settings()
        self._uri = settings.databases.neo4j.uri
        self._database = settings.databases.neo4j.database
        self._username = settings.neo4j_username
        self._password = settings.neo4j_password
        self._max_pool_size = settings.databases.neo4j.max_connection_pool_size
        self._timeout = settings.databases.neo4j.connection_timeout

    @classmethod
    def get_instance(cls) -> "Neo4jConnection":
        """Get singleton instance of Neo4j connection."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._connect()
        return cls._instance

    def _connect(self) -> None:
        """Establish connection to Neo4j."""
        if self._driver is None:
            logger.info(f"Connecting to Neo4j at {self._uri}")
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._username, self._password),
                max_connection_pool_size=self._max_pool_size,
                connection_timeout=self._timeout,
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info("Neo4j connection established")

    def close(self) -> None:
        """Close the Neo4j connection."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")

    def __enter__(self) -> "Neo4jConnection":
        """Context manager entry."""
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Get a Neo4j session as a context manager."""
        if self._driver is None:
            self._connect()
        session = self._driver.session(database=self._database)
        try:
            yield session
        finally:
            session.close()

    def run_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records as dictionaries
        """
        with self.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def run_write_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a write query within a transaction.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Query summary statistics
        """
        with self.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(query, parameters or {}).consume()
            )
            return {
                "nodes_created": result.counters.nodes_created,
                "relationships_created": result.counters.relationships_created,
                "properties_set": result.counters.properties_set,
            }

    def health_check(self) -> bool:
        """Check if Neo4j connection is healthy."""
        try:
            with self.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False


class ChromaDBConnection:
    """
    ChromaDB vector database connection manager.

    Provides persistent storage for molecular embeddings and similarity search.
    """

    _instance: Optional["ChromaDBConnection"] = None
    _client = None
    _collection = None

    def __init__(self):
        """Initialize ChromaDB connection from settings."""
        settings = get_settings()
        self._persist_directory = settings.databases.chromadb.persist_directory
        self._collection_name = settings.databases.chromadb.collection_name
        self._embedding_model = settings.databases.chromadb.embedding_model

    @classmethod
    def get_instance(cls) -> "ChromaDBConnection":
        """Get singleton instance of ChromaDB connection."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._connect()
        return cls._instance

    def _connect(self) -> None:
        """Establish connection to ChromaDB."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            logger.info(f"Connecting to ChromaDB at {self._persist_directory}")
            self._client = chromadb.PersistentClient(
                path=self._persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            logger.info("ChromaDB connection established")

    def get_or_create_collection(self, collection_name: Optional[str] = None):
        """
        Get or create a ChromaDB collection.

        Args:
            collection_name: Collection name (uses default if not provided)

        Returns:
            ChromaDB collection
        """
        if self._client is None:
            self._connect()

        name = collection_name or self._collection_name
        return self._client.get_or_create_collection(name=name)

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        collection_name: Optional[str] = None,
    ) -> None:
        """
        Add documents to a collection.

        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
            collection_name: Target collection name
        """
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info(f"Added {len(documents)} documents to {collection_name or self._collection_name}")

    def query(
        self,
        query_texts: List[str],
        n_results: int = 10,
        collection_name: Optional[str] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query the collection for similar documents.

        Args:
            query_texts: List of query strings
            n_results: Number of results to return
            collection_name: Collection to query
            where: Optional filter conditions

        Returns:
            Query results with documents, distances, and metadata
        """
        collection = self.get_or_create_collection(collection_name)
        return collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
        )

    def close(self) -> None:
        """Close ChromaDB connection (persists automatically)."""
        self._client = None
        self._collection = None
        logger.info("ChromaDB connection closed")

    def __enter__(self) -> "ChromaDBConnection":
        """Context manager entry."""
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    def health_check(self) -> bool:
        """Check if ChromaDB connection is healthy."""
        try:
            if self._client is None:
                self._connect()
            self._client.heartbeat()
            return True
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False
