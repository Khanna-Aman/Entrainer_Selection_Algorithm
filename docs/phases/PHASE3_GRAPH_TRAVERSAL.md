# Phase III: Graph-Based Molecular Expansion

> Expand candidate set through similarity-based graph traversal to discover structurally related molecules

## 🎯 Objective

Expand the 75-150 candidates from Phase II to 150-300 molecules by traversing the molecular similarity graph, discovering structurally related compounds that may offer improved safety-efficiency trade-offs.

---

## 📊 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHASE III PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Input: 75-150 Candidates from Phase II                                │
│                           │                                              │
│                           ▼                                              │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Neo4j Similarity Graph                        │   │
│   │                                                                  │   │
│   │    (Seed)──0.85──(Neighbor1)──0.78──(Neighbor2)                 │   │
│   │       │                                                          │   │
│   │       └──0.82──(Neighbor3)──0.75──(Neighbor4)                   │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                           │                                              │
│           ┌───────────────┼───────────────┐                             │
│           ▼               ▼               ▼                             │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                       │
│   │   1-Hop     │ │   2-Hop     │ │  Property   │                       │
│   │  Neighbors  │ │  Neighbors  │ │  Filtering  │                       │
│   │  (τ≥0.80)   │ │  (τ≥0.75)   │ │             │                       │
│   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘                       │
│          │               │               │                              │
│          └───────────────┼───────────────┘                              │
│                          ▼                                              │
│   Output: 150-300 Expanded Candidates with Similarity Scores            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Graph Construction

### Similarity Metric

**Tanimoto Coefficient** on Morgan Fingerprints (ECFP4):

```python
def tanimoto_similarity(fp1: BitVector, fp2: BitVector) -> float:
    """Calculate Tanimoto similarity between two fingerprints."""
    intersection = (fp1 & fp2).GetNumOnBits()
    union = (fp1 | fp2).GetNumOnBits()
    return intersection / union if union > 0 else 0.0
```

### Graph Schema

```cypher
// Node: Molecule
CREATE (m:Molecule {
    cid: INTEGER,
    smiles: STRING,
    name: STRING,
    fingerprint: LIST<INTEGER>,
    phase2_score: FLOAT,
    is_seed: BOOLEAN
})

// Edge: Similarity relationship
CREATE (m1)-[:SIMILAR_TO {
    tanimoto: FLOAT,
    hop_distance: INTEGER
}]->(m2)
```

### Edge Creation Criteria

| Hop Level | Tanimoto Threshold | Max Neighbors |
|-----------|-------------------|---------------|
| 1-hop | ≥ 0.80 | 10 per seed |
| 2-hop | ≥ 0.75 | 5 per 1-hop |

---

## 🔄 Traversal Algorithm

### Breadth-First Expansion

```python
def expand_candidates(seeds: list[Molecule], graph: Neo4jGraph) -> list[Molecule]:
    """Expand seed candidates through graph traversal."""
    expanded = set(seeds)
    
    # 1-hop expansion
    for seed in seeds:
        neighbors_1hop = graph.query("""
            MATCH (s:Molecule {cid: $cid})-[r:SIMILAR_TO]->(n:Molecule)
            WHERE r.tanimoto >= 0.80
            RETURN n ORDER BY r.tanimoto DESC LIMIT 10
        """, cid=seed.cid)
        expanded.update(neighbors_1hop)
    
    # 2-hop expansion (from 1-hop neighbors only)
    for mol in list(expanded - set(seeds)):
        neighbors_2hop = graph.query("""
            MATCH (s:Molecule {cid: $cid})-[r:SIMILAR_TO]->(n:Molecule)
            WHERE r.tanimoto >= 0.75 AND NOT n.is_seed
            RETURN n ORDER BY r.tanimoto DESC LIMIT 5
        """, cid=mol.cid)
        expanded.update(neighbors_2hop)
    
    return list(expanded)
```

### Property-Based Filtering

After expansion, apply thermodynamic filters:

```python
EXPANSION_FILTERS = {
    "boiling_point_k": (351, 500),      # Must be separable
    "molecular_weight": (50, 350),       # Reasonable size
    "vapor_pressure_kpa": (0.001, 10),   # Low volatility
}
```

---

## 📊 Scoring Propagation

### Inherited Score Calculation

```python
def calculate_inherited_score(
    neighbor: Molecule,
    seed: Molecule,
    similarity: float
) -> float:
    """Propagate score from seed with similarity decay."""
    decay_factor = 0.9  # Per hop
    return seed.phase2_score * similarity * decay_factor
```

### Multi-Seed Aggregation

When a molecule is reachable from multiple seeds:

```python
def aggregate_scores(scores: list[float]) -> float:
    """Aggregate scores from multiple paths."""
    # Use maximum score (optimistic)
    return max(scores)
```

---

## 🔧 Neo4j Queries

### Build Similarity Graph

```cypher
// Create similarity edges between all molecules
CALL apoc.periodic.iterate(
    "MATCH (m1:Molecule), (m2:Molecule) 
     WHERE id(m1) < id(m2) RETURN m1, m2",
    "WITH m1, m2, 
     gds.similarity.jaccard(m1.fingerprint, m2.fingerprint) AS sim
     WHERE sim >= 0.75
     CREATE (m1)-[:SIMILAR_TO {tanimoto: sim}]->(m2)",
    {batchSize: 1000}
)
```

### Find Expansion Candidates

```cypher
// Get all molecules within 2 hops of seeds
MATCH path = (seed:Molecule {is_seed: true})-[:SIMILAR_TO*1..2]-(neighbor:Molecule)
WHERE ALL(r IN relationships(path) WHERE r.tanimoto >= 0.75)
WITH neighbor, 
     MIN(length(path)) AS hop_distance,
     MAX([r IN relationships(path) | r.tanimoto]) AS max_similarity
RETURN DISTINCT neighbor, hop_distance, max_similarity
ORDER BY max_similarity DESC
```

---

## 📁 Output Artifacts

| File | Format | Description |
|------|--------|-------------|
| `phase3_expanded.json` | JSON | Expanded candidate list |
| `phase3_graph_stats.json` | JSON | Graph statistics |
| `phase3_paths.csv` | CSV | Seed-to-neighbor paths |

---

## 🔧 Configuration

```yaml
# science_config.yaml
phase3:
  similarity:
    fingerprint_type: "morgan"
    fingerprint_radius: 2
    fingerprint_bits: 2048
  traversal:
    hop1_threshold: 0.80
    hop2_threshold: 0.75
    max_hop1_neighbors: 10
    max_hop2_neighbors: 5
  filtering:
    apply_property_filters: true
    max_expansion_factor: 3.0
```

---

## 📈 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Expansion ratio | 1.5x - 2.5x | Count comparison |
| Similarity preservation | Mean τ ≥ 0.78 | Edge statistics |
| Property compliance | 100% | Filter validation |
| Graph connectivity | ≥ 80% in main component | Graph analysis |

