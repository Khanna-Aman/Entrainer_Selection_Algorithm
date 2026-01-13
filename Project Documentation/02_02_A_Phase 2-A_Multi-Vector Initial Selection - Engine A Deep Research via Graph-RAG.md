# 🎯 Phase II-A Implementation: Multi-Vector Initial Selection - Engine A


## Recommended Approach

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENGINE A: Graph-RAG System                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐  │
│  │ Document    │───▶│ Chunking &  │───▶│ ChromaDB                │  │
│  │ Corpus      │    │ Embedding   │    │ (Vector Store)          │  │
│  │ (Papers,    │    │             │    │                         │  │
│  │  Patents)   │    │             │    └───────────┬─────────────┘  │
│  └─────────────┘    └─────────────┘                │                │
│                                                     │ Semantic       │
│  ┌─────────────┐    ┌─────────────┐                │ Retrieval      │
│  │ Molecule    │───▶│ Property    │                ▼                │
│  │ Database    │    │ Extraction  │    ┌─────────────────────────┐  │
│  │ (PubChem)   │    │ (RDKit)     │───▶│ Neo4j Graph Database    │  │
│  └─────────────┘    └─────────────┘    │                         │  │
│                                         │ Nodes: Molecules,       │  │
│                                         │        Papers,          │  │
│                                         │        Authors,         │  │
│                                         │        Properties       │  │
│                                         │                         │  │
│                                         │ Edges: MENTIONED_IN,    │  │
│                                         │        SIMILAR_TO,      │  │
│                                         │        HAS_PROPERTY     │  │
│                                         └───────────┬─────────────┘  │
│                                                     │                │
│                                                     │ Graph          │
│                                                     │ Context        │
│                                                     ▼                │
│                                         ┌─────────────────────────┐  │
│                                         │ Gemini 1.5/2.0 Pro      │  │
│                                         │ (Reasoning Engine)      │  │
│                                         │                         │  │
│                                         │ Iterative Selection     │  │
│                                         │ with Citations          │  │
│                                         └───────────┬─────────────┘  │
│                                                     │                │
│                                                     ▼                │
│                                         ┌─────────────────────────┐  │
│                                         │ Output: 25-50 Molecules │  │
│                                         │ + Selection Rationale   │  │
│                                         └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation Strategy: Three-Layer Graph-RAG

Given your 32GB RAM constraint, I recommend a **lightweight Graph-RAG** architecture:

| Layer | Tool | Purpose | Memory Estimate |
|-------|------|---------|-----------------|
| Vector Store | ChromaDB | Semantic search over paper chunks | ~2-4GB for 10K documents |
| Graph Store | Neo4j Community | Relationship traversal | ~2-4GB for 100K molecules |
| LLM Reasoning | Gemini API | Grounded inference | API-based (no local memory) |

---

## Sub-Phase II-A.1: Document Corpus Preparation

### Data Sources for Literature

| Source | Access Method | Content Type | Notes |
|--------|---------------|--------------|-------|
| Semantic Scholar | API (free tier) | Paper metadata, abstracts | https://api.semanticscholar.org/ |
| PubMed/PMC | Entrez API | Biomedical papers | https://www.ncbi.nlm.nih.gov/home/develop/api/ |
| arXiv | API/Bulk | Preprints | https://arxiv.org/help/api |
| Google Patents | BigQuery Public Dataset | Patents | Requires Google Cloud account |
| ChemRxiv | Manual download | Chemistry preprints | https://chemrxiv.org/ |

**⚠️ Important Limitation:** Full-text access to many papers requires institutional subscriptions. Your corpus may be limited to:
- Abstracts (widely available)
- Open Access papers
- Preprints (arXiv, ChemRxiv)
- Patents (public)

### Document Acquisition Strategy

