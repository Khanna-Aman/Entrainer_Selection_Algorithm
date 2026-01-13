# 🎯 Phase III Implementation: Deep Traversal & Expansion

## Understanding Check

Based on the provided documents, I understand Phase III as follows:

**Context:** After Phase II completes, we have 75-150 "seed molecules" selected through three parallel engines:
- **Engine A (Graph-RAG):** Literature-grounded selection (25-50 molecules)
- **Engine B (TRIZ):** Innovation-driven selection (25-50 molecules)
- **Engine C (Cheminformatics):** Diversity-optimized selection (25-50 molecules)

**Phase III Objective:** Treat these seed molecules as "drilling locations" and perform **graph traversal** in Neo4j to:
1. Discover neighbor molecules (structurally similar, mentioned in same papers, share properties)
2. Follow "high probability paths" in the knowledge graph
3. Expand the candidate pool while maintaining safety and cost-effectiveness KPIs
4. Identify molecules missed in the initial Phase II scan

**Oil Exploration Metaphor:** This is the "drilling" phase where we follow veins of high probability from our initial strike points, avoiding low-yield areas.

---

## Recommended Approach

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│        PHASE III: DEEP TRAVERSAL & EXPANSION             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                       │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │         SEED CONSOLIDATION                 │ │
│ │ - Merge Engine A/B/C results (75-150 seeds)             │ │
│ │ - Prioritize multi-engine overlaps                 │ │
│ │ - Load into Neo4j as traversal starting points           │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│               │                     │
│               ▼                     │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │         GRAPH ENRICHMENT                  │ │
│ │ - Add structural similarity edges (Tanimoto > threshold)       │ │
│ │ - Add co-occurrence edges (same paper mentions)           │ │
│ │ - Add property similarity edges (similar descriptors)        │ │
│ │ - Import literature citations network               │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│               │                     │
│               ▼                     │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │         TRAVERSAL STRATEGIES                │ │
│ │                                   │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │ │
│ │ │ STRUCTURAL │ │ LITERATURE │ │ PROPERTY  │ │ MECHANISM  │   │ │
│ │ │ NEIGHBORS │ │ NEIGHBORS │ │ NEIGHBORS │ │ NEIGHBORS │   │ │
│ │ │       │ │       │ │       │ │       │   │ │
│ │ │ Tanimoto │ │ Co-citation │ │ Descriptor │ │ Same mech- │   │ │
│ │ │ similarity │ │ analysis  │ │ matching  │ │ anism type │   │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │ │
│ │                                   │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│               │                     │
│               ▼                     │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │         PROBABILITY SCORING                 │ │
│ │ - Score each discovered neighbor by multiple factors         │ │
│ │ - Apply safety KPI filters (exclude high-hazard)           │ │
│ │ - Apply cost-effectiveness filters                │ │
│ │ - Rank by composite "drilling success" probability         │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│               │                     │
│               ▼                     │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │         EXPANSION OUTPUT                  │ │
│ │ - Expanded candidate pool (150-300 molecules)            │ │
│ │ - Each with traversal provenance (how discovered)          │ │
│ │ - Ready for Phase IV optimization                │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Sub-Phase III.1: Seed Consolidation

### Merging Engine Outputs

First, we consolidate the outputs from all three Phase II engines and identify priority seeds.

```python
# src/traversal/seed_consolidation.py
"""
Phase III.1: Seed Consolidation

Merges outputs from Engines A, B, and C into a unified seed set
for graph traversal. Prioritizes molecules appearing in multiple engines.

References:
- Phase II-A: Engine A (Graph-RAG) results
- Phase II-B: Engine B (TRIZ) results
- Phase II-C: Engine C (Cheminformatics) results
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from collections import Counter
import json

@dataclass
class SeedMolecule:
    """A seed molecule for graph traversal with provenance"""
    smiles: str
    name: str
    source_engines: List[str]  # Which engines selected this molecule
    priority_score: float  # Higher = more engines agree
    cluster_id: Optional[str] = None
    mechanism: Optional[str] = None
    properties: Dict = field(default_factory=dict)
    rationale: str = ""  # Combined rationale from all sources
    
    def to_dict(self) -> dict:
        return {
            "smiles": self.smiles,
            "name": self.name,
            "source_engines": self.source_engines,
            "priority_score": self.priority_score,
            "cluster_id": self.cluster_id,
            "mechanism": self.mechanism,
            "properties": self.properties,
            "rationale": self.rationale
        }

@dataclass
class ConsolidationResult:
    """Result of seed consolidation"""
    all_seeds: List[SeedMolecule]
    triple_overlap: List[str]  # SMILES in all 3 engines
    double_overlap: List[str]  # SMILES in 2 engines
    single_source: List[str]   # SMILES in only 1 engine
    statistics: Dict

class SeedConsolidator:
    """
    Consolidates seed molecules from all Phase II engines.
    
    Priority Scoring:
    - Triple overlap (A+B+C): 3.0 base score
    - Double overlap (any 2): 2.0 base score
    - Single source: 1.0 base score
    
    Additional bonuses:
    - Literature support (Engine A): +0.5
    - TRIZ innovation score (Engine B): +0.3
    - High diversity contribution (Engine C): +0.2
    """
    
    def __init__(
        self,
        engine_a_path: Optional[Path] = None,
        engine_b_path: Optional[Path] = None,
        engine_c_path: Optional[Path] = None
    ):
        """
        Args:
            engine_a_path: Path to Engine A results JSON
            engine_b_path: Path to Engine B results JSON
            engine_c_path: Path to Engine C results JSON
        """
        self.engine_a_data = self._load_json(engine_a_path) if engine_a_path else {}
        self.engine_b_data = self._load_json(engine_b_path) if engine_b_path else {}
        self.engine_c_data = self._load_json(engine_c_path) if engine_c_path else {}
        
    def _load_json(self, path: Path) -> dict:
        """Load JSON file with error handling."""
        if not path or not path.exists():
            return {}
        try:
            with open(path) as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {path}: {e}")
            return {}
    
    def consolidate(self) -> ConsolidationResult:
        """
        Consolidate all engine outputs into unified seed list.
        
        Returns:
            ConsolidationResult with all seeds and overlap statistics
        """
        # Extract molecules from each engine
        engine_a_molecules = self._extract_engine_a_molecules()
        engine_b_molecules = self._extract_engine_b_molecules()
        engine_c_molecules = self._extract_engine_c_molecules()
        
        # Track SMILES to source engines
        smiles_to_sources: Dict[str, List[str]] = {}
        smiles_to_data: Dict[str, Dict] = {}
        
        # Process Engine A
        for mol in engine_a_molecules:
            smiles = mol.get("smiles", "")
            if not smiles:
                continue
            if smiles not in smiles_to_sources:
                smiles_to_sources[smiles] = []
                smiles_to_data[smiles] = {"name": "", "properties": {}, "rationale": []}
            smiles_to_sources[smiles].append("A")
            smiles_to_data[smiles]["name"] = mol.get("name", smiles_to_data[smiles]["name"])
            smiles_to_data[smiles]["rationale"].append(f"[A]: {mol.get('rationale', 'Literature-grounded')}")
            if mol.get("supporting_papers"):
                smiles_to_data[smiles]["rationale"].append(f"Papers: {mol.get('supporting_papers')}")
        
        # Process Engine B
        for mol in engine_b_molecules:
            smiles = mol.get("smiles", "")
            if not smiles:
                continue
            if smiles not in smiles_to_sources:
                smiles_to_sources[smiles] = []
                smiles_to_data[smiles] = {"name": "", "properties": {}, "rationale": []}
            smiles_to_sources[smiles].append("B")
            smiles_to_data[smiles]["name"] = mol.get("name", smiles_to_data[smiles]["name"])
            smiles_to_data[smiles]["rationale"].append(f"[B]: {mol.get('rationale', 'TRIZ-derived')}")
            if mol.get("supporting_agents"):
                smiles_to_data[smiles]["rationale"].append(f"TRIZ agents: {mol.get('supporting_agents')}")
        
        # Process Engine C
        for mol in engine_c_molecules:
            smiles = mol.get("smiles", "")
            if not smiles:
                continue
            if smiles not in smiles_to_sources:
                smiles_to_sources[smiles] = []
                smiles_to_data[smiles] = {"name": "", "properties": {}, "rationale": []}
            smiles_to_sources[smiles].append("C")
            smiles_to_data[smiles]["name"] = mol.get("name", smiles_to_data[smiles]["name"])
            smiles_to_data[smiles]["properties"] = mol.get("properties", {})
            smiles_to_data[smiles]["cluster_id"] = mol.get("cluster_id", "")
            smiles_to_data[smiles]["rationale"].append("[C]: Diversity-selected")
        
        # Create seed molecules with priority scores
        seeds = []
        triple_overlap = []
        double_overlap = []
        single_source = []
        
        for smiles, sources in smiles_to_sources.items():
            n_sources = len(sources)
            
            # Calculate priority score
            priority_score = float(n_sources)  # Base: number of engines
            
            # Bonuses
            if "A" in sources:
                priority_score += 0.5  # Literature support
            if "B" in sources:
                priority_score += 0.3  # Innovation potential
            if "C" in sources:
                priority_score += 0.2  # Diversity contribution
            
            data = smiles_to_data[smiles]
            
            seed = SeedMolecule(
                smiles=smiles,
                name=data.get("name", ""),
                source_engines=sources,
                priority_score=priority_score,
                cluster_id=data.get("cluster_id"),
                properties=data.get("properties", {}),
                rationale=" | ".join(data.get("rationale", []))
            )
            seeds.append(seed)
            
            # Track overlaps
            if n_sources == 3:
                triple_overlap.append(smiles)
            elif n_sources == 2:
                double_overlap.append(smiles)
            else:
                single_source.append(smiles)
        
        # Sort by priority score (descending)
        seeds.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Calculate statistics
        statistics = {
            "total_seeds": len(seeds),
            "triple_overlap_count": len(triple_overlap),
            "double_overlap_count": len(double_overlap),
            "single_source_count": len(single_source),
            "engine_a_contribution": len(engine_a_molecules),
            "engine_b_contribution": len(engine_b_molecules),
            "engine_c_contribution": len(engine_c_molecules),
            "average_priority_score": sum(s.priority_score for s in seeds) / len(seeds) if seeds else 0
        }
        
        return ConsolidationResult(
            all_seeds=seeds,
            triple_overlap=triple_overlap,
            double_overlap=double_overlap,
            single_source=single_source,
            statistics=statistics
        )
    
    def _extract_engine_a_molecules(self) -> List[Dict]:
        """Extract molecules from Engine A results."""
        return self.engine_a_data.get("molecules", [])
    
    def _extract_engine_b_molecules(self) -> List[Dict]:
        """Extract molecules from Engine B results."""
        return self.engine_b_data.get("selected_molecules", [])
    
    def _extract_engine_c_molecules(self) -> List[Dict]:
        """Extract molecules from Engine C results."""
        return self.engine_c_data.get("selected_molecules", [])
    
    def export_seeds(
        self, 
        result: ConsolidationResult, 
        output_path: Path
    ) -> Path:
        """Export consolidated seeds to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "phase": "III",
            "stage": "seed_consolidation",
            "seeds": [s.to_dict() for s in result.all_seeds],
            "overlaps": {
                "triple": result.triple_overlap,
                "double": result.double_overlap,
                "single": result.single_source
            },
            "statistics": result.statistics
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_path


if __name__ == "__main__":
    # Example usage
    consolidator = SeedConsolidator(
        engine_a_path=Path("data/engine_a_results.json"),
        engine_b_path=Path("data/engine_b_results.json"),
        engine_c_path=Path("data/engine_c_results.json")
    )
    
    result = consolidator.consolidate()
    
    print(f"Total seeds: {result.statistics['total_seeds']}")
    print(f"Triple overlap: {result.statistics['triple_overlap_count']}")
    print(f"Double overlap: {result.statistics['double_overlap_count']}")
    print(f"Single source: {result.statistics['single_source_count']}")
    
    if result.triple_overlap:
        print("\nHighest priority seeds (in all 3 engines):")
        for smiles in result.triple_overlap[:5]:
            seed = next(s for s in result.all_seeds if s.smiles == smiles)
            print(f"  - {seed.name}: {smiles[:30]}... (score: {seed.priority_score:.1f})")
```

