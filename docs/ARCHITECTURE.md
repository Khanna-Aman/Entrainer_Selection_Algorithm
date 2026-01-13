# System Architecture

> Detailed architecture documentation for the Safety-by-Design Entrainer Selection Framework

## 📋 Table of Contents

- [High-Level Overview](#high-level-overview)
- [Data Flow](#data-flow)
- [Module Architecture](#module-architecture)
- [Integration Points](#integration-points)
- [Design Principles](#design-principles)

---

## High-Level Overview

The framework implements a **five-phase pipeline** with clear boundaries between phases. Each phase produces artifacts consumed by subsequent phases.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │   Phase I    │───▶│   Phase II   │───▶│  Phase III   │                  │
│   │Domain Mapping│    │Multi-Vector  │    │Graph Traversal│                 │
│   │  100K → 500  │    │  Selection   │    │  150 → 300   │                  │
│   └──────────────┘    └──────────────┘    └──────────────┘                  │
│          │                   │                   │                          │
│          ▼                   ▼                   ▼                          │
│   ┌──────────────────────────────────────────────────────┐                  │
│   │                    Neo4j Graph DB                     │                  │
│   │         (Molecular Relationships & Metadata)          │                  │
│   └──────────────────────────────────────────────────────┘                  │
│          │                   │                   │                          │
│          ▼                   ▼                   ▼                          │
│   ┌──────────────┐    ┌──────────────┐                                      │
│   │   Phase IV   │───▶│   Phase V    │                                      │
│   │    MOBO      │    │  Simulation  │                                      │
│   │Active Learning│   │  Validation  │                                      │
│   └──────────────┘    └──────────────┘                                      │
│                              │                                              │
│                              ▼                                              │
│                    ┌──────────────────┐                                     │
│                    │  Pareto Library  │                                     │
│                    │   (Top 10-20)    │                                     │
│                    └──────────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Phase Transitions

| Transition | Input | Output | Format |
|------------|-------|--------|--------|
| I → II | 100K+ molecules | 500 cluster centroids | CSV + Neo4j |
| II → III | 75-150 candidates | Scored candidates | JSON + Neo4j |
| III → IV | 150-300 expanded set | Similarity graph | Neo4j edges |
| IV → V | Pareto candidates | Optimized set | CSV + metadata |
| V → Output | Simulated results | Final rankings | JSON + reports |

### Data Artifacts

```
data/
├── raw/
│   ├── pubchem_queries/          # API responses
│   └── literature_extracts/      # Parsed papers
├── processed/
│   ├── phase1_clusters.parquet   # Cluster definitions
│   ├── phase2_candidates.json    # Engine outputs
│   ├── phase3_expanded.json      # Graph traversal results
│   └── phase4_pareto.json        # MOBO results
└── results/
    ├── pareto_library.json       # Final Pareto set
    ├── simulation_results/       # DWSIM outputs
    └── reports/                  # Generated reports
```

---

## Module Architecture

### Core Module (`src/core/`)

Shared infrastructure used across all phases:

```
src/core/
├── __init__.py
├── config.py           # Configuration management
├── logging_config.py   # Structured logging
├── models/
│   ├── molecule.py     # Molecule data class
│   ├── candidate.py    # Candidate with scores
│   └── pareto.py       # Pareto point representation
├── database/
│   ├── neo4j_client.py # Graph database interface
│   └── chroma_client.py# Vector store interface
└── utils/
    ├── chemistry.py    # RDKit utilities
    └── validation.py   # Data validation
```

### Phase Modules

Each phase follows a consistent structure:

```
src/phase{N}/
├── __init__.py
├── main.py             # Entry point
├── pipeline.py         # Orchestration logic
├── services/           # Business logic
├── models/             # Phase-specific models
└── tests/              # Unit tests
```

---

## Integration Points

### External APIs

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    PubChem      │     │  Google Gemini  │     │    ChemSpider   │
│   PUG REST      │     │      API        │     │      API        │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  (Rate limiting, caching, retry logic, error handling)          │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Phase I      │     │    Phase II     │     │    Phase I      │
│  Data Retrieval │     │   Engine A/B    │     │  Supplementary  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Database Connections

| Database | Connection | Purpose |
|----------|------------|---------|
| Neo4j | Bolt protocol (7687) | Graph queries, traversal |
| ChromaDB | HTTP/gRPC | Vector similarity search |
| SQLite | File-based | Local caching, results |

---

## Design Principles

### 1. Phase Independence

Each phase can be run independently with appropriate input files:

```bash
# Run Phase II with pre-computed Phase I results
python -m src.phase2.main --input data/processed/phase1_clusters.parquet
```

### 2. Configuration-Driven

All parameters externalized to YAML:

```yaml
# science_config.yaml
phase4:
  mobo:
    n_initial_samples: 20
    n_iterations: 50
    acquisition_function: "qEHVI"
```

### 3. Reproducibility

- All random seeds configurable
- Full logging of parameters
- Artifact versioning with timestamps

### 4. Extensibility

New engines or phases can be added by implementing interfaces:

```python
class SelectionEngine(Protocol):
    def select(self, candidates: list[Molecule]) -> list[Candidate]:
        ...
```

---

## Concurrency Model

### Phase II: Parallel Engine Execution

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase II Orchestrator                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│   │  Engine A   │   │  Engine B   │   │  Engine C   │          │
│   │  (async)    │   │  (async)    │   │  (async)    │          │
│   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘          │
│          │                 │                 │                  │
│          └────────────────┬┴─────────────────┘                  │
│                           ▼                                     │
│                  ┌─────────────────┐                            │
│                  │    Consensus    │                            │
│                  │    Aggregator   │                            │
│                  └─────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### Phase IV: Sequential Active Learning

MOBO runs sequentially due to Gaussian Process fitting requirements.

---

## Error Handling Strategy

| Error Type | Strategy | Recovery |
|------------|----------|----------|
| API Rate Limit | Exponential backoff | Auto-retry |
| API Failure | Circuit breaker | Fallback to cache |
| Invalid Molecule | Log and skip | Continue pipeline |
| Database Error | Retry with reconnect | Fail after 3 attempts |
| Simulation Crash | Isolate and log | Mark as failed |

---

## Monitoring & Observability

### Logging Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed computation steps |
| INFO | Phase progress, key metrics |
| WARNING | Recoverable issues |
| ERROR | Failures requiring attention |

### Metrics Collected

- Molecules processed per phase
- API call counts and latencies
- Pareto hypervolume progression
- Simulation success rates