```python
# src/corpus/semantic_scholar_client.py
"""
Phase II-A.1: Academic Paper Retrieval from Semantic Scholar
Reference: https://api.semanticscholar.org/api-docs/
"""

import requests
import time
from dataclasses import dataclass
from typing import List, Optional
import json
from pathlib import Path

@dataclass
class Paper:
    """Representation of an academic paper"""
    paper_id: str
    title: str
    abstract: Optional[str]
    year: Optional[int]
    authors: List[str]
    venue: Optional[str]
    citation_count: int
    doi: Optional[str]
    fields_of_study: List[str]
    
    def to_dict(self) -> dict:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "abstract": self.abstract,
            "year": self.year,
            "authors": self.authors,
            "venue": self.venue,
            "citation_count": self.citation_count,
            "doi": self.doi,
            "fields_of_study": self.fields_of_study
        }

class SemanticScholarClient:
    """
    Client for Semantic Scholar Academic Graph API
    
    Rate Limits (as of knowledge cutoff):
    - Without API key: 100 requests per 5 minutes
    - With API key: Higher limits available
    
    [VERIFY CURRENT LIMITS: https://api.semanticscholar.org/api-docs/]
    """
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.session = requests.Session()
        if api_key:
            self.session.headers["x-api-key"] = api_key
        self.request_count = 0
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement conservative rate limiting"""
        # Conservative: 1 request per second without API key
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self.last_request_time = time.time()
        self.request_count += 1
    
    def search_papers(
        self, 
        query: str, 
        limit: int = 100,
        fields: Optional[List[str]] = None
    ) -> List[Paper]:
        """
        Search for papers matching a query
        
        Args:
            query: Search query string
            limit: Maximum number of results (API max typically 100 per request)
            fields: Paper fields to return
        
        Returns:
            List of Paper objects
        """
        if fields is None:
            fields = [
                "paperId", "title", "abstract", "year", 
                "authors", "venue", "citationCount", 
                "externalIds", "s2FieldsOfStudy"
            ]
        
        self._rate_limit()
        
        url = f"{self.BASE_URL}/paper/search"
        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": ",".join(fields)
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for item in data.get("data", []):
                paper = Paper(
                    paper_id=item.get("paperId", ""),
                    title=item.get("title", ""),
                    abstract=item.get("abstract"),
                    year=item.get("year"),
                    authors=[a.get("name", "") for a in item.get("authors", [])],
                    venue=item.get("venue"),
                    citation_count=item.get("citationCount", 0),
                    doi=item.get("externalIds", {}).get("DOI"),
                    fields_of_study=[
                        f.get("category", "") 
                        for f in item.get("s2FieldsOfStudy", [])
                    ]
                )
                papers.append(paper)
            
            return papers
            
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return []

def build_ethanol_water_corpus(
    client: SemanticScholarClient,
    output_dir: Path,
    max_papers: int = 500
) -> List[Paper]:
    """
    Build corpus of papers relevant to ethanol-water separation
    
    Search Strategy:
    1. Direct topic searches
    2. Key author searches (if known)
    3. Citation expansion from seminal papers
    """
    
    all_papers = []
    seen_ids = set()
    
    # Define search queries based on Phase I literature review
    search_queries = [
        "ethanol water separation extractive distillation",
        "azeotrope breaking entrainer selection",
        "ethanol dehydration solvent",
        "glycol entrainer distillation",
        "ionic liquid ethanol water separation",
        "deep eutectic solvent alcohol separation",
        "molecular simulation ethanol water",
        "UNIFAC ethanol water prediction",
        "green solvent separation process",
        "inherent safety solvent selection",
    ]
    
    for query in search_queries:
        print(f"Searching: '{query}'...")
        papers = client.search_papers(query, limit=100)
        
        for paper in papers:
            if paper.paper_id not in seen_ids:
                all_papers.append(paper)
                seen_ids.add(paper.paper_id)
        
        print(f"  Found {len(papers)} papers, {len(all_papers)} total unique")
        
        if len(all_papers) >= max_papers:
            break
    
    # Save corpus
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "paper_corpus.json"
    
    with open(output_file, 'w') as f:
        json.dump(
            [p.to_dict() for p in all_papers], 
            f, 
            indent=2
        )
    
    print(f"\nSaved {len(all_papers)} papers to {output_file}")
    return all_papers


if __name__ == "__main__":
    # Example usage
    client = SemanticScholarClient()  # Add API key if available
    
    output_dir = Path("data/corpus")
    papers = build_ethanol_water_corpus(client, output_dir, max_papers=500)
    
    # Print sample
    print("\nSample papers:")
    for paper in papers[:5]:
        print(f"  - {paper.title} ({paper.year})")
```

---

## Sub-Phase II-A.2: Chunking & Embedding Pipeline

### Text Chunking Strategy

For scientific papers, standard chunking can break mid-sentence or mid-concept. I recommend **semantic chunking**:

```python
# src/corpus/chunking.py
"""
Phase II-A.2: Document Chunking for RAG
"""

from dataclasses import dataclass
from typing import List, Optional
import re

@dataclass
class TextChunk:
    """A chunk of text with metadata"""
    chunk_id: str
    source_id: str  # Paper ID or document ID
    text: str
    chunk_type: str  # "abstract", "introduction", "methodology", etc.
    metadata: dict

def chunk_abstract(paper_id: str, abstract: str, max_tokens: int = 500) -> List[TextChunk]:
    """
    Chunk an abstract into semantic units
    
    For abstracts, we typically keep them whole (usually < 500 tokens)
    but split if necessary at sentence boundaries.
    """
    if not abstract:
        return []
    
    # Simple sentence splitting (for production, use spaCy or similar)
    sentences = re.split(r'(?<=[.!?])\s+', abstract)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    # Rough token estimate: 1 token ≈ 4 characters
    for sentence in sentences:
        sentence_tokens = len(sentence) // 4
        
        if current_length + sentence_tokens > max_tokens and current_chunk:
            # Save current chunk
            chunk_text = " ".join(current_chunk)
            chunks.append(TextChunk(
                chunk_id=f"{paper_id}_abstract_{len(chunks)}",
                source_id=paper_id,
                text=chunk_text,
                chunk_type="abstract",
                metadata={"position": len(chunks)}
            ))
            current_chunk = [sentence]
            current_length = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_length += sentence_tokens
    
    # Don't forget the last chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append(TextChunk(
            chunk_id=f"{paper_id}_abstract_{len(chunks)}",
            source_id=paper_id,
            text=chunk_text,
            chunk_type="abstract",
            metadata={"position": len(chunks)}
        ))
    
    return chunks


def create_molecule_context_chunk(
    molecule_name: str,
    smiles: str,
    paper_mentions: List[dict],
    properties: dict
) -> TextChunk:
    """
    Create a context-rich chunk for a molecule that combines
    structural info with literature mentions.
    
    This creates a "molecule card" that can be retrieved and 
    fed to the LLM with full context.
    """
    
    # Build context string
    context_parts = [
        f"Molecule: {molecule_name}",
        f"SMILES: {smiles}",
        "",
        "Properties:",
    ]
    
    for prop, value in properties.items():
        context_parts.append(f"  - {prop}: {value}")
    
    if paper_mentions:
        context_parts.append("")
        context_parts.append("Literature Mentions:")
        for mention in paper_mentions[:5]:  # Limit to top 5
            context_parts.append(
                f"  - {mention.get('paper_title', 'Unknown')} "
                f"({mention.get('year', 'N/A')}): "
                f"\"{mention.get('context', 'No context')}\""
            )
    
    return TextChunk(
        chunk_id=f"molecule_{smiles}",
        source_id=smiles,
        text="\n".join(context_parts),
        chunk_type="molecule_card",
        metadata={
            "molecule_name": molecule_name,
            "smiles": smiles,
            "properties": properties
        }
    )
```