---

## Sub-Phase III.2: Graph Enrichment

### Building Traversal-Ready Graph Structure

Before traversal, we need to enrich the Neo4j graph with additional edge types that enable discovery of neighbor molecules.

```python
# src/traversal/graph_enrichment.py
"""
Phase III.2: Graph Enrichment for Traversal

Adds additional edges to the Neo4j graph to enable effective traversal:
1. SIMILAR_TO: Structural similarity (Tanimoto)
2. CO_MENTIONED: Molecules mentioned in same papers
3. PROPERTY_SIMILAR: Similar physicochemical properties
4. SAME_MECHANISM: Share separation mechanism

References:
- Neo4j Python Driver: https://neo4j.com/docs/python-manual/current/
- RDKit for similarity: https://www.rdkit.org/docs/
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import json
import os

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("WARNING: neo4j package not available. Install with: pip install neo4j")

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit import DataStructs
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

@dataclass
class EnrichmentConfig:
    """Configuration for graph enrichment"""
    tanimoto_threshold: float = 0.5  # Minimum similarity for SIMILAR_TO edge
    property_similarity_threshold: float = 0.8  # Normalized property similarity
    batch_size: int = 100  # Batch size for Neo4j operations
    max_similar_edges_per_molecule: int = 20  # Limit edges to prevent explosion

class GraphEnrichment:
    """
    Enriches the Neo4j knowledge graph with traversal-enabling edges.
    
    Edge Types Created:
    1. (Molecule)-[:SIMILAR_TO {tanimoto: 0.7}]->(Molecule)
       - Based on Morgan fingerprint similarity
       - Bidirectional (created once, traversable both ways)
       
    2. (Molecule)-[:CO_MENTIONED {paper_count: 3}]->(Molecule)
       - Molecules mentioned in the same papers
       - Suggests functional relationship
       
    3. (Molecule)-[:PROPERTY_SIMILAR {similarity: 0.85}]->(Molecule)
       - Similar physicochemical profiles
       - Useful for finding functional analogs
       
    4. (Molecule)-[:SAME_MECHANISM]->(Mechanism)
       - Links molecules to separation mechanisms
       - Enables mechanism-based traversal
    """
    
    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        config: Optional[EnrichmentConfig] = None
    ):
        """
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            config: Enrichment configuration
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j package required. Install with: pip install neo4j")
        
        self.uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.password = neo4j_password or os.getenv("NEO4J_PASSWORD", "password")
        self.config = config or EnrichmentConfig()
        
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
    
    # =========================================================================
    # SEED LOADING
    # =========================================================================
    
    def load_seeds_to_graph(
        self, 
        seeds: List[Dict],
        mark_as_seed: bool = True
    ) -> int:
        """
        Load seed molecules into Neo4j graph.
        
        Args:
            seeds: List of seed molecule dicts (from consolidation)
            mark_as_seed: Add :Seed label for easy identification
            
        Returns:
            Number of seeds loaded
        """
        query = """
        UNWIND $seeds AS seed
        MERGE (m:Molecule {smiles: seed.smiles})
        SET m.name = seed.name,
            m.priority_score = seed.priority_score,
            m.source_engines = seed.source_engines,
            m.cluster_id = seed.cluster_id,
            m.is_seed = true,
            m.updated_at = datetime()
        WITH m, seed
        WHERE seed.mark_as_seed = true
        SET m:Seed
        RETURN count(m) as loaded
        """
        
        # Prepare seeds with marking flag
        seeds_data = []
        for seed in seeds:
            seed_copy = dict(seed)
            seed_copy["mark_as_seed"] = mark_as_seed
            seeds_data.append(seed_copy)
        
        with self.driver.session() as session:
            result = session.run(query, seeds=seeds_data)
            record = result.single()
            return record["loaded"] if record else 0
    
    # =========================================================================
    # STRUCTURAL SIMILARITY EDGES
    # =========================================================================
    
    def create_similarity_edges(
        self,
        smiles_list: Optional[List[str]] = None
    ) -> int:
        """
        Create SIMILAR_TO edges based on Tanimoto similarity.
        
        If smiles_list is None, computes for all molecules in graph.
        This can be expensive for large graphs - use with caution.
        
        Args:
            smiles_list: Optional list of SMILES to focus on (seeds)
            
        Returns:
            Number of edges created
        """
        if not RDKIT_AVAILABLE:
            print("WARNING: RDKit not available, skipping similarity edges")
            return 0
        
        # Get molecules from graph
        if smiles_list:
            molecules = self._get_molecules_by_smiles(smiles_list)
        else:
            molecules = self._get_all_molecules()
        
        if len(molecules) < 2:
            return 0
        
        print(f"Computing similarity for {len(molecules)} molecules...")
        
        # Compute fingerprints
        fps = {}
        for mol in molecules:
            smiles = mol["smiles"]
            rdkit_mol = Chem.MolFromSmiles(smiles)
            if rdkit_mol:
                fps[smiles] = AllChem.GetMorganFingerprintAsBitVect(rdkit_mol, 2, nBits=2048)
        
        # Find similar pairs above threshold
        similar_pairs = []
        smiles_keys = list(fps.keys())
        
        for i in range(len(smiles_keys)):
            similarities = []
            for j in range(i + 1, len(smiles_keys)):
                sim = DataStructs.TanimotoSimilarity(
                    fps[smiles_keys[i]], 
                    fps[smiles_keys[j]]
                )
                if sim >= self.config.tanimoto_threshold:
                    similarities.append((smiles_keys[j], sim))
            
            # Limit edges per molecule
            similarities.sort(key=lambda x: x[1], reverse=True)
            for target_smiles, sim in similarities[:self.config.max_similar_edges_per_molecule]:
                similar_pairs.append({
                    "smiles1": smiles_keys[i],
                    "smiles2": target_smiles,
                    "tanimoto": sim
                })
        
        print(f"Found {len(similar_pairs)} similar pairs above threshold {self.config.tanimoto_threshold}")
        
        # Create edges in batches
        edges_created = 0
        for i in range(0, len(similar_pairs), self.config.batch_size):
            batch = similar_pairs[i:i + self.config.batch_size]
            edges_created += self._create_similarity_batch(batch)
        
        return edges_created
    
    def _create_similarity_batch(self, pairs: List[Dict]) -> int:
        """Create a batch of similarity edges."""
        query = """
        UNWIND $pairs AS pair
        MATCH (m1:Molecule {smiles: pair.smiles1})
        MATCH (m2:Molecule {smiles: pair.smiles2})
        MERGE (m1)-[r:SIMILAR_TO]->(m2)
        SET r.tanimoto = pair.tanimoto,
            r.created_at = datetime()
        RETURN count(r) as created
        """
        
        with self.driver.session() as session:
            result = session.run(query, pairs=pairs)
            record = result.single()
            return record["created"] if record else 0
    
    # =========================================================================
    # CO-MENTION EDGES
    # =========================================================================
    
    def create_co_mention_edges(self) -> int:
        """
        Create CO_MENTIONED edges for molecules appearing in same papers.
        
        This leverages the existing MENTIONED_IN relationships from Engine A.
        
        Returns:
            Number of edges created
        """
        query = """
        // Find molecule pairs that share papers
        MATCH (m1:Molecule)-[:MENTIONED_IN]->(p:Paper)<-[:MENTIONED_IN]-(m2:Molecule)
        WHERE m1.smiles < m2.smiles  // Avoid duplicates
        WITH m1, m2, count(DISTINCT p) as shared_papers
        WHERE shared_papers >= 1
        MERGE (m1)-[r:CO_MENTIONED]->(m2)
        SET r.paper_count = shared_papers,
            r.created_at = datetime()
        RETURN count(r) as created
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            return record["created"] if record else 0
    
    # =========================================================================
    # PROPERTY SIMILARITY EDGES
    # =========================================================================
    
    def create_property_similarity_edges(
        self,
        property_weights: Optional[Dict[str, float]] = None
    ) -> int:
        """
        Create PROPERTY_SIMILAR edges based on physicochemical properties.
        
        Uses normalized Euclidean distance on weighted properties.
        
        Args:
            property_weights: Weight for each property (default: equal weights)
            
        Returns:
            Number of edges created
        """
        # Default weights emphasizing entrainer-relevant properties
        if property_weights is None:
            property_weights = {
                "molecular_weight": 1.0,
                "logp": 1.5,  # Important for separation
                "tpsa": 1.5,  # Polar surface area
                "hbd": 1.0,   # H-bond donors
                "hba": 1.0,   # H-bond acceptors
            }
        
        # Get molecules with properties from graph
        molecules = self._get_molecules_with_properties()
        
        if len(molecules) < 2:
            return 0
        
        print(f"Computing property similarity for {len(molecules)} molecules...")
        
        # Normalize properties and compute similarity
        similar_pairs = self._compute_property_similarity(molecules, property_weights)
        
        print(f"Found {len(similar_pairs)} property-similar pairs")
        
        # Create edges
        edges_created = 0
        for i in range(0, len(similar_pairs), self.config.batch_size):
            batch = similar_pairs[i:i + self.config.batch_size]
            edges_created += self._create_property_similarity_batch(batch)
        
        return edges_created
    
    def _compute_property_similarity(
        self, 
        molecules: List[Dict],
        weights: Dict[str, float]
    ) -> List[Dict]:
        """Compute property similarity between molecules."""
        import numpy as np
        
        # Build property matrix
        prop_names = list(weights.keys())
        matrix = []
        valid_molecules = []
        
        for mol in molecules:
            props = mol.get("properties", {})
            row = []
            valid = True
            for prop in prop_names:
                val = props.get(prop)
                if val is None:
                    valid = False
                    break
                row.append(float(val))
            if valid:
                matrix.append(row)
                valid_molecules.append(mol)
        
        if len(matrix) < 2:
            return []
        
        matrix = np.array(matrix)
        
        # Normalize (z-score)
        mean = np.mean(matrix, axis=0)
        std = np.std(matrix, axis=0)
        std[std == 0] = 1
        normalized = (matrix - mean) / std
        
        # Apply weights
        weight_array = np.array([weights.get(p, 1.0) for p in prop_names])
        weighted = normalized * weight_array
        
        # Compute pairwise similarity (1 - normalized distance)
        similar_pairs = []
        n = len(valid_molecules)
        
        for i in range(n):
            for j in range(i + 1, n):
                # Euclidean distance
                dist = np.sqrt(np.sum((weighted[i] - weighted[j]) ** 2))
                # Convert to similarity (inverse, capped at 1)
                max_dist = np.sqrt(np.sum((4 * weight_array) ** 2))  # Approx max distance
                similarity = 1 - min(dist / max_dist, 1)
                
                if similarity >= self.config.property_similarity_threshold:
                    similar_pairs.append({
                        "smiles1": valid_molecules[i]["smiles"],
                        "smiles2": valid_molecules[j]["smiles"],
                        "similarity": similarity
                    })
        
        return similar_pairs
    
    def _create_property_similarity_batch(self, pairs: List[Dict]) -> int:
        """Create a batch of property similarity edges."""
        query = """
        UNWIND $pairs AS pair
        MATCH (m1:Molecule {smiles: pair.smiles1})
        MATCH (m2:Molecule {smiles: pair.smiles2})
        MERGE (m1)-[r:PROPERTY_SIMILAR]->(m2)
        SET r.similarity = pair.similarity,
            r.created_at = datetime()
        RETURN count(r) as created
        """
        
        with self.driver.session() as session:
            result = session.run(query, pairs=pairs)
            record = result.single()
            return record["created"] if record else 0
    
    # =========================================================================
    # MECHANISM LINKS
    # =========================================================================
    
    def create_mechanism_nodes_and_edges(self) -> int:
        """
        Create Mechanism nodes and link molecules to them.
        
        Mechanisms defined in Phase I:
        - HYDROGEN_BONDING
        - POLARITY_SHIFT
        - SALTING_OUT
        - STERIC_DISRUPTION
        
        Returns:
            Number of edges created
        """
        # Create mechanism nodes
        mechanisms = [
            {"name": "HYDROGEN_BONDING", "description": "Preferential H-bonding with water"},
            {"name": "POLARITY_SHIFT", "description": "Alters relative volatility via polarity"},
            {"name": "SALTING_OUT", "description": "Ionic interactions forcing phase separation"},
            {"name": "STERIC_DISRUPTION", "description": "Physical interference with H-bond network"},
        ]
        
        create_mechanisms_query = """
        UNWIND $mechanisms AS mech
        MERGE (m:Mechanism {name: mech.name})
        SET m.description = mech.description
        RETURN count(m) as created
        """
        
        # Link molecules based on cluster_id pattern
        link_query = """
        MATCH (mol:Molecule)
        WHERE mol.cluster_id IS NOT NULL
        WITH mol, 
             CASE 
                 WHEN mol.cluster_id STARTS WITH 'HB_' THEN 'HYDROGEN_BONDING'
                 WHEN mol.cluster_id STARTS WITH 'PS_' THEN 'POLARITY_SHIFT'
                 WHEN mol.cluster_id STARTS WITH 'SO_' THEN 'SALTING_OUT'
                 WHEN mol.cluster_id STARTS WITH 'SD_' THEN 'STERIC_DISRUPTION'
                 ELSE null
             END as mechanism_name
        WHERE mechanism_name IS NOT NULL
        MATCH (mech:Mechanism {name: mechanism_name})
        MERGE (mol)-[r:USES_MECHANISM]->(mech)
        RETURN count(r) as linked
        """
        
        with self.driver.session() as session:
            session.run(create_mechanisms_query, mechanisms=mechanisms)
            result = session.run(link_query)
            record = result.single()
            return record["linked"] if record else 0
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _get_molecules_by_smiles(self, smiles_list: List[str]) -> List[Dict]:
        """Get molecules by SMILES from graph."""
        query = """
        UNWIND $smiles_list AS smiles
        MATCH (m:Molecule {smiles: smiles})
        RETURN m.smiles as smiles, m.name as name, m.properties as properties
        """
        
        with self.driver.session() as session:
            result = session.run(query, smiles_list=smiles_list)
            return [dict(record) for record in result]
    
    def _get_all_molecules(self, limit: int = 10000) -> List[Dict]:
        """Get all molecules from graph (with limit)."""
        query = """
        MATCH (m:Molecule)
        RETURN m.smiles as smiles, m.name as name, m.properties as properties
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            return [dict(record) for record in result]
    
    def _get_molecules_with_properties(self, limit: int = 10000) -> List[Dict]:
        """Get molecules that have property data."""
        query = """
        MATCH (m:Molecule)
        WHERE m.properties IS NOT NULL
        RETURN m.smiles as smiles, m.name as name, m.properties as properties
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            return [dict(record) for record in result]
    
    def run_full_enrichment(
        self,
        seeds: List[Dict],
        compute_all_similarities: bool = False
    ) -> Dict:
        """
        Run complete graph enrichment pipeline.
        
        Args:
            seeds: Consolidated seed molecules
            compute_all_similarities: If True, compute similarity for all molecules
                                     If False, only for seeds (faster)
                                     
        Returns:
            Statistics dictionary
        """
        print("=" * 60)
        print("PHASE III.2: GRAPH ENRICHMENT")
        print("=" * 60)
        
        stats = {}
        
        # Step 1: Load seeds
        print("\n[1/5] Loading seed molecules to graph...")
        stats["seeds_loaded"] = self.load_seeds_to_graph(seeds)
        print(f"      Loaded {stats['seeds_loaded']} seeds")
        
        # Step 2: Create similarity edges
        print("\n[2/5] Creating structural similarity edges...")
        if compute_all_similarities:
            stats["similarity_edges"] = self.create_similarity_edges()
        else:
            seed_smiles = [s.get("smiles") for s in seeds if s.get("smiles")]
            stats["similarity_edges"] = self.create_similarity_edges(seed_smiles)
        print(f"      Created {stats['similarity_edges']} SIMILAR_TO edges")
        
        # Step 3: Create co-mention edges
        print("\n[3/5] Creating co-mention edges...")
        stats["co_mention_edges"] = self.create_co_mention_edges()
        print(f"      Created {stats['co_mention_edges']} CO_MENTIONED edges")
        
        # Step 4: Create property similarity edges
        print("\n[4/5] Creating property similarity edges...")
        stats["property_edges"] = self.create_property_similarity_edges()
        print(f"      Created {stats['property_edges']} PROPERTY_SIMILAR edges")
        
        # Step 5: Create mechanism links
        print("\n[5/5] Creating mechanism nodes and links...")
        stats["mechanism_edges"] = self.create_mechanism_nodes_and_edges()
        print(f"      Created {stats['mechanism_edges']} USES_MECHANISM edges")
        
        print("\n" + "=" * 60)
        print("ENRICHMENT COMPLETE")
        print(f"Total edges created: {sum(stats.values())}")
        print("=" * 60)
        
        return stats


if __name__ == "__main__":
    # Example usage
    print("Graph Enrichment module loaded.")
    print("Use GraphEnrichment class with Neo4j connection to enrich graph.")
```

