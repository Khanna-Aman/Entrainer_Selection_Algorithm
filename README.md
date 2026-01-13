
# 🧪 Safety-by-Design Framework for Ethanol-Water Separation Entrainer Selection

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **An Active Learning Framework for Simultaneous Optimization of Thermodynamic Efficiency and Inherent Safety in Extractive Distillation Entrainers**

## 🎯 Project Overview

This research framework implements a **"Safety-by-Design"** approach to entrainer selection for ethanol-water separation. Unlike traditional methods that optimize efficiency first and apply safety as a retroactive constraint, this framework treats **safety and efficiency as simultaneous objectives** within a Multi-Objective Bayesian Optimization (MOBO) loop.

### The Problem

In industrial ethanol-water separation via extractive distillation:
- Traditional approach: Maximize efficiency first → Apply safety constraints later
- Result: Selection of hazardous solvents (e.g., benzene - a known carcinogen)
- Consequence: Expensive containment and mitigation strategies

### Our Solution

A five-phase computational pipeline that:
1. **Maps the chemical space** to identify promising molecular "hot spots"
2. **Selects candidates** using three parallel AI/algorithmic engines
3. **Expands the search** via graph-based molecular similarity traversal
4. **Optimizes simultaneously** for safety and efficiency using MOBO + qEHVI
5. **Validates rigorously** through process simulation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ENTRAINER SELECTION FRAMEWORK                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Phase I: Domain Mapping          Phase II: Multi-Vector Selection       │
│  ┌─────────────────────┐         ┌─────────────────────────────────┐    │
│  │ Literature Survey   │         │  Engine A    Engine B   Engine C │    │
│  │ Database Scoping    │────────▶│  Graph-RAG   TRIZ      RDKit     │    │
│  │ Cluster Definition  │         │  (AI)       (Heuristic)(Algorithmic)│ │
│  │ 100K+ → 500 clusters│         │     └────────┬─────────┘         │    │
│  └─────────────────────┘         └──────────────┼───────────────────┘    │
│                                                 │                        │
│                                                 ▼                        │
│  Phase III: Deep Traversal       Phase IV: Bayesian Optimization        │
│  ┌─────────────────────┐         ┌─────────────────────────────────┐    │
│  │ Neo4j Graph DB      │         │  Gaussian Process Surrogate     │    │
│  │ Similarity Expansion│────────▶│  qEHVI Acquisition Function     │    │
│  │ 75-150 → 150-300    │         │  Pareto Frontier Identification │    │
│  └─────────────────────┘         └──────────────┬───────────────────┘    │
│                                                 │                        │
│                                                 ▼                        │
│                           Phase V: Simulation & Validation               │
│                           ┌─────────────────────────────────┐           │
│                           │  DWSIM Process Simulation        │           │
│                           │  Final Top 10 Ranking            │           │
│                           │  Pareto-Optimal Library Output   │           │
│                           └─────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🔬 Research Hypotheses

| ID | Hypothesis | Validation Phase | Success Metric |
|----|------------|------------------|----------------|
| H1 | Pareto frontier exhibits convex structure with identifiable knee points | Phase IV | ≥1 knee point identified |
| H2 | qEHVI achieves equivalent hypervolume with ≤30% computational budget | Phase IV | HV_30% ≥ 0.95 × HV_100% |
| H3 | Consensus safety scoring reduces uncertainty by ≥25% | Phase II | σ_reduction ≥ 25% |

## 📁 Project Structure

```
entrainer-selection/
├── src/
│   ├── core/              # Shared infrastructure (config, logging, models)
│   ├── phase1/            # Domain Mapping & Cluster Definition
│   ├── phase2/
│   │   ├── engine_a/      # Graph-RAG with Gemini
│   │   ├── engine_b/      # TRIZ Multi-Agent System
│   │   └── engine_c/      # Cheminformatics & Diversity
│   ├── phase3/            # Graph Traversal & Expansion
│   ├── phase4/            # MOBO & Active Learning
│   └── phase5/            # DWSIM Simulation & Validation
├── config/
│   ├── infra_config.yaml  # Database, API, logging settings
│   └── science_config.yaml # SMARTS patterns, thresholds, thermodynamics
├── data/
│   ├── raw/               # API query results
│   ├── processed/         # Cleaned datasets
│   └── results/           # Output from each phase
├── notebooks/             # Jupyter notebooks for exploration
├── tests/                 # Unit and integration tests
├── docs/                  # Extended documentation
│   └── phases/            # Detailed phase documentation
├── backlog/               # Development task tracking
└── scripts/               # Utility scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Neo4j Community Edition (for Graph-RAG)
- DWSIM (for Phase V simulation - Windows only)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/entrainer-selection.git
cd entrainer-selection

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set up configuration
cp config/infra_config.example.yaml config/infra_config.yaml
# Edit config files with your API keys and database credentials
```

### Environment Variables

```bash
# Required API Keys
export GOOGLE_API_KEY="your-gemini-api-key"
export PUBCHEM_API_KEY="optional-for-higher-rate-limits"

# Database Configuration
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"
```

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [TECH_STACK.md](docs/TECH_STACK.md) | Complete technology stack and dependencies |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and data flow |
| [Phase Documentation](docs/phases/) | Detailed documentation for each phase |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [API Reference](docs/api/) | Module and function documentation |

## 🧬 Key Technologies

| Category | Technologies |
|----------|--------------|
| **Core Language** | Python 3.11+ |
| **Cheminformatics** | RDKit, PubChemPy |
| **Machine Learning** | BoTorch, GPyTorch, PyTorch |
| **Graph Database** | Neo4j + ChromaDB |
| **LLM Integration** | Google Gemini API |
| **Process Simulation** | DWSIM (COM automation) |
| **Thermodynamics** | thermo (UNIFAC) |

## 📊 Expected Outcomes

1. **Pareto-Optimal Library**: High-dimensional dataset identifying "Knee Points" - optimal safety/efficiency trade-offs
2. **Quantifiable Metrics**: 20% reduction in inherent risk with <8% efficiency penalty
3. **Reproducible Workflow**: Dockerized pipeline adaptable to other separation problems
4. **Benchmark Comparison**: Validated against ethylene glycol (industry standard) and benzene (historical negative control)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 📚 References

- Altshuller, G. (1999). *The Innovation Algorithm: TRIZ*
- Laroche, L. et al. (1991). "Homogeneous Azeotropic Distillation" [DOI: 10.1021/ie00020a013]
- Perry's Chemical Engineers' Handbook, 9th Edition
- BoTorch Multi-Objective Optimization: [botorch.org](https://botorch.org/)

## 📧 Contact

For questions or collaboration inquiries, please open an issue or contact the maintainers.

---

**Status**: 🚧 Active Development | **Current Phase**: Infrastructure Setup
=======
>>>>>>> bc927b64ce62b9bc50578b925227a072729c5808