### Embedding with ChromaDB

```python
# src/vectorstore/chroma_store.py
"""
Phase II-A.2: ChromaDB Vector Store Setup

Reference: https://docs.trychroma.com/
[VERIFY: Check current ChromaDB API as it evolves rapidly]
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path
import json

class MoleculeRAGVectorStore:
    """
    ChromaDB-based vector store for Graph-RAG system
    
    Collections:
    1. paper_chunks - Academic paper text chunks
    2. molecule_cards - Molecule context summaries
    3. patent_chunks - Patent text chunks (if available)
    """
    
    def __init__(self, persist_directory: str = "./data/chromadb"):
        """
        Initialize ChromaDB client with persistence
        
        Args:
            persist_directory: Where to store the database
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize persistent client
        # [VERIFY: ChromaDB API may have changed - check docs]
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Create or get collections
        # Using default embedding function (all-MiniLM-L6-v2)
        # For chemistry-specific embeddings, consider:
        # - ChemBERTa (if available as sentence transformer)
        # - SciBERT
        # [NEEDS VERIFICATION: Best embedding model for chemistry text]
        
        self.paper_collection = self.client.get_or_create_collection(
            name="paper_chunks",
            metadata={"description": "Academic paper text chunks"}
        )
        
        self.molecule_collection = self.client.get_or_create_collection(
            name="molecule_cards",
            metadata={"description": "Molecule context summaries"}
        )
    
    def add_paper_chunks(
        self, 
        chunks: List[Dict],
        batch_size: int = 100
    ) -> int:
        """
        Add paper chunks to the vector store
        
        Args:
            chunks: List of dicts with keys: chunk_id, text, metadata
            batch_size: Batch size for insertion
            
        Returns:
            Number of chunks added
        """
        total_added = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            self.paper_collection.add(
                ids=[c["chunk_id"] for c in batch],
                documents=[c["text"] for c in batch],
                metadatas=[c.get("metadata", {}) for c in batch]
            )
            
            total_added += len(batch)
            print(f"Added {total_added}/{len(chunks)} chunks")
        
        return total_added
    
    def add_molecule_cards(
        self,
        molecules: List[Dict],
        batch_size: int = 100
    ) -> int:
        """
        Add molecule context cards to vector store
        
        Args:
            molecules: List of dicts with keys: smiles, text, metadata
        """
        total_added = 0
        
        for i in range(0, len(molecules), batch_size):
            batch = molecules[i:i + batch_size]
            
            self.molecule_collection.add(
                ids=[m["smiles"] for m in batch],
                documents=[m["text"] for m in batch],
                metadatas=[m.get("metadata", {}) for m in batch]
            )
            
            total_added += len(batch)
        
        return total_added
    
    def search_papers(
        self,
        query: str,
        n_results: int = 10,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Semantic search over paper chunks
        
        Args:
            query: Natural language query
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            List of matching chunks with distances
        """
        results = self.paper_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        # Format results
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None
            })
        
        return formatted
    
    def search_molecules(
        self,
        query: str,
        n_results: int = 10
    ) -> List[Dict]:
        """Semantic search over molecule cards"""
        results = self.molecule_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "smiles": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None
            })
        
        return formatted
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collections"""
        return {
            "paper_chunks": self.paper_collection.count(),
            "molecule_cards": self.molecule_collection.count()
        }


if __name__ == "__main__":
    # Example usage
    store = MoleculeRAGVectorStore()
    
    # Add sample paper chunk
    sample_chunks = [
        {
            "chunk_id": "paper_001_abstract_0",
            "text": "This study investigates ethylene glycol as an entrainer for ethanol-water separation. We found that the relative volatility increases significantly when using glycol concentrations above 50 mol%.",
            "metadata": {
                "paper_id": "paper_001",
                "year": 2020,
                "chunk_type": "abstract"
            }
        }
    ]
    
    store.add_paper_chunks(sample_chunks)
    
    # Search
    results = store.search_papers("glycol entrainer effectiveness")
    print(f"Found {len(results)} results")
    for r in results:
        print(f"  - {r['chunk_id']}: {r['text'][:100]}...")
```

---

## Sub-Phase II-A.3: Neo4j Graph Schema Design

### Graph Schema for Molecule-Literature Knowledge Graph