---

## Sub-Phase III.3: Traversal Strategies

### Multi-Strategy Graph Traversal

This is the core "drilling" logic—traversing the graph from seed molecules to discover neighbors.

```python
# src/traversal/traversal_strategies.py
"""
Phase III.3: Graph Traversal Strategies

Implements multiple traversal strategies to discover neighbor molecules:
1. Structural Traversal: Follow SIMILAR_TO edges
2. Literature Traversal: Follow CO_MENTIONED and citation paths
3. Property Traversal: Follow PROPERTY_SIMILAR edges
4. Mechanism Traversal: Find molecules with same mechanism

Each strategy scores neighbors by "drilling success probability."

References:
- Neo4j Cypher: https://neo4j.com/docs/cypher-manual/current/
- Graph traversal patterns: https://neo4j.com/docs/cypher-manual/current/patterns/
"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

class TraversalStrategy(Enum):
    """Available traversal strategies"""
    STRUCTURAL = "structural"
    LITERATURE = "literature"
    PROPERTY = "property"
    MECHANISM = "mechanism"
    COMBINED = "combined"

@dataclass
class DiscoveredMolecule:
    """A molecule discovered through traversal"""
    smiles: str
    name: str
    discovery_strategy: str
    discovery_path: str  # Description of how it was found
    seed_source: str     # Which seed molecule led to this
    edge_score: float    # Strength of connection (e.g., Tanimoto)
    hop_distance: int    # Number of hops from seed
    probability_score: float = 0.0  # Computed drilling probability
    properties: Dict = field(default_factory=dict)
    safety_flags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "smiles": self.smiles,
            "name": self.name,
            "discovery_strategy": self.discovery_strategy,
            "discovery_path": self.discovery_path,
            "seed_source": self.seed_source,
            "edge_score": self.edge_score,
            "hop_distance": self.hop_distance,
            "probability_score": self.probability_score,
            "properties": self.properties,
            "safety_flags": self.safety_flags
        }

@dataclass
class TraversalConfig:
    """Configuration for traversal"""
    max_hops: int = 2  # Maximum distance from seeds
    min_edge_score: float = 0.4  # Minimum similarity/connection strength
    max_neighbors_per_seed: int = 20  # Limit per seed to prevent explosion
    exclude_seeds: bool = True  # Don't return seeds as discoveries
    
class GraphTraverser:
    """
    Performs graph traversal from seed molecules to discover neighbors.
    
    The "Oil Drilling" Logic:
    - Seeds are "strike points" where we found oil
    - We drill along "high probability veins" (strong edges)
    - We avoid "low probability zones" (weak edges, filtered out)
    - We collect neighbors that meet our KPI thresholds
    """
    
    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        config: Optional[TraversalConfig] = None
    ):
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j package required")
        
        self.uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.password = neo4j_password or os.getenv("NEO4J_PASSWORD", "password")
        self.config = config or TraversalConfig()
        
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
    
    # =========================================================================
    # STRUCTURAL TRAVERSAL
    # =========================================================================
    
    def traverse_structural(
        self,
        seed_smiles: List[str],
        min_tanimoto: Optional[float] = None
    ) -> List[DiscoveredMolecule]:
        """
        Traverse via SIMILAR_TO edges to find structurally similar molecules.
        
        This follows "veins" of structural similarity from seeds.
        
        Cypher Pattern:
        (seed:Seed)-[:SIMILAR_TO*1..2]->(neighbor)
        WHERE similarity above threshold
        
        Args:
            seed_smiles: List of seed SMILES to start from
            min_tanimoto: Minimum Tanimoto similarity (default from config)
            
        Returns:
            List of discovered molecules
        """
        min_tanimoto = min_tanimoto or self.config.min_edge_score
        
        query = """
        UNWIND $seeds AS seed_smiles
        MATCH (seed:Molecule {smiles: seed_smiles})
        // 1-hop: Direct neighbors
        OPTIONAL MATCH path1 = (seed)-[r1:SIMILAR_TO]->(n1:Molecule)
        WHERE r1.tanimoto >= $min_tanimoto
          AND n1.smiles <> seed_smiles
        // 2-hop: Neighbors of neighbors (if configured)
        OPTIONAL MATCH path2 = (seed)-[:SIMILAR_TO]->(mid:Molecule)-[r2:SIMILAR_TO]->(n2:Molecule)
        WHERE r2.tanimoto >= $min_tanimoto
          AND n2.smiles <> seed_smiles
          AND n2.smiles <> mid.smiles
          AND $max_hops >= 2
        
        WITH seed, 
             collect(DISTINCT {
                 smiles: n1.smiles, 
                 name: n1.name,
                 score: r1.tanimoto, 
                 hops: 1,
                 properties: n1.properties
             }) as hop1,
             collect(DISTINCT {
                 smiles: n2.smiles, 
                 name: n2.name,
                 score: r2.tanimoto, 
                 hops: 2,
                 properties: n2.properties
             }) as hop2
        
        UNWIND (hop1 + hop2) as neighbor
        WHERE neighbor.smiles IS NOT NULL
        
        RETURN DISTINCT
            seed.smiles as seed_smiles,
            neighbor.smiles as neighbor_smiles,
            neighbor.name as neighbor_name,
            neighbor.score as edge_score,
            neighbor.hops as hop_distance,
            neighbor.properties as properties
        ORDER BY neighbor.score DESC
        LIMIT $limit
        """
        
        discoveries = []
        
        with self.driver.session() as session:
            result = session.run(
                query,
                seeds=seed_smiles,
                min_tanimoto=min_tanimoto,
                max_hops=self.config.max_hops,
                limit=len(seed_smiles) * self.config.max_neighbors_per_seed
            )
            
            for record in result:
                if self.config.exclude_seeds and record["neighbor_smiles"] in seed_smiles:
                    continue
                    
                discoveries.append(DiscoveredMolecule(
                    smiles=record["neighbor_smiles"],
                    name=record["neighbor_name"] or "",
                    discovery_strategy="structural",
                    discovery_path=f"SIMILAR_TO (Tanimoto: {record['edge_score']:.2f})",
                    seed_source=record["seed_smiles"],
                    edge_score=record["edge_score"],
                    hop_distance=record["hop_distance"],
                    properties=record["properties"] or {}
                ))
        
        return discoveries
    
    # =========================================================================
    # LITERATURE TRAVERSAL
    # =========================================================================
    
    def traverse_literature(
        self,
        seed_smiles: List[str],
        min_shared_papers: int = 1
    ) -> List[DiscoveredMolecule]:
        """
        Traverse via CO_MENTIONED edges and paper citations.
        
        This finds molecules that co-occur in literature with seeds,
        suggesting functional or contextual relationships.
        
        Args:
            seed_smiles: List of seed SMILES
            min_shared_papers: Minimum papers sharing mention
            
        Returns:
            List of discovered molecules
        """
        query = """
        UNWIND $seeds AS seed_smiles
        MATCH (seed:Molecule {smiles: seed_smiles})
        
        // Direct co-mention
        OPTIONAL MATCH (seed)-[r:CO_MENTIONED]-(neighbor:Molecule)
        WHERE r.paper_count >= $min_papers
          AND neighbor.smiles <> seed_smiles
        
        WITH seed, 
             collect(DISTINCT {
                 smiles: neighbor.smiles,
                 name: neighbor.name,
                 paper_count: r.paper_count,
                 properties: neighbor.properties
             }) as co_mentioned
        
        // Also find molecules in same papers (if CO_MENTIONED not created)
        OPTIONAL MATCH (seed)-[:MENTIONED_IN]->(p:Paper)<-[:MENTIONED_IN]-(neighbor2:Molecule)
        WHERE neighbor2.smiles <> seed.smiles
        
        WITH seed, co_mentioned,
             collect(DISTINCT {
                 smiles: neighbor2.smiles,
                 name: neighbor2.name,
                 paper_count: 1,
                 properties: neighbor2.properties
             }) as paper_neighbors
        
        UNWIND (co_mentioned + paper_neighbors) as neighbor
        WHERE neighbor.smiles IS NOT NULL
        
        RETURN DISTINCT
            seed.smiles as seed_smiles,
            neighbor.smiles as neighbor_smiles,
            neighbor.name as neighbor_name,
            neighbor.paper_count as shared_papers,
            neighbor.properties as properties
        ORDER BY shared_papers DESC
        LIMIT $limit
        """
        
        discoveries = []
        
        with self.driver.session() as session:
            result = session.run(
                query,
                seeds=seed_smiles,
                min_papers=min_shared_papers,
                limit=len(seed_smiles) * self.config.max_neighbors_per_seed
            )
            
            for record in result:
                if self.config.exclude_seeds and record["neighbor_smiles"] in seed_smiles:
                    continue
                
                # Normalize paper count to 0-1 score (assuming max ~10 papers)
                edge_score = min(record["shared_papers"] / 10.0, 1.0)
                
                discoveries.append(DiscoveredMolecule(
                    smiles=record["neighbor_smiles"],
                    name=record["neighbor_name"] or "",
                    discovery_strategy="literature",
                    discovery_path=f"CO_MENTIONED ({record['shared_papers']} papers)",
                    seed_source=record["seed_smiles"],
                    edge_score=edge_score,
                    hop_distance=1,
                    properties=record["properties"] or {}
                ))
        
        return discoveries
    
    # =========================================================================
    # PROPERTY TRAVERSAL
    # =========================================================================
    
    def traverse_property(
        self,
        seed_smiles: List[str],
        min_similarity: Optional[float] = None
    ) -> List[DiscoveredMolecule]:
        """
        Traverse via PROPERTY_SIMILAR edges.
        
        Finds molecules with similar physicochemical profiles,
        which may be functional alternatives even if structurally different.
        
        Args:
            seed_smiles: List of seed SMILES
            min_similarity: Minimum property similarity
            
        Returns:
            List of discovered molecules
        """
        min_similarity = min_similarity or self.config.min_edge_score
        
        query = """
        UNWIND $seeds AS seed_smiles
        MATCH (seed:Molecule {smiles: seed_smiles})
        MATCH (seed)-[r:PROPERTY_SIMILAR]->(neighbor:Molecule)
        WHERE r.similarity >= $min_similarity
          AND neighbor.smiles <> seed_smiles
        
        RETURN DISTINCT
            seed.smiles as seed_smiles,
            neighbor.smiles as neighbor_smiles,
            neighbor.name as neighbor_name,
            r.similarity as similarity,
            neighbor.properties as properties
        ORDER BY similarity DESC
        LIMIT $limit
        """
        
        discoveries = []
        
        with self.driver.session() as session:
            result = session.run(
                query,
                seeds=seed_smiles,
                min_similarity=min_similarity,
                limit=len(seed_smiles) * self.config.max_neighbors_per_seed
            )
            
            for record in result:
                if self.config.exclude_seeds and record["neighbor_smiles"] in seed_smiles:
                    continue
                
                discoveries.append(DiscoveredMolecule(
                    smiles=record["neighbor_smiles"],
                    name=record["neighbor_name"] or "",
                    discovery_strategy="property",
                    discovery_path=f"PROPERTY_SIMILAR ({record['similarity']:.2f})",
                    seed_source=record["seed_smiles"],
                    edge_score=record["similarity"],
                    hop_distance=1,
                    properties=record["properties"] or {}
                ))
        
        return discoveries
    
    # =========================================================================
    # MECHANISM TRAVERSAL
    # =========================================================================
    
    def traverse_mechanism(
        self,
        seed_smiles: List[str],
        expand_mechanism: bool = True
    ) -> List[DiscoveredMolecule]:
        """
        Traverse via USES_MECHANISM edges.
        
        Finds other molecules that use the same separation mechanism.
        This is a "lateral" traversal—not based on direct similarity,
        but on functional equivalence.
        
        Args:
            seed_smiles: List of seed SMILES
            expand_mechanism: If True, find ALL molecules with same mechanism
                            If False, only highly-rated ones
            
        Returns:
            List of discovered molecules
        """
        query = """
        UNWIND $seeds AS seed_smiles
        MATCH (seed:Molecule {smiles: seed_smiles})-[:USES_MECHANISM]->(mech:Mechanism)
        MATCH (neighbor:Molecule)-[:USES_MECHANISM]->(mech)
        WHERE neighbor.smiles <> seed_smiles
        
        // Optionally filter to high-priority neighbors
        WITH seed, mech, neighbor,
             COALESCE(neighbor.priority_score, 0) as priority
        WHERE $expand_all OR priority > 0
        
        RETURN DISTINCT
            seed.smiles as seed_smiles,
            neighbor.smiles as neighbor_smiles,
            neighbor.name as neighbor_name,
            mech.name as mechanism,
            priority,
            neighbor.properties as properties
        ORDER BY priority DESC
        LIMIT $limit
        """
        
        discoveries = []
        
        with self.driver.session() as session:
            result = session.run(
                query,
                seeds=seed_smiles,
                expand_all=expand_mechanism,
                limit=len(seed_smiles) * self.config.max_neighbors_per_seed
            )
            
            for record in result:
                if self.config.exclude_seeds and record["neighbor_smiles"] in seed_smiles:
                    continue
                
                # Use priority as edge score (normalized)
                edge_score = min(record["priority"] / 4.0, 1.0) if record["priority"] else 0.5
                
                discoveries.append(DiscoveredMolecule(
                    smiles=record["neighbor_smiles"],
                    name=record["neighbor_name"] or "",
                    discovery_strategy="mechanism",
                    discovery_path=f"SAME_MECHANISM ({record['mechanism']})",
                    seed_source=record["seed_smiles"],
                    edge_score=edge_score,
                    hop_distance=1,  # Same mechanism = functional neighbor
                    properties=record["properties"] or {}
                ))
        
        return discoveries
    
    # =========================================================================
    # COMBINED TRAVERSAL
    # =========================================================================
    
    def traverse_combined(
        self,
        seed_smiles: List[str],
        strategies: Optional[List[TraversalStrategy]] = None
    ) -> List[DiscoveredMolecule]:
        """
        Run multiple traversal strategies and combine results.
        
        Molecules found by multiple strategies get boosted scores.
        
        Args:
            seed_smiles: List of seed SMILES
            strategies: Which strategies to run (default: all)
            
        Returns:
            Combined list of discoveries with unified scoring
        """
        if strategies is None:
            strategies = [
                TraversalStrategy.STRUCTURAL,
                TraversalStrategy.LITERATURE,
                TraversalStrategy.PROPERTY,
                TraversalStrategy.MECHANISM
            ]
        
        all_discoveries: Dict[str, DiscoveredMolecule] = {}
        strategy_counts: Dict[str, int] = {}  # SMILES -> number of strategies finding it
        
        # Run each strategy
        for strategy in strategies:
            if strategy == TraversalStrategy.STRUCTURAL:
                discoveries = self.traverse_structural(seed_smiles)
            elif strategy == TraversalStrategy.LITERATURE:
                discoveries = self.traverse_literature(seed_smiles)
            elif strategy == TraversalStrategy.PROPERTY:
                discoveries = self.traverse_property(seed_smiles)
            elif strategy == TraversalStrategy.MECHANISM:
                discoveries = self.traverse_mechanism(seed_smiles)
            else:
                continue
            
            for d in discoveries:
                if d.smiles not in all_discoveries:
                    all_discoveries[d.smiles] = d
                    strategy_counts[d.smiles] = 1
                else:
                    # Merge: keep highest edge score, combine paths
                    existing = all_discoveries[d.smiles]
                    strategy_counts[d.smiles] += 1
                    
                    if d.edge_score > existing.edge_score:
                        existing.edge_score = d.edge_score
                    
                    existing.discovery_strategy = "combined"
                    existing.discovery_path += f" | {d.discovery_path}"
        
        # Boost scores for multi-strategy discoveries
        for smiles, count in strategy_counts.items():
            if count > 1:
                all_discoveries[smiles].edge_score *= (1 + 0.2 * (count - 1))
        
        return list(all_discoveries.values())
    
    def run_full_traversal(
        self,
        seed_smiles: List[str]
    ) -> Tuple[List[DiscoveredMolecule], Dict]:
        """
        Run complete traversal pipeline.
        
        Returns:
            Tuple of (discoveries, statistics)
        """
        print("=" * 60)
        print("PHASE III.3: GRAPH TRAVERSAL")
        print("=" * 60)
        
        stats = {"seeds": len(seed_smiles)}
        
        print(f"\nTraversing from {len(seed_smiles)} seeds...")
        print(f"Config: max_hops={self.config.max_hops}, min_edge={self.config.min_edge_score}")
        
        discoveries = self.traverse_combined(seed_smiles)
        
        stats["total_discoveries"] = len(discoveries)
        stats["by_strategy"] = {}
        
        for d in discoveries:
            strategy = d.discovery_strategy
            stats["by_strategy"][strategy] = stats["by_strategy"].get(strategy, 0) + 1
        
        print(f"\nDiscoveries by strategy:")
        for strategy, count in stats["by_strategy"].items():
            print(f"  {strategy}: {count}")
        
        print(f"\nTotal unique discoveries: {stats['total_discoveries']}")
        
        return discoveries, stats


if __name__ == "__main__":
    print("Traversal Strategies module loaded.")
    print("Use GraphTraverser class with Neo4j connection.")
```

