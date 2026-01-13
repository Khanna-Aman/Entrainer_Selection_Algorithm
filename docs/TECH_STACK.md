# Technology Stack

> Complete technology stack and dependencies for the Safety-by-Design Entrainer Selection Framework

## 📋 Table of Contents

- [Core Technologies](#core-technologies)
- [Phase-Specific Dependencies](#phase-specific-dependencies)
- [Infrastructure](#infrastructure)
- [Development Tools](#development-tools)
- [Version Requirements](#version-requirements)

---

## Core Technologies

### Python Environment

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Core runtime |
| pip | Latest | Package management |
| venv | Built-in | Virtual environment |

### Data Science Stack

| Library | Version | Purpose |
|---------|---------|---------|
| NumPy | ≥1.24 | Numerical computing |
| Pandas | ≥2.0 | Data manipulation |
| SciPy | ≥1.11 | Scientific computing |
| Matplotlib | ≥3.7 | Visualization |
| Seaborn | ≥0.12 | Statistical visualization |

---

## Phase-Specific Dependencies

### Phase I: Domain Mapping

| Library | Purpose |
|---------|---------|
| `pubchempy` | PubChem API access |
| `rdkit` | Molecular fingerprints & clustering |
| `scikit-learn` | K-means clustering |
| `hdbscan` | Density-based clustering |

### Phase II: Multi-Vector Selection

#### Engine A: Graph-RAG

| Library | Purpose |
|---------|---------|
| `google-generativeai` | Gemini API integration |
| `neo4j` | Graph database driver |
| `chromadb` | Vector embeddings storage |
| `langchain` | RAG orchestration |

#### Engine B: TRIZ Multi-Agent

| Library | Purpose |
|---------|---------|
| `google-generativeai` | Gemini API for agents |
| `pydantic` | Data validation |
| `asyncio` | Async agent coordination |

#### Engine C: Cheminformatics

| Library | Purpose |
|---------|---------|
| `rdkit` | Molecular descriptors |
| `mordred` | Extended descriptors |
| `scikit-learn` | Diversity selection |

### Phase III: Graph Traversal

| Library | Purpose |
|---------|---------|
| `neo4j` | Graph database operations |
| `networkx` | Graph algorithms |
| `rdkit` | Tanimoto similarity |

### Phase IV: Bayesian Optimization

| Library | Version | Purpose |
|---------|---------|---------|
| `botorch` | ≥0.9 | Multi-objective BO |
| `gpytorch` | ≥1.11 | Gaussian processes |
| `torch` | ≥2.0 | Deep learning backend |

### Phase V: Process Simulation

| Component | Purpose |
|-----------|---------|
| `pythoncom` | COM automation (Windows) |
| `win32com` | DWSIM interface |
| `thermo` | UNIFAC calculations |

---

## Infrastructure

### Databases

| Database | Version | Purpose |
|----------|---------|---------|
| Neo4j Community | 5.x | Graph storage for molecular relationships |
| ChromaDB | Latest | Vector embeddings for RAG |
| SQLite | Built-in | Local caching and results storage |

### External APIs

| API | Purpose | Rate Limits |
|-----|---------|-------------|
| PubChem PUG REST | Chemical data retrieval | 5 req/sec |
| Google Gemini | LLM for Graph-RAG & TRIZ | Varies by tier |
| ChemSpider | Supplementary chemical data | API key required |

### Process Simulation

| Software | Version | Platform |
|----------|---------|----------|
| DWSIM | 8.x | Windows (COM automation) |

---

## Development Tools

### Code Quality

| Tool | Purpose |
|------|---------|
| `black` | Code formatting |
| `isort` | Import sorting |
| `flake8` | Linting |
| `mypy` | Type checking |
| `pre-commit` | Git hooks |

### Testing

| Tool | Purpose |
|------|---------|
| `pytest` | Test framework |
| `pytest-cov` | Coverage reporting |
| `pytest-asyncio` | Async test support |
| `hypothesis` | Property-based testing |

### Documentation

| Tool | Purpose |
|------|---------|
| `mkdocs` | Documentation site |
| `mkdocs-material` | Theme |
| `mkdocstrings` | API documentation |

---

## Version Requirements

### Minimum Requirements

```
Python >= 3.11
Neo4j >= 5.0
DWSIM >= 8.0 (Windows only)
```

### Recommended Versions

```
Python 3.11.x (tested)
Neo4j 5.15.0
DWSIM 8.6.8
```

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| Storage | 10 GB | 50 GB |
| GPU | Not required | CUDA-capable (for BoTorch) |

---

## Installation Notes

### RDKit Installation

RDKit requires conda or a pre-built wheel:

```bash
# Option 1: Conda (recommended)
conda install -c conda-forge rdkit

# Option 2: pip (if available for your platform)
pip install rdkit
```

### Neo4j Setup

```bash
# Using Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5-community
```

### DWSIM Setup (Windows)

1. Download DWSIM from [dwsim.org](https://dwsim.org)
2. Install with COM automation support enabled
3. Register COM objects (usually automatic)

---

## Dependency Graph

```
entrainer-selection
├── Core
│   ├── numpy, pandas, scipy
│   └── pydantic, pyyaml
├── Cheminformatics
│   ├── rdkit
│   ├── pubchempy
│   └── mordred
├── Machine Learning
│   ├── torch
│   ├── botorch
│   └── gpytorch
├── Graph/RAG
│   ├── neo4j
│   ├── chromadb
│   └── langchain
├── LLM
│   └── google-generativeai
└── Simulation
    ├── thermo
    └── pywin32 (Windows)
```