```cypher
// Neo4j Schema for Ethanol-Water Separation Graph-RAG
// Run these in Neo4j Browser to create constraints and indexes

// ============================================
// NODE TYPES
// ============================================

// Molecules - Central entity
// Properties: smiles (unique), name, molecular_weight, cluster_id, etc.
CREATE CONSTRAINT molecule_smiles IF NOT EXISTS
FOR (m:Molecule) REQUIRE m.smiles IS UNIQUE;

// Papers - Academic literature
CREATE CONSTRAINT paper_id IF NOT EXISTS
FOR (p:Paper) REQUIRE p.paper_id IS UNIQUE;

// Authors
CREATE CONSTRAINT author_id IF NOT EXISTS
FOR (a:Author) REQUIRE a.author_id IS UNIQUE;

// Properties - Molecular properties as separate nodes for querying
// (Allows queries like "find all molecules with boiling point > 150")
CREATE CONSTRAINT property_id IF NOT EXISTS
FOR (prop:Property) REQUIRE prop.property_id IS UNIQUE;

// Clusters - From Phase I
CREATE CONSTRAINT cluster_id IF NOT EXISTS
FOR (c:Cluster) REQUIRE c.cluster_id IS UNIQUE;

// Mechanism - Separation mechanisms
CREATE CONSTRAINT mechanism_name IF NOT EXISTS
FOR (mech:Mechanism) REQUIRE mech.name IS UNIQUE;

// ============================================
// RELATIONSHIP TYPES
// ============================================

// Molecule relationships:
// (Molecule)-[:MENTIONED_IN {context: "...", sentiment: "positive/negative/neutral"}]->(Paper)
// (Molecule)-[:SIMILAR_TO {tanimoto: 0.85}]->(Molecule)
// (Molecule)-[:HAS_PROPERTY {value: 150, unit: "°C"}]->(Property)
// (Molecule)-[:BELONGS_TO]->(Cluster)
// (Molecule)-[:USES_MECHANISM]->(Mechanism)

// Paper relationships:
// (Paper)-[:AUTHORED_BY]->(Author)
// (Paper)-[:CITES]->(Paper)
// (Author)-[:CO_AUTHORED_WITH]->(Author)

// ============================================
// INDEXES for performance
// ============================================

CREATE INDEX molecule_name IF NOT EXISTS
FOR (m:Molecule) ON (m.name);

CREATE INDEX molecule_mw IF NOT EXISTS
FOR (m:Molecule) ON (m.molecular_weight);

CREATE INDEX paper_year IF NOT EXISTS
FOR (p:Paper) ON (p.year);

CREATE INDEX cluster_mechanism IF NOT EXISTS
FOR (c:Cluster) ON (c.mechanism);
```

### Neo4j Python Integration

```python
# src/graphdb/neo4j_client.py
"""
Phase II-A.3: Neo4j Graph Database Client

Reference: https://neo4j.com/docs/python-manual/current/
"""

from neo4j import GraphDatabase
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import os

@dataclass
class MoleculeNode:
    """Molecule representation for graph storage"""
    smiles: str
    name: str
    molecular_weight: float
    cluster_id: str
    properties: Dict[str, Any]

@dataclass  
class PaperNode:
    """Paper representation for graph storage"""
    paper_id: str
    title: str
    year: int
    abstract: Optional[str]
    authors: List[str]

class MoleculeGraphDB:
    """
    Neo4j client for the molecule-literature knowledge graph
    
    Setup Instructions:
    1. Install Neo4j Community Edition: https://neo4j.com/download/
    2. Start Neo4j (default: bolt://localhost:7687)
    3. Set environment variables:
       - NEO4J_URI=bolt://localhost:7687
       - NEO4J_USER=neo4j
       - NEO4J_PASSWORD=your_password
    """
    
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
    
    def close(self):
        self.driver.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ==========================================
    # CREATE Operations
    # ==========================================
    
    def create_molecule(self, molecule: MoleculeNode) -> bool:
        """Create or update a molecule node"""
        query = """
        MERGE (m:Molecule {smiles: $smiles})
        SET m.name = $name,
            m.molecular_weight = $molecular_weight,
            m.cluster_id = $cluster_id,
            m.properties = $properties,
            m.updated_at = datetime()
        RETURN m
        """
        
        with self.driver.session() as session:
            result = session.run(
                query,
                smiles=molecule.smiles,
                name=molecule.name,
                molecular_weight=molecule.molecular_weight,
                cluster_id=molecule.cluster_id,
                properties=molecule.properties
            )
            return result.single() is not None
    
    def create_paper(self, paper: PaperNode) -> bool:
        """Create or update a paper node"""
        query = """
        MERGE (p:Paper {paper_id: $paper_id})
        SET p.title = $title,
            p.year = $year,
            p.abstract = $abstract,
            p.updated_at = datetime()
        WITH p
        UNWIND $authors as author_name
        MERGE (a:Author {name: author_name})
        MERGE (p)-[:AUTHORED_BY]->(a)
        RETURN p
        """
        
        with self.driver.session() as session:
            result = session.run(
                query,
                paper_id=paper.paper_id,
                title=paper.title,
                year=paper.year,
                abstract=paper.abstract,
                authors=paper.authors
            )
            return result.single() is not None
    
    def link_molecule_to_paper(
        self,
        smiles: str,
        paper_id: str,
        context: str,
        sentiment: str = "neutral"
    ) -> bool:
        """
        Create MENTIONED_IN relationship between molecule and paper
        
        Args:
            smiles: Molecule SMILES
            paper_id: Paper identifier
            context: The text context where molecule was mentioned
            sentiment: positive/negative/neutral assessment
        """
        query = """
        MATCH (m:Molecule {smiles: $smiles})
        MATCH (p:Paper {paper_id: $paper_id})
        MERGE (m)-[r:MENTIONED_IN]->(p)
        SET r.context = $context,
            r.sentiment = $sentiment,
            r.created_at = datetime()
        RETURN r
        """
        
        with self.driver.session() as session:
            result = session.run(
                query,
                smiles=smiles,
                paper_id=paper_id,
                context=context,
                sentiment=sentiment
            )
            return result.single() is not None
    
    def create_similarity_edge(
        self,
        smiles1: str,
        smiles2: str,
        tanimoto_similarity: float
    ) -> bool:
        """Create SIMILAR_TO relationship between molecules"""
        query = """
        MATCH (m1:Molecule {smiles: $smiles1})
        MATCH (m2:Molecule {smiles: $smiles2})
        MERGE (m1)-[r:SIMILAR_TO]->(m2)
        SET r.tanimoto = $similarity
        RETURN r
        """
        
        with self.driver.session() as session:
            result = session.run(
                query,
                smiles1=smiles1,
                smiles2=smiles2,
                similarity=tanimoto_similarity
            )
            return result.single() is not None
    
    # ==========================================
    # QUERY Operations for Graph-RAG
    # ==========================================
    
    def get_molecule_context(self, smiles: str) -> Dict:
        """
        Get full context for a molecule including:
        - Basic properties
        - All paper mentions
        - Similar molecules
        - Cluster information
        
        This is used to build the "graph context" for the LLM
        """
        query = """
        MATCH (m:Molecule {smiles: $smiles})
        OPTIONAL MATCH (m)-[mentioned:MENTIONED_IN]->(p:Paper)
        OPTIONAL MATCH (m)-[sim:SIMILAR_TO]->(neighbor:Molecule)
        OPTIONAL MATCH (m)-[:BELONGS_TO]->(c:Cluster)
        RETURN m,
               collect(DISTINCT {
                   paper_id: p.paper_id,
                   title: p.title,
                   year: p.year,
                   context: mentioned.context,
                   sentiment: mentioned.sentiment
               }) as papers,
               collect(DISTINCT {
                   smiles: neighbor.smiles,
                   name: neighbor.name,
                   similarity: sim.tanimoto
               }) as similar_molecules,
               c.cluster_id as cluster_id,
               c.mechanism as mechanism
        """
        
        with self.driver.session() as session:
            result = session.run(query, smiles=smiles)
            record = result.single()
            
            if not record:
                return {}
            
            molecule = record["m"]
            return {
                "smiles": molecule["smiles"],
                "name": molecule["name"],
                "molecular_weight": molecule["molecular_weight"],
                "properties": molecule.get("properties", {}),
                "paper_mentions": [p for p in record["papers"] if p["paper_id"]],
                "similar_molecules": [s for s in record["similar_molecules"] if s["smiles"]],
                "cluster_id": record["cluster_id"],
                "mechanism": record["mechanism"]
            }
    
    def find_molecules_by_mechanism(
        self,
        mechanism: str,
        limit: int = 50
    ) -> List[Dict]:
        """Find molecules that use a specific separation mechanism"""
        query = """
        MATCH (m:Molecule)-[:BELONGS_TO]->(c:Cluster)
        WHERE c.mechanism = $mechanism
        OPTIONAL MATCH (m)-[:MENTIONED_IN]->(p:Paper)
        WITH m, count(DISTINCT p) as paper_count
        ORDER BY paper_count DESC
        LIMIT $limit
        RETURN m.smiles as smiles,
               m.name as name,
               m.molecular_weight as mw,
               paper_count
        """
        
        with self.driver.session() as session:
            result = session.run(query, mechanism=mechanism, limit=limit)
            return [dict(record) for record in result]
    
    def get_cooccurrence_network(
        self,
        smiles: str,
        depth: int = 2
    ) -> List[Dict]:
        """
        Get molecules that co-occur with target in literature
        
        Args:
            smiles: Starting molecule
            depth: How many hops in the citation network
        """
        query = """
        MATCH (m:Molecule {smiles: $smiles})-[:MENTIONED_IN]->(p:Paper)
        MATCH (other:Molecule)-[:MENTIONED_IN]->(p)
        WHERE other.smiles <> $smiles
        WITH other, count(DISTINCT p) as shared_papers
        ORDER BY shared_papers DESC
        LIMIT 20
        RETURN other.smiles as smiles,
               other.name as name,
               shared_papers
        """
        
        with self.driver.session() as session:
            result = session.run(query, smiles=smiles)
            return [dict(record) for record in result]
    
    def get_graph_statistics(self) -> Dict:
        """Get overview statistics of the knowledge graph"""
        query = """
        MATCH (m:Molecule) WITH count(m) as molecule_count
        MATCH (p:Paper) WITH molecule_count, count(p) as paper_count
        MATCH ()-[r:MENTIONED_IN]->() WITH molecule_count, paper_count, count(r) as mention_count
        RETURN molecule_count, paper_count, mention_count
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            return dict(record) if record else {}


if __name__ == "__main__":
    # Test connection
    with MoleculeGraphDB() as db:
        stats = db.get_graph_statistics()
        print(f"Graph Statistics: {stats}")
```