---

## Sub-Phase III.4: Probability Scoring and KPI Filtering

### Scoring and Filtering Discovered Molecules

```python
# src/traversal/probability_scoring.py
"""
Phase III.4: Probability Scoring and KPI Filtering

Scores discovered molecules by "drilling success probability" and
applies safety/cost-effectiveness filters as defined in the research proposal.

The scoring considers:
1. Discovery strength (edge scores from traversal)
2. Multi-strategy agreement (found by multiple strategies)
3. Proximity to high-priority seeds
4. Property suitability for separation
5. Safety profile (KPI filter)
6. Cost-effectiveness (KPI filter)

References:
- Research Proposal: Safety-Cost Penalty Function
- Phase I: Property requirements for entrainers
"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
import json
from pathlib import Path

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

@dataclass
class ScoringConfig:
    """Configuration for probability scoring"""
    # Weight factors for score components
    edge_score_weight: float = 0.3
    multi_strategy_weight: float = 0.2
    seed_priority_weight: float = 0.2
    property_suitability_weight: float = 0.3
    
    # Safety KPI thresholds
    # Reference: GHS categories, lower = more hazardous
    min_acute_toxicity_category: int = 4  # Category 4+ is acceptable (LD50 > 300 mg/kg)
    max_flash_point_penalty: float = 0.5  # Penalty for flash point < 60°C
    
    # Property suitability ranges (from Phase I/Literature)
    ideal_mw_range: Tuple[float, float] = (80.0, 300.0)
    ideal_bp_min: float = 150.0  # °C, above ethanol BP
    ideal_logp_range: Tuple[float, float] = (-1.0, 2.0)
    ideal_hba_min: int = 2  # At least 2 H-bond acceptors for water affinity

@dataclass
class ScoredMolecule:
    """A molecule with computed probability score"""
    smiles: str
    name: str
    discovery_info: Dict  # From traversal
    probability_score: float  # Final drilling probability
    score_components: Dict[str, float]  # Breakdown
    passes_safety_kpi: bool
    passes_cost_kpi: bool
    safety_flags: List[str]
    properties: Dict
    
    def to_dict(self) -> dict:
        return {
            "smiles": self.smiles,
            "name": self.name,
            "probability_score": self.probability_score,
            "score_components": self.score_components,
            "passes_safety_kpi": self.passes_safety_kpi,
            "passes_cost_kpi": self.passes_cost_kpi,
            "safety_flags": self.safety_flags,
            "properties": self.properties,
            "discovery_info": self.discovery_info
        }

class ProbabilityScorer:
    """
    Computes drilling success probability for discovered molecules.
    
    The metaphor: Not all neighbors are equally promising.
    We want to drill (analyze deeply) the most promising ones first.
    
    This scorer combines:
    1. Traversal evidence (edge strength, multi-strategy)
    2. Intrinsic suitability (properties match separation requirements)
    3. Safety screening (KPI filter from research proposal)
    """
    
    def __init__(
        self,
        config: Optional[ScoringConfig] = None,
        seed_priorities: Optional[Dict[str, float]] = None
    ):
        """
        Args:
            config: Scoring configuration
            seed_priorities: Dict mapping seed SMILES to priority scores
        """
        self.config = config or ScoringConfig()
        self.seed_priorities = seed_priorities or {}
    
    def score_molecule(
        self,
        discovery: Dict,
        strategy_count: int = 1
    ) -> ScoredMolecule:
        """
        Compute probability score for a single discovered molecule.
        
        Args:
            discovery: Discovery dict from traversal
            strategy_count: How many strategies found this molecule
            
        Returns:
            ScoredMolecule with computed scores
        """
        smiles = discovery.get("smiles", "")
        properties = discovery.get("properties", {})
        
        # Calculate score components
        components = {}
        
        # 1. Edge score (direct from traversal)
        edge_score = discovery.get("edge_score", 0.5)
        components["edge_strength"] = edge_score
        
        # 2. Multi-strategy bonus
        multi_strategy_score = min(strategy_count / 4.0, 1.0)  # Max at 4 strategies
        components["multi_strategy"] = multi_strategy_score
        
        # 3. Seed priority inheritance
        seed_smiles = discovery.get("seed_source", "")
        seed_priority = self.seed_priorities.get(seed_smiles, 1.0)
        # Normalize to 0-1 (assuming max priority ~4)
        seed_priority_score = min(seed_priority / 4.0, 1.0)
        components["seed_priority"] = seed_priority_score
        
        # 4. Property suitability
        property_score = self._calculate_property_suitability(smiles, properties)
        components["property_suitability"] = property_score
        
        # Weighted combination
        probability_score = (
            self.config.edge_score_weight * components["edge_strength"] +
            self.config.multi_strategy_weight * components["multi_strategy"] +
            self.config.seed_priority_weight * components["seed_priority"] +
            self.config.property_suitability_weight * components["property_suitability"]
        )
        
        # Safety KPI check
        passes_safety, safety_flags = self._check_safety_kpi(smiles, properties)
        
        # Cost KPI check (simplified)
        passes_cost = self._check_cost_kpi(properties)
        
        # Apply safety penalty to score if needed
        if not passes_safety:
            probability_score *= 0.1  # Heavy penalty for safety failures
        
        return ScoredMolecule(
            smiles=smiles,
            name=discovery.get("name", ""),
            discovery_info={
                "strategy": discovery.get("discovery_strategy", ""),
                "path": discovery.get("discovery_path", ""),
                "seed_source": seed_smiles,
                "hop_distance": discovery.get("hop_distance", 1)
            },
            probability_score=probability_score,
            score_components=components,
            passes_safety_kpi=passes_safety,
            passes_cost_kpi=passes_cost,
            safety_flags=safety_flags,
            properties=properties
        )
    
    def _calculate_property_suitability(
        self,
        smiles: str,
        properties: Dict
    ) -> float:
        """
        Calculate how well properties match ideal entrainer profile.
        
        Returns score 0-1.
        """
        if not properties and RDKIT_AVAILABLE:
            # Calculate properties from SMILES if not provided
            properties = self._calculate_rdkit_properties(smiles)
        
        if not properties:
            return 0.5  # Unknown = neutral
        
        scores = []
        
        # Molecular weight suitability
        mw = properties.get("molecular_weight") or properties.get("MolWt")
        if mw:
            mw_min, mw_max = self.config.ideal_mw_range
            if mw_min <= mw <= mw_max:
                scores.append(1.0)
            else:
                # Penalty proportional to distance from range
                if mw < mw_min:
                    scores.append(max(0, 1 - (mw_min - mw) / mw_min))
                else:
                    scores.append(max(0, 1 - (mw - mw_max) / mw_max))
        
        # LogP suitability
        logp = properties.get("logp") or properties.get("LogP")
        if logp is not None:
            logp_min, logp_max = self.config.ideal_logp_range
            if logp_min <= logp <= logp_max:
                scores.append(1.0)
            else:
                scores.append(max(0, 1 - abs(logp - (logp_min + logp_max) / 2) / 3))
        
        # H-bond acceptors
        hba = properties.get("hba") or properties.get("HBondAcceptors")
        if hba is not None:
            if hba >= self.config.ideal_hba_min:
                scores.append(1.0)
            else:
                scores.append(hba / self.config.ideal_hba_min)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _calculate_rdkit_properties(self, smiles: str) -> Dict:
        """Calculate properties using RDKit."""
        if not RDKIT_AVAILABLE:
            return {}
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {}
            
            return {
                "molecular_weight": Descriptors.MolWt(mol),
                "logp": Descriptors.MolLogP(mol),
                "hba": Descriptors.NumHAcceptors(mol),
                "hbd": Descriptors.NumHDonors(mol),
                "tpsa": Descriptors.TPSA(mol)
            }
        except Exception:
            return {}
    
    def _check_safety_kpi(
        self,
        smiles: str,
        properties: Dict
    ) -> Tuple[bool, List[str]]:
        """
        Check if molecule passes safety KPIs.
        
        Based on research proposal's Safety-Cost Penalty Function:
        - GHS acute toxicity category >= 4 (lower categories = more toxic)
        - Flash point considerations
        - Known hazard flags
        
        Returns:
            Tuple of (passes_kpi, list_of_safety_flags)
        """
        safety_flags = []
        passes = True
        
        # Check GHS toxicity category if available
        toxicity_cat = properties.get("ghs_acute_toxicity_category")
        if toxicity_cat is not None:
            if toxicity_cat < self.config.min_acute_toxicity_category:
                passes = False
                safety_flags.append(f"GHS Category {toxicity_cat} (too toxic)")
        
        # Check flash point
        flash_point = properties.get("flash_point")
        if flash_point is not None and flash_point < 60:
            safety_flags.append(f"Low flash point: {flash_point}°C")
            # Not an automatic fail, but a flag
        
        # Check for known hazardous substructures (simplified)
        if RDKIT_AVAILABLE:
            hazard_patterns = {
                "benzene ring": "c1ccccc1",  # Aromatic - potential carcinogen
                "halogen": "[F,Cl,Br,I]",    # Halogenated
            }
            
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                for hazard_name, pattern in hazard_patterns.items():
                    pattern_mol = Chem.MolFromSmarts(pattern)
                    if pattern_mol and mol.HasSubstructMatch(pattern_mol):
                        safety_flags.append(f"Contains {hazard_name}")
                        # Note: Not automatic fail, just flagged
                        # Benzene itself would fail, benzene ring in larger mol may be ok
        
        return passes, safety_flags
    
    def _check_cost_kpi(self, properties: Dict) -> bool:
        """
        Check if molecule passes cost-effectiveness KPIs.
        
        Simplified check based on:
        - Molecular complexity (proxy for synthesis cost)
        - Common availability (would need external database)
        
        For now, return True unless obvious issues.
        """
        # [NEEDS VERIFICATION]: Real cost estimation requires:
        # - Commercial availability databases (Sigma-Aldrich, TCI, etc.)
        # - Synthesis complexity estimation
        # - Scale-up considerations
        
        # Placeholder: All pass for now
        return True
    
    def score_all(
        self,
        discoveries: List[Dict],
        filter_safety_failures: bool = True
    ) -> List[ScoredMolecule]:
        """
        Score all discovered molecules.
        
        Args:
            discoveries: List of discovery dicts from traversal
            filter_safety_failures: If True, exclude molecules failing safety KPI
            
        Returns:
            List of scored molecules, sorted by probability score
        """
        # Count how many strategies found each molecule
        smiles_strategy_count: Dict[str, int] = {}
        for d in discoveries:
            smiles = d.get("smiles", "")
            strategy = d.get("discovery_strategy", "")
            key = f"{smiles}|{strategy}"
            if key not in smiles_strategy_count:
                smiles_strategy_count[smiles] = smiles_strategy_count.get(smiles, 0) + 1
        
        # Score each molecule
        scored = []
        seen_smiles = set()
        
        for discovery in discoveries:
            smiles = discovery.get("smiles", "")
            if smiles in seen_smiles:
                continue
            seen_smiles.add(smiles)
            
            strategy_count = smiles_strategy_count.get(smiles, 1)
            scored_mol = self.score_molecule(discovery, strategy_count)
            
            if filter_safety_failures and not scored_mol.passes_safety_kpi:
                continue
            
            scored.append(scored_mol)
        
        # Sort by probability score (descending)
        scored.sort(key=lambda x: x.probability_score, reverse=True)
        
        return scored


def score_and_filter_discoveries(
    discoveries: List[Dict],
    seed_data: List[Dict],
    config: Optional[ScoringConfig] = None
) -> Tuple[List[ScoredMolecule], Dict]:
    """
    Convenience function to score and filter discoveries.
    
    Args:
        discoveries: Raw discoveries from traversal
        seed_data: Consolidated seed data (for priority mapping)
        config: Scoring configuration
        
    Returns:
        Tuple of (scored_molecules, statistics)
    """
    # Build seed priority map
    seed_priorities = {}
    for seed in seed_data:
        smiles = seed.get("smiles", "")
        priority = seed.get("priority_score", 1.0)
        seed_priorities[smiles] = priority
    
    scorer = ProbabilityScorer(config=config, seed_priorities=seed_priorities)
    
    scored = scorer.score_all(discoveries, filter_safety_failures=True)
    
    stats = {
        "total_scored": len(scored),
        "passed_safety": sum(1 for s in scored if s.passes_safety_kpi),
        "passed_cost": sum(1 for s in scored if s.passes_cost_kpi),
        "avg_probability": sum(s.probability_score for s in scored) / len(scored) if scored else 0
    }
    
    return scored, stats


if __name__ == "__main__":
    print("Probability Scoring module loaded.")
```

