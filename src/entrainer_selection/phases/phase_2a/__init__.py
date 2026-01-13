"""
Phase II-A: Graph-RAG Engine
============================

Literature-grounded selection using Graph-RAG architecture:
- Neo4j for knowledge graph storage
- ChromaDB for vector embeddings
- Gemini LLM for reasoning and extraction

Key Components:
- GraphRAGEngine: Main orchestrator
- KnowledgeGraphBuilder: Neo4j graph construction
- DocumentProcessor: Literature chunking and embedding
- SafetyVerifier: GHS data verification (CRITICAL FIX: Use PubChem API, not just LLM)

CRITICAL FIX Applied:
- Safety data is verified against PubChem PUG REST API
- LLM extraction is used only as fallback for unstructured text
- Context-aware property storage: (Molecule)-[:HAS_PROPERTY {context}]->(Property)

Output:
- Literature-grounded candidate molecules
- Safety profiles with verified GHS data
"""

__all__ = []