---

## Sub-Phase II-A.4: Gemini-Powered Iterative Selection

### Iterative Research Workflow Design

This is the core "Deep Research" logic - an iterative loop where the LLM:
1. Receives graph context + vector search results
2. Reasons about molecule suitability
3. Requests additional information (next query)
4. Converges on final selection with citations

```python
# src/llm/gemini_research_engine.py
"""
Phase II-A.4: Gemini-Powered Iterative Molecule Selection

This implements the "Deep Research" workflow using:
1. ChromaDB for semantic retrieval
2. Neo4j for graph context
3. Gemini API for reasoning

[VERIFY: Check current Gemini API at https://ai.google.dev/]
"""

import google.generativeai as genai
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import json
import os
from pathlib import Path

# Import our modules (adjust paths as needed)
# from src.vectorstore.chroma_store import MoleculeRAGVectorStore
# from src.graphdb.neo4j_client import MoleculeGraphDB

@dataclass
class SelectionResult:
    """Result of molecule selection with full provenance"""
    smiles: str
    name: str
    selection_score: float  # 0-1 confidence
    rationale: str
    supporting_papers: List[str]
    mechanism: str
    safety_notes: List[str]
    iteration_selected: int

@dataclass
class ResearchSession:
    """Tracks the iterative research process"""
    session_id: str
    target_count: int = 50
    selected_molecules: List[SelectionResult] = field(default_factory=list)
    explored_clusters: List[str] = field(default_factory=list)
    iteration_history: List[Dict] = field(default_factory=list)
    
class GeminiResearchEngine:
    """
    Iterative research engine using Gemini for grounded molecule selection
    
    Setup:
    1. Set GOOGLE_API_KEY environment variable
    2. Ensure Neo4j is running with populated graph
    3. Ensure ChromaDB has paper/molecule embeddings
    
    [VERIFY: Current Gemini API structure - check https://ai.google.dev/]
    """
    
    SYSTEM_PROMPT = """You are a computational chemistry research assistant specializing in separation science. Your task is to identify promising entrainer molecules for ethanol-water extractive distillation.

CRITICAL RULES:
1. ONLY recommend molecules that are explicitly mentioned in the provided context
2. NEVER invent or hallucinate molecule names, SMILES, or properties
3. If you're uncertain about a molecule, say so explicitly
4. Always cite the source (paper ID or database) for each recommendation
5. Consider BOTH efficiency AND safety - flag any safety concerns

For each molecule you recommend, provide:
- SMILES (exactly as given in context)
- Name
- Why it's promising for ethanol-water separation
- Safety considerations (if mentioned)
- Supporting evidence (paper citations)
- Confidence level (high/medium/low)

If the provided context doesn't contain enough information to make recommendations, clearly state what additional information you need."""

    def __init__(
        self,
        vector_store,  # MoleculeRAGVectorStore instance
        graph_db,      # MoleculeGraphDB instance
        model_name: str = "gemini-1.5-pro"  # [VERIFY: Current model name]
    ):
        self.vector_store = vector_store
        self.graph_db = graph_db
        
        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        # [VERIFY: Current Gemini API initialization]
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self.SYSTEM_PROMPT
        )
    
    def _build_context(
        self,
        query: str,
        focus_cluster: Optional[str] = None,
        previous_selections: List[str] = None
    ) -> str:
        """
        Build comprehensive context for LLM from vector store and graph
        
        This is the "RAG" part - retrieving relevant context
        """
        context_parts = []
        
        # 1. Vector search for relevant paper chunks
        paper_results = self.vector_store.search_papers(query, n_results=10)
        
        if paper_results:
            context_parts.append("=== RELEVANT LITERATURE ===")
            for result in paper_results:
                context_parts.append(f"\n[Paper Chunk: {result['chunk_id']}]")
                context_parts.append(result['text'])
                if result.get('metadata', {}).get('year'):
                    context_parts.append(f"(Year: {result['metadata']['year']})")
        
        # 2. Vector search for relevant molecules
        molecule_results = self.vector_store.search_molecules(query, n_results=15)
        
        if molecule_results:
            context_parts.append("\n\n=== CANDIDATE MOLECULES ===")
            for mol in molecule_results:
                context_parts.append(f"\n{mol['text']}")
        
        # 3. If focus cluster specified, get graph context for that cluster
        if focus_cluster:
            cluster_molecules = self.graph_db.find_molecules_by_mechanism(
                focus_cluster, 
                limit=20
            )
            if cluster_molecules:
                context_parts.append(f"\n\n=== MOLECULES IN CLUSTER: {focus_cluster} ===")
                for mol in cluster_molecules:
                    context_parts.append(
                        f"- {mol.get('name', 'Unknown')} "
                        f"(SMILES: {mol['smiles']}, MW: {mol.get('mw', 'N/A')}, "
                        f"Papers: {mol.get('paper_count', 0)})"
                    )
        
        # 4. Add previous selections to avoid duplicates
        if previous_selections:
            context_parts.append("\n\n=== ALREADY SELECTED (DO NOT RE-SELECT) ===")
            for smiles in previous_selections:
                context_parts.append(f"- {smiles}")
        
        return "\n".join(context_parts)
    
    def _parse_selection_response(
        self, 
        response_text: str,
        iteration: int
    ) -> List[SelectionResult]:
        """
        Parse LLM response to extract structured molecule selections
        
        Note: This uses a simple parsing approach. For production,
        consider using structured output (Gemini function calling)
        or more robust parsing.
        """
        selections = []
        
        # Simple parsing - look for SMILES patterns
        # [IMPROVEMENT: Use Gemini's structured output/function calling]
        lines = response_text.split('\n')
        
        current_molecule = {}
        
        for line in lines:
            line = line.strip()
            
            if line.lower().startswith('smiles:'):
                if current_molecule.get('smiles'):
                    # Save previous molecule
                    try:
                        selections.append(SelectionResult(
                            smiles=current_molecule.get('smiles', ''),
                            name=current_molecule.get('name', 'Unknown'),
                            selection_score=self._parse_confidence(
                                current_molecule.get('confidence', 'medium')
                            ),
                            rationale=current_molecule.get('rationale', ''),
                            supporting_papers=current_molecule.get('papers', []),
                            mechanism=current_molecule.get('mechanism', 'unknown'),
                            safety_notes=current_molecule.get('safety', []),
                            iteration_selected=iteration
                        ))
                    except Exception:
                        pass
                    current_molecule = {}
                
                current_molecule['smiles'] = line.split(':', 1)[1].strip()
            
            elif line.lower().startswith('name:'):
                current_molecule['name'] = line.split(':', 1)[1].strip()
            
            elif line.lower().startswith('confidence:'):
                current_molecule['confidence'] = line.split(':', 1)[1].strip()
            
            elif 'rationale' in line.lower() or 'reason' in line.lower():
                current_molecule['rationale'] = line
        
        # Don't forget last molecule
        if current_molecule.get('smiles'):
            try:
                selections.append(SelectionResult(
                    smiles=current_molecule.get('smiles', ''),
                    name=current_molecule.get('name', 'Unknown'),
                    selection_score=self._parse_confidence(
                        current_molecule.get('confidence', 'medium')
                    ),
                    rationale=current_molecule.get('rationale', ''),
                    supporting_papers=current_molecule.get('papers', []),
                    mechanism=current_molecule.get('mechanism', 'unknown'),
                    safety_notes=current_molecule.get('safety', []),
                    iteration_selected=iteration
                ))
            except Exception:
                pass
        
        return selections
    
    def _parse_confidence(self, confidence_str: str) -> float:
        """Convert confidence string to float"""
        confidence_str = confidence_str.lower()
        if 'high' in confidence_str:
            return 0.9
        elif 'medium' in confidence_str:
            return 0.6
        elif 'low' in confidence_str:
            return 0.3
        else:
            return 0.5
    
    def run_iterative_research(
        self,
        session: ResearchSession,
        max_iterations: int = 5,
        molecules_per_iteration: int = 10
    ) -> ResearchSession:
        """
        Run the iterative research workflow
        
        Each iteration:
        1. Build context from vector store + graph
        2. Query Gemini for molecule recommendations
        3. Parse and validate results
        4. Update session state
        5. Formulate next query based on gaps
        """
        
        # Define research queries for each iteration
        # These represent different "angles" of exploration
        research_queries = [
            "ethanol water separation entrainer glycol efficiency",
            "safe non-toxic entrainer dehydration solvent",
            "ionic liquid deep eutectic solvent ethanol separation",
            "industrial entrainer extractive distillation commercial",
            "novel green solvent alcohol separation sustainable"
        ]
        
        for iteration in range(max_iterations):
            if len(session.selected_molecules) >= session.target_count:
                print(f"Target count reached at iteration {iteration}")
                break
            
            query = research_queries[iteration % len(research_queries)]
            print(f"\n=== Iteration {iteration + 1}: '{query}' ===")
            
            # Build context
            context = self._build_context(
                query=query,
                previous_selections=[m.smiles for m in session.selected_molecules]
            )
            
            # Create prompt
            prompt = f"""Based on the following context, identify {molecules_per_iteration} promising entrainer molecules for ethanol-water separation that have NOT been previously selected.

{context}

For each molecule, provide:
1. SMILES: [exact SMILES string]
2. Name: [molecule name]
3. Confidence: [high/medium/low]
4. Rationale: [why this is a good candidate]
5. Safety: [any safety concerns mentioned]
6. Source: [which paper/database mentioned this]

Remember: Only recommend molecules explicitly mentioned in the context above."""

            # Query Gemini
            try:
                # [VERIFY: Current Gemini API call structure]
                response = self.model.generate_content(prompt)
                response_text = response.text
                
                # Parse response
                new_selections = self._parse_selection_response(
                    response_text, 
                    iteration
                )
                
                # Add to session (avoid duplicates)
                existing_smiles = {m.smiles for m in session.selected_molecules}
                for selection in new_selections:
                    if selection.smiles not in existing_smiles:
                        session.selected_molecules.append(selection)
                        existing_smiles.add(selection.smiles)
                
                # Record iteration
                session.iteration_history.append({
                    "iteration": iteration,
                    "query": query,
                    "context_length": len(context),
                    "new_molecules": len(new_selections),
                    "total_molecules": len(session.selected_molecules)
                })
                
                print(f"  Selected {len(new_selections)} new molecules")
                print(f"  Total: {len(session.selected_molecules)}")
                
            except Exception as e:
                print(f"  Error in iteration {iteration}: {e}")
                session.iteration_history.append({
                    "iteration": iteration,
                    "query": query,
                    "error": str(e)
                })
        
        return session
    
    def export_results(
        self,
        session: ResearchSession,
        output_path: Path
    ) -> Path:
        """Export research results to JSON"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            "session_id": session.session_id,
            "target_count": session.target_count,
            "actual_count": len(session.selected_molecules),
            "molecules": [
                {
                    "smiles": m.smiles,
                    "name": m.name,
                    "score": m.selection_score,
                    "rationale": m.rationale,
                    "papers": m.supporting_papers,
                    "mechanism": m.mechanism,
                    "safety_notes": m.safety_notes,
                    "iteration": m.iteration_selected
                }
                for m in session.selected_molecules
            ],
            "iteration_history": session.iteration_history
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return output_path


# Example orchestration script
def run_engine_a_pipeline():
    """
    Main pipeline for Engine A
    
    Prerequisites:
    1. Neo4j running with populated graph (from Phase I + II-A.3)
    2. ChromaDB populated with paper chunks (from II-A.2)
    3. GOOGLE_API_KEY set
    """
    from uuid import uuid4
    
    # Initialize components
    # [Adjust imports based on your project structure]
    # vector_store = MoleculeRAGVectorStore()
    # graph_db = MoleculeGraphDB()
    
    # For testing, create mock objects
    print("NOTE: This is a template. Connect actual vector_store and graph_db.")
    print("Exiting template mode.")
    return
    
    # Initialize research engine
    engine = GeminiResearchEngine(
        vector_store=vector_store,
        graph_db=graph_db,
        model_name="gemini-1.5-pro"  # [VERIFY current model]
    )
    
    # Create session
    session = ResearchSession(
        session_id=str(uuid4()),
        target_count=50
    )
    
    # Run research
    session = engine.run_iterative_research(
        session=session,
        max_iterations=5,
        molecules_per_iteration=12
    )
    
    # Export results
    output_path = Path("data/engine_a_results.json")
    engine.export_results(session, output_path)
    
    print(f"\n=== ENGINE A COMPLETE ===")
    print(f"Selected {len(session.selected_molecules)} molecules")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    run_engine_a_pipeline()
```