---

## Sub-Phase III.5: Phase III Orchestrator

### Complete Pipeline Integration

```python
# src/traversal/phase3_orchestrator.py
"""
Phase III: Deep Traversal & Expansion - Complete Orchestrator

Integrates all Phase III components:
1. Seed Consolidation (merge Engine A/B/C outputs)
2. Graph Enrichment (add traversal edges)
3. Graph Traversal (discover neighbors)
4. Probability Scoring & KPI Filtering
5. Output Generation (expanded candidate pool)

The "Oil Drilling" metaphor in action:
- Seeds = Strike points
- Graph edges = Underground veins
- Traversal = Following high-probability paths
- Scoring = Evaluating drilling success probability
- Output = Expanded, filtered candidate pool for Phase IV
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime

from src.traversal.seed_consolidation import (
    SeedConsolidator, 
    ConsolidationResult,
    SeedMolecule
)
from src.traversal.graph_enrichment import (
    GraphEnrichment,
    EnrichmentConfig
)
from src.traversal.traversal_strategies import (
    GraphTraverser,
    TraversalConfig,
    DiscoveredMolecule
)
from src.traversal.probability_scoring import (
    ProbabilityScorer,
    ScoringConfig,
    ScoredMolecule,
    score_and_filter_discoveries
)

@dataclass
class Phase3Result:
    """Complete output from Phase III"""
    # Seed information
    total_seeds: int
    triple_overlap_seeds: int
    
    # Traversal results
    total_discoveries: int
    discoveries_by_strategy: Dict[str, int]
    
    # Scored and filtered candidates
    expanded_candidates: List[Dict]  # Final candidate pool
    candidates_passing_safety: int
    candidates_passing_cost: int
    
    # Statistics
    expansion_ratio: float  # Candidates / Seeds
    avg_probability_score: float
    
    # Provenance
    timestamp: str
    config_used: Dict

class Phase3Orchestrator:
    """
    Orchestrates the complete Phase III pipeline.
    
    Input: Engine A/B/C results (75-150 seeds)
    Output: Expanded candidate pool (150-300 molecules)
    """
    
    def __init__(
        self,
        engine_a_path: Optional[Path] = None,
        engine_b_path: Optional[Path] = None,
        engine_c_path: Optional[Path] = None,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None
    ):
        """
        Args:
            engine_a_path: Path to Engine A results
            engine_b_path: Path to Engine B results
            engine_c_path: Path to Engine C results
            neo4j_*: Neo4j connection parameters
        """
        self.engine_a_path = engine_a_path or Path("data/engine_a_results.json")
        self.engine_b_path = engine_b_path or Path("data/engine_b_results.json")
        self.engine_c_path = engine_c_path or Path("data/engine_c_results.json")
        
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        # Will be populated during run
        self.consolidation_result: Optional[ConsolidationResult] = None
        self.enrichment_stats: Optional[Dict] = None
        self.discoveries: Optional[List[DiscoveredMolecule]] = None
        self.scored_candidates: Optional[List[ScoredMolecule]] = None
    
    def run_pipeline(
        self,
        target_expansion: int = 300,
        enrichment_config: Optional[EnrichmentConfig] = None,
        traversal_config: Optional[TraversalConfig] = None,
        scoring_config: Optional[ScoringConfig] = None
    ) -> Phase3Result:
        """
        Run the complete Phase III pipeline.
        
        Args:
            target_expansion: Target number of candidates (150-300)
            enrichment_config: Graph enrichment configuration
            traversal_config: Traversal configuration
            scoring_config: Scoring configuration
            
        Returns:
            Phase3Result with expanded candidate pool
        """
        print("=" * 70)
        print("PHASE III: DEEP TRAVERSAL & EXPANSION")
        print("=" * 70)
        print("\n'The Oil Drilling Phase'")
        print("Treating seeds as drill sites, following high-probability veins...\n")
        
        # =====================================================================
        # STEP 1: Seed Consolidation
        # =====================================================================
        print("-" * 70)
        print("STEP 1: SEED CONSOLIDATION")
        print("-" * 70)
        
        consolidator = SeedConsolidator(
            engine_a_path=self.engine_a_path,
            engine_b_path=self.engine_b_path,
            engine_c_path=self.engine_c_path
        )
        
        self.consolidation_result = consolidator.consolidate()
        
        print(f"\nConsolidation Results:")
        print(f"  Total seeds: {self.consolidation_result.statistics['total_seeds']}")
        print(f"  Triple overlap (highest priority): {self.consolidation_result.statistics['triple_overlap_count']}")
        print(f"  Double overlap: {self.consolidation_result.statistics['double_overlap_count']}")
        print(f"  Single source: {self.consolidation_result.statistics['single_source_count']}")
        
        if self.consolidation_result.triple_overlap:
            print(f"\n  ⭐ High-priority seeds (all 3 engines agree):")
            for smiles in self.consolidation_result.triple_overlap[:3]:
                seed = next(s for s in self.consolidation_result.all_seeds if s.smiles == smiles)
                print(f"    - {seed.name[:40] if seed.name else smiles[:40]}...")
        
        # =====================================================================
        # STEP 2: Graph Enrichment
        # =====================================================================
        print("\n" + "-" * 70)
        print("STEP 2: GRAPH ENRICHMENT")
        print("-" * 70)
        
        seeds_as_dicts = [s.to_dict() for s in self.consolidation_result.all_seeds]
        
        try:
            with GraphEnrichment(
                neo4j_uri=self.neo4j_uri,
                neo4j_user=self.neo4j_user,
                neo4j_password=self.neo4j_password,
                config=enrichment_config
            ) as enricher:
                self.enrichment_stats = enricher.run_full_enrichment(
                    seeds=seeds_as_dicts,
                    compute_all_similarities=False  # Focus on seeds
                )
        except Exception as e:
            print(f"\n⚠️  Graph enrichment error: {e}")
            print("   Continuing with existing graph structure...")
            self.enrichment_stats = {"error": str(e)}
        
        # =====================================================================
        # STEP 3: Graph Traversal
        # =====================================================================
        print("\n" + "-" * 70)
        print("STEP 3: GRAPH TRAVERSAL")
        print("-" * 70)
        
        seed_smiles = [s.smiles for s in self.consolidation_result.all_seeds]
        
        try:
            with GraphTraverser(
                neo4j_uri=self.neo4j_uri,
                neo4j_user=self.neo4j_user,
                neo4j_password=self.neo4j_password,
                config=traversal_config
            ) as traverser:
                self.discoveries, traversal_stats = traverser.run_full_traversal(seed_smiles)
        except Exception as e:
            print(f"\n⚠️  Traversal error: {e}")
            print("   Using seeds as candidates...")
            self.discoveries = []
            traversal_stats = {"total_discoveries": 0, "by_strategy": {}}
        
        # =====================================================================
        # STEP 4: Probability Scoring & KPI Filtering
        # =====================================================================
        print("\n" + "-" * 70)
        print("STEP 4: PROBABILITY SCORING & KPI FILTERING")
        print("-" * 70)
        
        # Convert discoveries to dicts for scoring
        discoveries_dicts = [d.to_dict() for d in self.discoveries] if self.discoveries else []
        
        # Also include seeds as candidates (they passed Phase II selection)
        for seed in self.consolidation_result.all_seeds:
            discoveries_dicts.append({
                "smiles": seed.smiles,
                "name": seed.name,
                "discovery_strategy": "seed",
                "discovery_path": f"Phase II Seed (engines: {seed.source_engines})",
                "seed_source": seed.smiles,
                "edge_score": 1.0,  # Seeds get high edge score
                "hop_distance": 0,
                "properties": seed.properties,
                "priority_score": seed.priority_score
            })
        
        self.scored_candidates, scoring_stats = score_and_filter_discoveries(
            discoveries=discoveries_dicts,
            seed_data=seeds_as_dicts,
            config=scoring_config
        )
        
        print(f"\nScoring Results:")
        print(f"  Total scored: {scoring_stats['total_scored']}")
        print(f"  Passed safety KPI: {scoring_stats['passed_safety']}")
        print(f"  Passed cost KPI: {scoring_stats['passed_cost']}")
        print(f"  Avg probability score: {scoring_stats['avg_probability']:.3f}")
        
        # Limit to target expansion
        final_candidates = self.scored_candidates[:target_expansion]
        
        print(f"\n  Final candidates (top {target_expansion}): {len(final_candidates)}")
        
        # =====================================================================
        # STEP 5: Compile Results
        # =====================================================================
        print("\n" + "-" * 70)
        print("STEP 5: COMPILE RESULTS")
        print("-" * 70)
        
        result = Phase3Result(
            total_seeds=self.consolidation_result.statistics['total_seeds'],
            triple_overlap_seeds=self.consolidation_result.statistics['triple_overlap_count'],
            total_discoveries=traversal_stats.get('total_discoveries', 0),
            discoveries_by_strategy=traversal_stats.get('by_strategy', {}),
            expanded_candidates=[c.to_dict() for c in final_candidates],
            candidates_passing_safety=sum(1 for c in final_candidates if c.passes_safety_kpi),
            candidates_passing_cost=sum(1 for c in final_candidates if c.passes_cost_kpi),
            expansion_ratio=len(final_candidates) / max(self.consolidation_result.statistics['total_seeds'], 1),
            avg_probability_score=scoring_stats['avg_probability'],
            timestamp=datetime.now().isoformat(),
            config_used={
                "enrichment": enrichment_config.__dict__ if enrichment_config else "default",
                "traversal": traversal_config.__dict__ if traversal_config else "default",
                "scoring": scoring_config.__dict__ if scoring_config else "default"
            }
        )
        
        print(f"\nPhase III Complete!")
        print(f"  Seeds: {result.total_seeds}")
        print(f"  Expansion ratio: {result.expansion_ratio:.2f}x")
        print(f"  Final candidates: {len(result.expanded_candidates)}")
        
        print("\n" + "=" * 70)
        print("PHASE III OUTPUT READY FOR PHASE IV (Bayesian Optimization)")
        print("=" * 70)
        
        return result
    
    def export_results(
        self,
        result: Phase3Result,
        output_path: Optional[Path] = None
    ) -> Path:
        """Export Phase III results to JSON."""
        if output_path is None:
            output_path = Path("data/phase3_results.json")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "phase": "III",
            "stage": "deep_traversal_expansion",
            "summary": {
                "total_seeds": result.total_seeds,
                "triple_overlap_seeds": result.triple_overlap_seeds,
                "total_discoveries": result.total_discoveries,
                "final_candidates": len(result.expanded_candidates),
                "expansion_ratio": result.expansion_ratio,
                "avg_probability_score": result.avg_probability_score
            },
            "candidates": result.expanded_candidates,
            "discoveries_by_strategy": result.discoveries_by_strategy,
            "kpi_summary": {
                "passing_safety": result.candidates_passing_safety,
                "passing_cost": result.candidates_passing_cost
            },
            "timestamp": result.timestamp,
            "config": result.config_used
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"\nResults exported to: {output_path}")
        return output_path


def run_phase3_pipeline(
    engine_a_path: Optional[Path] = None,
    engine_b_path: Optional[Path] = None,
    engine_c_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    target_expansion: int = 300
) -> Phase3Result:
    """
    Main entry point for Phase III.
    
    Args:
        engine_a_path: Path to Engine A results
        engine_b_path: Path to Engine B results
        engine_c_path: Path to Engine C results
        output_path: Where to save results
        target_expansion: Target number of candidates
        
    Returns:
        Phase3Result with expanded candidate pool
    """
    orchestrator = Phase3Orchestrator(
        engine_a_path=engine_a_path,
        engine_b_path=engine_b_path,
        engine_c_path=engine_c_path
    )
    
    result = orchestrator.run_pipeline(target_expansion=target_expansion)
    
    if output_path is None:
        output_path = Path("data/phase3_results.json")
    
    orchestrator.export_results(result, output_path)
    
    return result


if __name__ == "__main__":
    result = run_phase3_pipeline()
```

