# Phase II: Multi-Vector Candidate Selection

> Three parallel AI/algorithmic engines for diverse candidate identification with consensus scoring

## 🎯 Objective

Select 75-150 high-potential entrainer candidates from 500 cluster centroids using three complementary approaches, then aggregate results with consensus scoring to reduce uncertainty.

---

## 📊 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHASE II PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Input: 500 Cluster Centroids from Phase I                             │
│                           │                                              │
│           ┌───────────────┼───────────────┐                             │
│           ▼               ▼               ▼                             │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                       │
│   │  Engine A   │ │  Engine B   │ │  Engine C   │                       │
│   │  Graph-RAG  │ │    TRIZ     │ │Cheminformatics│                     │
│   │  (Gemini)   │ │Multi-Agent  │ │  (RDKit)    │                       │
│   │             │ │  (Gemini)   │ │             │                       │
│   │  ~50 picks  │ │  ~50 picks  │ │  ~50 picks  │                       │
│   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘                       │
│          │               │               │                              │
│          └───────────────┼───────────────┘                              │
│                          ▼                                              │
│              ┌─────────────────────┐                                    │
│              │ Consensus Aggregator │                                    │
│              │  - Rank fusion       │                                    │
│              │  - Uncertainty calc  │                                    │
│              │  - Deduplication     │                                    │
│              └──────────┬──────────┘                                    │
│                         ▼                                               │
│   Output: 75-150 Candidates with Consensus Scores & Uncertainty         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Engine A: Graph-RAG with Gemini

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      GRAPH-RAG ENGINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │   Neo4j     │    │  ChromaDB   │    │   Gemini    │        │
│   │  Knowledge  │───▶│   Vector    │───▶│    LLM      │        │
│   │   Graph     │    │   Store     │    │  Reasoning  │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                  │
│   Query: "Find molecules similar to ethylene glycol with        │
│           lower toxicity and comparable selectivity"            │
└─────────────────────────────────────────────────────────────────┘
```

### Knowledge Graph Schema

```cypher
(:Molecule {cid, smiles, name})
(:Property {name, value, unit})
(:FunctionalGroup {smarts, name})
(:SafetyClass {ghs_category, description})

(:Molecule)-[:HAS_PROPERTY]->(:Property)
(:Molecule)-[:CONTAINS]->(:FunctionalGroup)
(:Molecule)-[:CLASSIFIED_AS]->(:SafetyClass)
(:Molecule)-[:SIMILAR_TO {tanimoto: float}]->(:Molecule)
```

### Selection Criteria

- Structural similarity to known entrainers
- Safety profile improvement potential
- Thermodynamic property alignment

---

## 🔬 Engine B: TRIZ Multi-Agent System

### Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRIZ MULTI-AGENT SYSTEM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │Contradiction│    │ Inventive   │    │  Solution   │        │
│   │  Analyst    │───▶│ Principles  │───▶│  Generator  │        │
│   │   Agent     │    │   Agent     │    │   Agent     │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                  │
│   Contradiction: "High selectivity" vs "Low toxicity"           │
│   Principles: #35 (Parameter changes), #28 (Mechanics sub.)     │
└─────────────────────────────────────────────────────────────────┘
```

### TRIZ Contradiction Matrix

| Improving Parameter | Worsening Parameter | Suggested Principles |
|---------------------|---------------------|----------------------|
| Selectivity | Toxicity | 35, 28, 31, 40 |
| Efficiency | Flammability | 15, 28, 35, 1 |
| Stability | Cost | 35, 10, 28, 29 |

### Agent Prompts

Each agent receives structured prompts with:
- Current contradiction definition
- Candidate molecule properties
- TRIZ principle descriptions
- Scoring rubric

---

## 🔬 Engine C: Cheminformatics & Diversity

### Algorithm

```python
def select_diverse_candidates(centroids, n_select=50):
    # 1. Compute extended descriptors
    descriptors = compute_mordred_descriptors(centroids)
    
    # 2. Apply MaxMin diversity selection
    selected = maxmin_picker(
        descriptors,
        n_select=n_select,
        seed_molecules=known_entrainers
    )
    
    # 3. Score by property alignment
    scores = score_thermodynamic_alignment(selected)
    
    return selected, scores
```

### Diversity Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| Tanimoto diversity | ≥ 0.7 | Structural variety |
| Property coverage | ≥ 80% | Parameter space |
| Functional group variety | ≥ 10 types | Chemical diversity |

---

## 🔄 Consensus Aggregation

### Rank Fusion Algorithm

```python
def consensus_score(engine_ranks: dict[str, int]) -> float:
    """Reciprocal Rank Fusion with engine weights."""
    weights = {"engine_a": 0.35, "engine_b": 0.30, "engine_c": 0.35}
    k = 60  # Smoothing constant
    
    score = sum(
        weights[engine] / (k + rank)
        for engine, rank in engine_ranks.items()
    )
    return score
```

### Uncertainty Quantification

```python
def calculate_uncertainty(engine_scores: list[float]) -> float:
    """Lower uncertainty when engines agree."""
    return np.std(engine_scores) / np.mean(engine_scores)
```

**Hypothesis H3**: Consensus scoring reduces uncertainty by ≥25% compared to single-engine selection.

---

## 📁 Output Artifacts

| File | Format | Description |
|------|--------|-------------|
| `engine_a_results.json` | JSON | Graph-RAG selections with reasoning |
| `engine_b_results.json` | JSON | TRIZ agent selections with principles |
| `engine_c_results.json` | JSON | Diversity selections with scores |
| `phase2_consensus.json` | JSON | Aggregated results with uncertainty |

---

## 🔧 Configuration

```yaml
# science_config.yaml
phase2:
  engine_a:
    model: "gemini-2.0-flash"
    temperature: 0.3
    max_candidates: 50
  engine_b:
    n_agents: 3
    triz_principles: [1, 10, 15, 28, 31, 35, 40]
  engine_c:
    diversity_threshold: 0.7
    descriptor_set: "mordred_2d"
  consensus:
    fusion_k: 60
    min_engines_agreement: 2
```

---

## 📈 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Candidate count | 75-150 | Pipeline output |
| Engine overlap | 20-40% | Diversity check |
| Uncertainty reduction | ≥25% | H3 validation |
| Known entrainer recall | ≥80% | Benchmark test |