---

## Code Artifacts Summary

### Notebooks to Create

| Notebook | Purpose |
|----------|---------|
| `05_corpus_acquisition.ipynb` | Semantic Scholar API queries, paper collection |
| `06_chunking_embedding.ipynb` | Document processing, ChromaDB population |
| `07_neo4j_population.ipynb` | Graph schema creation, data loading |
| `08_gemini_research.ipynb` | Interactive testing of research workflow |
| `09_engine_a_integration.ipynb` | Full Engine A pipeline execution |

### Required Configuration Files

```python
# config/engine_a_config.yaml
"""
Configuration for Engine A pipeline
"""

vector_store:
  persist_directory: "./data/chromadb"
  paper_collection: "paper_chunks"
  molecule_collection: "molecule_cards"

neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  # password: Set via NEO4J_PASSWORD env var

gemini:
  model: "gemini-1.5-pro"  # [VERIFY: Current model name]
  # api_key: Set via GOOGLE_API_KEY env var

research:
  target_molecules: 50
  max_iterations: 5
  molecules_per_iteration: 12

data_sources:
  semantic_scholar:
    max_papers: 500
    rate_limit_delay: 1.0
```

### Data Pipeline Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                 ENGINE A DATA FLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Semantic Scholar API]  ──►  [Paper Corpus JSON]               │
│                                      │                          │
│                                      ▼                          │
│                            [Chunking Pipeline]                   │
│                                      │                          │
│                                      ▼                          │
│                            [ChromaDB Embeddings]                 │
│                                      │                          │
│  [PubChem API]  ──►  [Molecule Data]  │                         │
│         │                   │        │                          │
│         ▼                   ▼        ▼                          │
│  [RDKit Properties]  ──► [Neo4j Graph]  ◄───  [Paper-Molecule   │
│                                               Links]             │
│                                      │                          │
│                                      ▼                          │
│                          [Graph-RAG Queries]                     │
│                                      │                          │
│                                      ▼                          │
│                          [Gemini Reasoning]                      │
│                                      │                          │
│                                      ▼                          │
│                    [Engine A Results: 25-50 molecules]          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Verification Notes