---

## Code Artifacts Summary

### Project Structure Addition

```
src/
├── traversal/
│   ├── __init__.py
│   ├── seed_consolidation.py      # Merge Engine A/B/C outputs
│   ├── graph_enrichment.py        # Add traversal edges to Neo4j
│   ├── traversal_strategies.py    # Multi-strategy graph traversal
│   ├── probability_scoring.py     # Score and filter discoveries
│   └── phase3_orchestrator.py     # Complete pipeline
```

### Notebooks to Create

| Notebook | Purpose |
|----------|---------|
| `23_seed_consolidation.ipynb` | Test engine output merging |
| `24_graph_enrichment.ipynb` | Visualize enriched graph in Neo4j |
| `25_traversal_exploration.ipynb` | Test individual traversal strategies |
| `26_scoring_analysis.ipynb` | Analyze probability scores and KPI filters |
| `27_phase3_integration.ipynb` | Full Phase III pipeline |

### Neo4j Schema Extensions

```cypher
// Additional constraints for Phase III
CREATE CONSTRAINT seed_smiles IF NOT EXISTS
FOR (s:Seed) REQUIRE s.smiles IS UNIQUE;

// New relationship types
// (Molecule)-[:SIMILAR_TO {tanimoto: float}]->(Molecule)
// (Molecule)-[:CO_MENTIONED {paper_count: int}]->(Molecule)
// (Molecule)-[:PROPERTY_SIMILAR {similarity: float}]->(Molecule)
// (Molecule)-[:USES_MECHANISM]->(Mechanism)

// Indexes for traversal performance
CREATE INDEX traversal_priority IF NOT EXISTS
FOR (m:Molecule) ON (m.priority_score);

CREATE INDEX traversal_seed IF NOT EXISTS
FOR (m:Molecule) ON (m.is_seed);
```