### Items Requiring User Verification

| Item | Action Required | URL |
|------|-----------------|-----|
| Gemini model name | Verify current available models | https://ai.google.dev/models/gemini |
| Gemini API structure | Check current SDK documentation | https://ai.google.dev/gemini-api/docs |
| ChromaDB API | Verify current API (changes frequently) | https://docs.trychroma.com/ |
| Semantic Scholar rate limits | Check current policy | https://api.semanticscholar.org/ |
| Neo4j Python driver | Verify current version compatibility | https://neo4j.com/docs/python-manual/current/ |

### Sources Cited

| Claim | Source | Status |
|-------|--------|--------|
| Semantic Scholar API exists | https://api.semanticscholar.org/ | High confidence |
| ChromaDB as vector store | https://www.trychroma.com/ | High confidence |
| Neo4j Python driver | https://neo4j.com/docs/python-manual/current/ | High confidence |
| Gemini API general structure | https://ai.google.dev/ | Moderate - verify current version |
| Graph-RAG architecture concept | Established RAG pattern | High confidence |

### Accuracy Limitations

1. **Gemini "Deep Research"**: I interpreted this as a custom workflow since I'm not certain of a specific Google product by this name. If you're referring to a specific feature, please clarify.

2. **ZINC Database**: You mentioned ZINC alongside PubChem. ZINC (https://zinc.docking.org/) is primarily for drug discovery/docking. For industrial solvents, PubChem may be more relevant. [NEEDS VERIFICATION: Is ZINC appropriate for entrainer molecules?]

3. **Paper full-text access**: The pipeline assumes abstract-level access. Full-text would require institutional subscriptions or open-access filtering.

---

## GitHub Portfolio Framing

### README Section for Phase II-A

```markdown
## Phase II-A: Multi-Vector Initial Selection 🎯

### Engine A: Graph-RAG Literature Analysis

**Status:** In Development

This module implements a Graph-RAG (Retrieval-Augmented Generation) system 
for literature-grounded molecule selection.

#### Architecture
- **Vector Store:** ChromaDB for semantic paper search
- **Graph Store:** Neo4j for molecule-literature relationships
- **Reasoning:** Gemini 1.5 Pro for grounded inference

#### Key Features
- Iterative research workflow with provenance tracking
- No hallucinated molecules - all recommendations cite sources
- Integration with Phase I cluster definitions

#### Outputs
- 25-50 molecules with documented selection rationale
- Full provenance chain (which paper mentioned which molecule)
- Confidence scores and safety flags

### Reproducibility
```bash
# Populate vector store
python -m src.corpus.populate_chromadb

# Populate Neo4j graph
python -m src.graphdb.populate_graph

# Run Engine A
python -m src.llm.gemini_research_engine
```
```

### Suggested Badges

```markdown
![Graph-RAG](https://img.shields.io/badge/Architecture-Graph--RAG-purple)
![Neo4j](https://img.shields.io/badge/Graph-Neo4j-blue)
![ChromaDB](https://img.shields.io/badge/Vector-ChromaDB-orange)
![Gemini](https://img.shields.io/badge/LLM-Gemini-green)
```

---

## Confidence Assessment

### High Confidence
- Overall Graph-RAG architecture design
- ChromaDB as lightweight vector store choice
- Neo4j Community Edition for graph storage
- Semantic Scholar as free academic paper source
- RDKit for molecular property calculation
- General Python code patterns and error handling

### Needs Verification
- **Gemini API current structure** - SDK may have changed
- **"Gemini 3 Pro"** - I'm not aware of this version; verify model availability
- **"Deep Research flows"** - unclear if this is a specific Google product
- **ChromaDB current API** - evolves rapidly, check docs
- **Rate limits** for all APIs - verify current policies

### Outside My Expertise
- Optimal embedding models for chemistry text (ChemBERTa vs SciBERT vs general)
- ZINC database applicability for industrial solvents (vs drug-like molecules)
- Specific institutional access to full-text papers in your context

---