---

## Verification Notes

### Items Requiring User Verification

| Item | Action Required | Reference |
|------|-----------------|-----------|
| Neo4j connection | Ensure Neo4j is running and accessible | https://neo4j.com/download/ |
| Engine outputs exist | Run Phases II-A, II-B, II-C first | Previous phase documentation |
| RDKit installation | Required for similarity calculation | `pip install rdkit` |
| Safety data sources | GHS data not available in PubChem directly | May need ECHA integration `[NEEDS VERIFICATION]` |

### Sources Cited

| Claim | Source | Status |
|-------|--------|--------|
| Tanimoto similarity standard | RDKit documentation | High confidence |
| Neo4j Cypher patterns | Neo4j documentation | High confidence |
| GHS toxicity categories | ECHA/GHS classification | High confidence - categories accurate |
| Property ranges for entrainers | Perry's Handbook, general literature | Moderate - verify for specific cases |

### Accuracy Limitations

1. **Safety Data Availability**: The code assumes safety properties (GHS categories) are available in molecule properties. In practice, this data may need to be fetched from ECHA or other safety databases. The current implementation includes placeholder logic.

2. **Cost Estimation**: Real cost-effectiveness analysis requires commercial availability databases and pricing data. The current `_check_cost_kpi` method is a placeholder.

3. **Graph Quality**: The traversal quality depends heavily on the richness of the Neo4j graph (papers, citations, properties). If the graph is sparse, discoveries will be limited.

---

## GitHub Portfolio Framing

### README Section for Phase III

```markdown
## Phase III: Deep Traversal & Expansion 🔍

### The "Drilling" Phase

**Status:** In Development

This phase treats Phase II selections as "drill sites" and explores the 
molecular knowledge graph to discover additional candidates.

#### The Oil Exploration Metaphor
| Activity | Metaphor | Implementation |
|----------|----------|----------------|
| Seeds | Strike points | Engine A/B/C selections |
| Traversal | Following veins | Graph path exploration |
| Scoring | Probability estimation | Multi-factor scoring |
| Filtering | Avoiding dry holes | Safety/cost KPIs |

#### Traversal Strategies
| Strategy | Edge Type | Discovers |
|----------|-----------|-----------|
| Structural | SIMILAR_TO | Tanimoto-similar molecules |
| Literature | CO_MENTIONED | Co-cited compounds |
| Property | PROPERTY_SIMILAR | Functional analogs |
| Mechanism | USES_MECHANISM | Same separation mechanism |

#### Key Metrics
| Metric | Value |
|--------|-------|
| Input seeds | 75-150 |
| Expansion target | 150-300 |
| Expansion ratio | ~2x |
| Safety pass rate | XX% |

### Reproducibility
```bash
# Requires Neo4j running
export NEO4J_URI=bolt://localhost:7687
export NEO4J_PASSWORD=your_password

# Run Phase III
python -m src.traversal.phase3_orchestrator
```
```

### Suggested Badges

```markdown
![Neo4j](https://img.shields.io/badge/Database-Neo4j-blue)
![Phase](https://img.shields.io/badge/Phase-III%20Traversal-orange)
![Expansion](https://img.shields.io/badge/Expansion-2x-green)
```

---

## Confidence Assessment

### High Confidence
- Seed consolidation logic
- Neo4j Cypher query patterns
- Tanimoto similarity calculation
- Multi-strategy traversal design
- Probability scoring framework

### Needs Verification
- **GHS safety data retrieval** - May need external API integration
- **Cost estimation** - Placeholder implementation
- **Optimal traversal thresholds** - May need tuning based on actual data
- **Neo4j performance** - Large graphs may need query optimization

### Outside My Expertise
- Specific industrial cost benchmarks for entrainers
- Regulatory compliance requirements for specific jurisdictions
- Optimal graph density for effective traversal

---

## Integration with Phase IV

Phase III outputs feed directly into Phase IV (Bayesian Optimization):

```python
# Phase IV will receive:
phase3_results = {
    "expanded_candidates": [
        {
            "smiles": "...",
            "probability_score": 0.85,
            "properties": {...},
            "passes_safety_kpi": True,
            # Ready for MOBO objective functions
        },
        ...
    ],
    "total_candidates": 300,  # Target for optimization
}

# Phase IV will:
# 1. Calculate thermodynamic properties (UNIFAC)
# 2. Apply safety penalty function
# 3. Run Multi-Objective Bayesian Optimization
# 4. Identify Pareto frontier
```